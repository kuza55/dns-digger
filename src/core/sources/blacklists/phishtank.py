import os
import re
import csv
import gzip
import json
import shutil 
import tempfile
import urllib2
import urlparse
import datetime

import source

class phishtank(source.Base):
  
  def __init__(self):
    self.retrieved = False
    self.dir = os.path.join('log', 'blacklists', str(datetime.date.today()))
    self.filename = os.path.join(self.dir, 'phishtank.com.csv.gz')  
    self.api_key = '4abb40d62ffd19925833130b4c6e0fb2ede2aa5d74fcd2f07965a79e52e168bb'
    self.url = "http://data.phishtank.com/data/%s/online-valid.csv.gz" % (self.api_key,)	
    self.patterns = {"ip": "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"}
	
  @property 
  def name(self):
    return "phishtank.com"
  
  def retrieve(self):
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    
    req = urllib2.urlopen(self.url)
    with open(self.filename, 'wb') as f:
      shutil.copyfileobj(req, f)
      
    self.retrieved = True
  
  @property
  def domains(self):
    if not self.retrieved:
      self.retrieve()
    
    assert self.retrieved
    
    with gzip.open(self.filename) as f:
      reader = csv.reader(f, quoting=csv.QUOTE_NONE)
      header = reader.next()
      for row in reader:
        entry = dict(zip(header, row))
        try:
          domain = urlparse.urlparse(entry['url']).hostname
        
          if domain and not re.match(self.patterns['ip'], domain):
    				yield {'domain': domain, 'label': 'phishing', 'info': json.dumps(entry)}        
        except UnicodeDecodeError:
          pass
