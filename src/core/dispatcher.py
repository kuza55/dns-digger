__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import sys
import json
import time
import logging

import pika

from log import logger
from module import Module

class Dispatcher(Module):
  """Dispatch query requests to stub resolvers.

  Dispatcher is a producer responsible for acting on the priority queue, 
  sending messages to resolvers when domains' TTLs expire, and monitoring 
  the priority queue for neglected or outstanding queries.
  """
  def setup_queues(self):
    # declare message path
    chan = self.rabbit.channel()
    chan.exchange_declare(exchange='dns', type='direct')
    chan.queue_declare(queue='query', durable=True)
    chan.queue_declare(queue='response', durable=True)
    chan.queue_declare(queue='reduce', durable=True)
    chan.queue_declare(queue='archive', durable=True)
    
    # bind queues to exchange
    chan.queue_bind(exchange='dns', queue='query', routing_key='query')
    chan.queue_bind(exchange='dns', queue='response', routing_key='response')
    chan.queue_bind(exchange='dns', queue='archive', routing_key='response')
      
  def dispatch(self):
    redis = self.redis
    channel = self.rabbit.channel()

    query_config = dict(self.config.items('query'))
    query_type = query_config['type']
    num_resolvers = int(query_config['resolvers'])
    distfactor = int(query_config['distribution'])

    logger.info("started dispatcher.")

    prev = 0
    while True:
      now = time.time()

      # dispatch domains
      domains = redis.zrangebyscore('domains', prev, now)
      for domain in domains:        
        resolvers = [redis.srandmember('resolvers') for i in range(num_resolvers)]   
        message = json.dumps({'domain' : domain, 'resolvers' : resolvers, 'type' : query_type })

        # send message to multiple resolvers
        for i in range(distfactor):
          channel.basic_publish(exchange='dns', routing_key='query', 
            properties =  pika.BasicProperties(content_type='application/json'), body=message)

        if self.verbose:
          logger.info("sent %r." % (message,))

      prev = now

      # reschedule negelected domains
      domains = redis.zrangebyscore('domains', 0, (now - 60*60))
      for domain in domains:
        redis.zadd('domains', time.time(), domain)
      if len(domains) > 0:
        logger.info("reprioritized %d neglected domains." % (len(domains),))

      time.sleep(5)

  def run(self):
    self.setup_queues()
    try:
      self.dispatch()
    except KeyboardInterrupt:
      logger.info("stopping dispatcher.")
    return 0
          
