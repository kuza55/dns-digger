import os
import re
import shutil
import urllib2
import urlparse
import datetime
import xml.dom.minidom

import source

class clean_mx(source.Base):
  
  def __init__(self):
    self.retrieved = False
    self.url = "http://support.clean-mx.de/clean-mx/xmlviruses.php?"
    self.dir = os.path.join('log', 'blacklists', str(datetime.date.today()))
    self.filename = os.path.join(self.dir, 'support.clean-mx.de')
    
  @property 
  def name(self):
    return "support.clean-mx.de"
  
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
      dom = xml.dom.minidom.parse(f)
      items = dom.getElementsByTagName("entry")
    
      for item in items:
        domain = item.getElementsByTagName("domain")[0].childNodes[0].data
        yield {"domain":domain}
      
