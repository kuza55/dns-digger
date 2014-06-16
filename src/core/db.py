#!/usr/bin/env python
__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import datetime
import urlparse
import sqlalchemy 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, Date, Boolean
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
Session = sessionmaker()

class Domain(Base):
  __tablename__ = 'domains'
  id = Column(Integer, primary_key=True)
  _domain = Column('domain', String, unique=True)
  active  = Column('active', Boolean)
  sources = relationship('Source', backref='domain')

  @hybrid_property
  def domain(self):
    return self._domain

  @domain.setter
  def domain(self, domain):
    self._domain = Domain.normalize(domain)

  @staticmethod
  def normalize(d):
    """
      Normalize a domain name for consistency:
        1. lowercase
        2. remove trailing spaces
        3. remove trailing dots 
        4. remove any url scheme (http://)
        5. remove any url path (/index.html)
        6. remove any ports (:8080)
    """
    # 1. lowercase and remove trailing spaces and dots
    domain = d.lower().strip()
    
    # 2. 3.
    if domain == '.':
      return domain
    else:
      domain = domain.strip('.')

    # 4. 5. remove any url scheme prefix or trailing path
    u = urlparse.urlparse(domain)
    if u.scheme:
      domain = u.hostname
    
    # 6. remove any ports
    u = urlparse.urlparse('//' + domain)
    if u.port or u.path:
      domain = u.hostname
      
    return domain

  def __repr__(self):
    return "<Domain(id='%s', domain='%s', active='%s')>" % \
      (self.id, self.domain, self.active)

class Source(Base):
  __tablename__  = 'sources'
  __table_args__ = (ForeignKeyConstraint(['domain_id'], ['domains.id']),)
  domain_id = Column(Integer, primary_key=True)
  source    = Column(String, primary_key=True)
  date      = Column('log_date', Date, primary_key=True, default=datetime.datetime.utcnow)
  label     = Column(String)
  info      = Column(String)

  def __repr__(self):
    return "<Source(domain_id='%s', source='%s', label='%s', date='%s')>" % \
      (self.domain_id, self.source, self.label, self.date)

