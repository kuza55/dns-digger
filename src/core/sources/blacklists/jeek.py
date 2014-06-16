import re
import tempfile
import urllib2
from urlparse import urlparse

import source

class jeek(source.Base):
  
  def __init__(self):
    self.retrieved = False
    self.tmp = tempfile.TemporaryFile()
  
  def __del__(self):
    if self.tmp:
      self.tmp.close
  
  @property 
  def name(self):
    return "jsunpack.jeek.org"
  
  def retrieve(self):
    u = urllib2.urlopen("http://jsunpack.jeek.org/dec/go?list=url")
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
      u = urlparse(line.strip())
      
      if not u.hostname:
        continue
      
      yield {"domain":u.hostname.strip()}

  
