import os
import re
import shutil
import urllib2
import datetime

import source

class zeustracker(source.Base):

  def __init__(self):
    self.retrieved = False
    
    self.url = "https://zeustracker.abuse.ch/blocklist.php?download=domainblocklist"
    self.dir = os.path.join('log', 'blacklists', str(datetime.date.today()))
    self.filename = os.path.join(self.dir, 'zeustracker.abuse.ch')
    
    self.patterns = {"ip": "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"}
        
  @property
  def name(self):
    return "zeustracker.abuse.ch"
    
  def retrieve(self):
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
      
    req = urllib2.urlopen(self.url)
    with open(self.filename, 'wb') as f:
      shutil.copyfileobj(req, f)

    self.retrieved = True
    return
    
  @property
  def domains(self):
    if not self.retrieved:
      self.retrieve()
    
    with open(self.filename) as f:      
      for line in f:
        l = line.strip()
        if l == '' or l[0] == '#':
          continue
       
        yield { "domain": l }
      
