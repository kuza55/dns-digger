__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import pika 
import redis
import psycopg2
import sqlalchemy
import collections

class Module(object):
  """ Digger module base class wraps configuration and service connections. """
  def __init__(self, config, verbose=False):
    self.config  = config
    self.verbose = verbose
    self._db     = None
    self._redis  = None
    self._rabbit = None

  def __del__(self):
    if self._rabbit and self._rabbit.is_open:
      self._rabbit.close()

  @property
  def rabbit(self):
    """ RabbitMQ connection wrapper. """
    if not self._rabbit or not self._rabbit.is_open:
      rabbit_config = dict(self.config.items('rabbitmq'))
      host = rabbit_config.get('host', 'localhost')
      port = int(rabbit_config.get('port', 5672))
      username = rabbit_config.get('user', 'guest')
      password = rabbit_config.get('password', '')
      
      creds = pika.PlainCredentials(username, password)
      params = pika.ConnectionParameters(host=host, port=port, credentials=creds)
      self._rabbit = pika.BlockingConnection(params)
    return self._rabbit

  @property
  def redis(self):
    """ Redis connection wrapper. """
    if not self._redis:
      redis_config = dict(self.config.items('redis'))
      host = redis_config.get('host', 'localhost')
      port = int(redis_config.get('port', 6379))
      self._redis = redis.StrictRedis(host=host, port=port)
    return self._redis

  @property
  def db(self):
    """ Database connection wrapper. """
    if not self._db:
      db_config = collections.defaultdict(str, self.config.items('database'))
      url = "%(dialect)s://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % db_config
      self._db = sqlalchemy.create_engine(url)
    return self._db

