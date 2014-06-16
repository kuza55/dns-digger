__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import os
import time
import urllib2
import pkgutil
import inspect
import datetime
import importlib

import tldextract 

import db
import source
from log import logger
from module import Module

class Aggregator(Module):
  """Aggregate and activate new domains.

  Aggregator uses reflection to enumerate all the classes in the blacklists module,
  each of which retrieve and parse a list of malicious domain names from a unique
  source.

  To add an additional source implement a class that subclasses the abstract base class source.Base, 
  and place in the core/sources/ directory.
  """
  def __init__(self, resolvers, domains, source, config, verbose=False):
    super(Aggregator, self).__init__(config)
    self.config = config
    # input files
    self.source = source
    self.resolvers_file = resolvers
    self.domains_file = domains
    # retrieval scripts
    self.sources = self.load_sources()  
    
  def load_sources(self, pkg=None):
    """ Dynamically enumerate packages (sources/**/.py) and import domain sub-classes of source.Base for execution.  """
    sources = []
    if pkg is None:
      pkg = importlib.import_module('sources')
    for loader, name, is_pkg in pkgutil.walk_packages(pkg.__path__, prefix=(pkg.__name__ + '.')):
      if not is_pkg:
        module = loader.find_module(name).load_module(name)
        for s in dir(module):
          attr = getattr(module, s)
          if inspect.isclass(attr) and issubclass(attr, source.Base):
            sources.append(attr)
    return sources

  def invoke_sources(self):
    """ Execute each source class generating domains. """
    for klass in self.sources:
      count  = 0

      source = None
      if 'config' in inspect.getargspec(klass.__init__).args:
        source = klass(self.config)
      else:
        source = klass()

      try:
        for entry in source.domains:
          labels = tldextract.extract(entry['domain'])
          if all(labels[1:]) and not any([c for c in entry['domain'] if ord(c) > 128]):
            count += 1
            yield entry, source.name
          else:
            logger.warn("invalid domain: %s from %s" % (entry['domain'], source.name))
        logger.info("aggregated %d domains from %s." % (count, source.name or ''))
      except urllib2.URLError, ex:
        logger.error("failed to retrieve domain blacklist - %s" % (source.name,))
  
  def find_or_create_domain(self, session, _domain, _source, label="", info=""):
    _domain = db.Domain.normalize(_domain)

    # find or create domain
    domain = session.query(db.Domain).filter_by(domain=_domain).first()
    if not domain:
      domain = db.Domain(domain=_domain, active=True)
      session.add(domain)
    assert domain

    # find or create source
    source = session.query(db.Source).\
      filter(db.Source.domain == domain).\
      filter_by(source=_source).\
      first()
    if not source:
      source = db.Source(domain_id=domain.id, source=_source, label=label, info=info)
      session.add(source)

    return domain

  def create_working_dir(self):
    """ Make timestamped working directory. """
    time = datetime.datetime.now()
    wd = os.path.join("log", "aggregator", time.strftime("%Y%m%d%H%M%S"))
    if not os.path.exists(wd):
      os.makedirs(wd)
      logger.info("created working directory %s." % (wd,))
    
    assert os.path.isdir(wd), "working directory not created"
    return wd

  def collect(self):  
    """ Compose domains from input files and source scripts. """
    # select active domain names from the database
    session = db.Session(bind=self.db, autoflush=True)
    domains = session.query(db.Domain).filter_by(active=True).all()
    logger.info("aggregated %d active domains from the database." % (len(domains),))

    # aggregate domains from auxiliary input files
    if self.domains_file:
      with open(self.domains_file) as f:
        for domain in filter(None, (l.strip() for l in f)):
          domain = self.find_or_create_domain(session, domain, self.source)
          domains.append(domain)
    session.commit()

    # aggregate domains from sources
    for entry, source in self.invoke_sources():
      domain = entry.get('domain')
      label = entry.get('label', '')
      info = entry.get('info', '')
      domain = self.find_or_create_domain(session, domain, source, label, info)
      domains.append(domain)
    session.commit()

    logger.info("aggregated %d total domains" % (len(domains),))

    return domains
        
  def run(self):
    """ Collect active domains from the database, scripts, and input files. """
    logger.info("started aggregator.")
    
    try:
      # 1. collect domains
      domains = set(d.domain for d in self.collect() if d.active)
      
      # 2. log aggregated domains
      wd = self.create_working_dir()
      with open(os.path.join(wd, 'aggregated'), 'w') as f:
        f.write("\n".join(domains))
      
      # 3. add domains to redis
      for domain in domains:
        score = self.redis.zscore('domains', domain)
        if not (score and score > time.time()):
          self.redis.zadd('domains', time.time(), domain)
      
      # 4. add resolvers to redis
      if self.resolvers_file:
        with open(self.resolvers_file) as f:
          for line in f:
            self.redis.sadd('resolvers', line.strip())
    except KeyboardInterrupt:
      logger.info("stopping aggregator.")

    return 0
