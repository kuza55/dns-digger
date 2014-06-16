__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import time
import json

import wdns

from db import Domain
from log import logger
from module import Module

class Scheduler(Module):
  """Schedule future queries of domains.

    Scheduler is a consumer which updates the next query time,
    according to the TTLs of responses from the Resolvers.
  """
  def __init__(self, config, verbose=False):
    super(Scheduler, self).__init__(config, verbose)
    query_config = dict(config.items('query')) 
    self.minttl = int(query_config.get("minttl", 300))
    self.maxttl = int(query_config.get("maxttl", 3600))
    self.rrtype = wdns.str_to_rrtype(query_config.get("type", "A"))
  
  def update_priority(self, domain, response, query_time):
    now = time.time()
    if response:
      answers = [rr for rr in response.sec[1] if rr.rrtype == self.rrtype]
      if answers:
        ttl = min(rr.rrttl for rr in answers)
        # min(max(expiration, now), configured maximum)
        priority = min(max(query_time + max(self.minttl, ttl), now), now + self.maxttl)
        self.redis.zadd('domains', priority, domain)       
        return
    # query again in an hour
    self.redis.zadd('domains', (now + 60*60), domain)
  
  def message_handler(self, channel, method, properties, body):
    if self.verbose:
      logger.info("received %r" % (body,))

    message = json.loads(body)
    domain = Domain.normalize(message.get('domain'))
    response = message.get('response')    
    query_time = message.get('time', time.time())
        
    # parse dns message if there was one
    if response:
      try:
        response = wdns.parse_message(response.decode('base64'))
      except wdns.MessageParseException, e:
        response = None
    
    # update priority in redis if domain exists 
    if self.redis.zscore('domains', domain):
      self.update_priority(domain, response, query_time)
  
    channel.basic_ack(delivery_tag=method.delivery_tag)
  
  def run(self):
    logger.info("started scheduler.")
    channel = self.rabbit.channel()
    try:
      channel.basic_consume(self.message_handler, queue='response')
      channel.start_consuming()
    except KeyboardInterrupt:
      logger.info("stopping scheduler.")
    return 0

