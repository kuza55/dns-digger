__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import sys
import json
import logging
import logging.handlers
import collections

import pika

class Archiver(object):
  """Write JSON responses to disk as CSV file.

  Archiver is a simple consumer which uses Python's logging module and the 
  TimeRotatingFileHandler to archive raw JSON messages to disk as CSVs.
  """
  def __init__(self, queue, config):
    self.queue = queue
    self.config = config
    self.rabbit_conn, self.rabbit_channel = self.connect()

  def connect(self):
    rabbit_config = dict(self.config.items('rabbitmq'))
    creds = pika.PlainCredentials(rabbit_config['user'], rabbit_config['password'])
    params = pika.ConnectionParameters(host=rabbit_config['host'], 
                                       port=int(rabbit_config['port']),
                                       credentials=creds)
    rabbit_conn = pika.BlockingConnection(params)
    rabbit_channel = rabbit_conn.channel()
    
    return rabbit_conn, rabbit_channel
    
  def message_handler(self, channel, method, properties, body):
    message = collections.defaultdict(str, json.loads(body))
    
    flags = message.get('flags', '')
    if not 'ignore' in flags:      
      message['response'] = message['response'].replace("\n", '')
      self.logger.info("%(domain)s,%(resolver)s,%(time)d,%(response)s,%(error)s" % message)   
    
    channel.basic_ack(delivery_tag=method.delivery_tag)

  def run(self):
    self.logger = logging.getLogger('archiver')
    self.logger.setLevel(logging.INFO)
        
    # handler = logging.handlers.RotatingFileHandler('log/responses', maxBytes=(2**30))
    handler = logging.handlers.TimedRotatingFileHandler('log/responses', when='midnight')
    handler.setFormatter('')
    self.logger.addHandler(handler)
    
    try:
      self.rabbit_channel.basic_consume(self.message_handler, queue=self.queue)
      self.rabbit_channel.start_consuming()
    except KeyboardInterrupt:
      self.rabbit_channel.stop_consuming()
      self.rabbit_conn.close()

    return 0

