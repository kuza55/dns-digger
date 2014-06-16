import os
import re
import shutil
import urllib2
import datetime
import urlparse

import source

class siriurz(source.Base):
  
  def __init__(self):
    self.retrieved = False
    self.url = 'http://vxvault.siri-urz.net/URL_List.php'
    self.dir = os.path.join('log', 'blacklists', str(datetime.date.today()))
    self.filename = os.path.join(self.dir, 'vxvault.siri-urz.net')
    self.patterns = {
      "ip": "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    }
  
  @property 
  def name(self):
    return 'vxvault.siri-urz.net'
  
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
    assert self.retrieved
    
    with open(self.filename) as f:
      for line in f:
        domain = urlparse.urlparse(line).hostname
        if domain and not re.match(self.patterns['ip'], domain):
          yield {'domain': domain, 'info': line.strip()}

  
    
