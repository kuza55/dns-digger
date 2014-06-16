import re
import tempfile
import urllib2
from urlparse import urlparse

import source

class iseclab(source.Base):
  
  def __init__(self):
    self.retrieved = False
    self.tmp = tempfile.TemporaryFile()
  
  def __del__(self):
    if self.tmp:
      self.tmp.close
  
  @property 
  def name(self):
    return "exposure.iseclab.org"
  
  def retrieve(self):
    u = urllib2.urlopen("http://exposure.iseclab.org/malware_domains.txt")
    self.tmp.write(u.read())
    self.tmp.seek(0)
    self.retrieved = True
    return
  
  @property
  def domains(self):
    if not self.retrieved:
      self.retrieve()
    
    assert self.retrieved
    
    for line in self.tmp:
      yield {"domain":line.strip()}
      
