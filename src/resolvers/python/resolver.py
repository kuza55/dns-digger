#!/usr/bin/env python
__author__ = "Kevin Warrick"
__credits__ = ["Roberto Perdisci", "Kang Li"]
__email__ = "kwarrick@uga.edu"

import sys
import pika
import json
import time
import traceback
import dns.resolver
import dns.exception

from log import logger

class Resolver(object):
  """
  Resolvers are consumers reacting to Dispatchers messages;
  querying domains and sending the DNS response back to the 
  RabbitMQ server.

  """
  def __init__(self, host='localhost', port=5672, user=None, password=None, verbose=False):   
    self.host = host
    self.port = int(port)
    self.user = user
    self.password = password
    self.verbose = verbose

    # set local open recursives
    resolver = dns.resolver.get_default_resolver()
    self.resolvers = resolver.nameservers
    
    self.connection, self.channel = self.connect()

  def connect(self):
    # connect to rabbitmq
    creds = pika.PlainCredentials(self.user, self.password)
    params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=creds)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    return connection, channel

  def query_domain(self, domain, server, type):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.timeout = 1.0
    resolver.nameservers = list(set(self.resolvers + [server])) 

    return resolver.query(domain, type, raise_on_nx=False, raise_on_no_answer=False)
        
  def message_handler(self, channel, method, properties, body):
    if self.verbose:
      logger.info("received %r" % (body,))
    
    query = json.loads(body)
    for host in query['resolvers']:
      message = {'domain' : query['domain'], 'resolver' : host, 'time' : time.time() }
    
      try:
        answer = self.query_domain(query['domain'], host, query['type'])
        message['response'] = answer.response.to_wire().encode('base64')
      except dns.exception.DNSException as e:
        # error = traceback.format_exception_only(type(e), e)[0].strip()
        # logger.info("%s %s - %s " % (query['domain'], host, error))
        message['error'] = type(e).__name__
    
      # send response to reducer
      data = json.dumps(message)
      self.channel.basic_publish(exchange='dns', routing_key='response', body=data, 
        properties = pika.BasicProperties(delivery_mode=2, content_type='application/json'))
    
    channel.basic_ack(delivery_tag = method.delivery_tag)
    
  def run(self):
    logger.info("started resolver.")
    
    try:
      self.channel.basic_qos(prefetch_count=25)
      self.channel.basic_consume(self.message_handler, queue='query')
      self.channel.start_consuming()
    except KeyboardInterrupt:
      logger.info('stopping resolver.')
      self.channel.stop_consuming()
      self.connection.close()
    
    return 0


if __name__ == '__main__':
  import argparse
  import ConfigParser
  from email.mime.text import MIMEText
  from subprocess import Popen, PIPE
  
  parser = argparse.ArgumentParser(description = "digger - resolver rabbit", add_help=False)
  parser.add_argument('--help', action = 'help')
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-h', '--host', required = True, help = "rabbitmq server hostname")
  parser.add_argument('-p', '--port', default = 5672, help = "rabbitmq server port")
  parser.add_argument('--user', default = 'digger', help = "rabbitmq server username")
  parser.add_argument('--password', required=True, help = "rabbitmq server password")
  
  args = parser.parse_args()

  r = Resolver(host = args.host, port = args.port, user = args.user, password = args.password)
  r.verbose = args.verbose
  sys.exit(r.run())

