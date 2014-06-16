import re
import tempfile
import urllib2
from datetime import date, timedelta

import source

class snort(source.Base):

  def __init__(self):
    self.retrieved = False
    self.tmp = tempfile.TemporaryFile() 
  
  def __del__(self):
    if self.tmp:
      self.tmp.close
        
  @property
  def name(self):
    return "labs.snort.org"
    
  def retrieve(self):   
    try:
      yesterday = date.today() - timedelta(1)
      u = urllib2.urlopen("http://labs.snort.org/iplists/dnslist-%s" % (str(yesterday),))
      self.tmp.write(u.read())
      self.tmp.seek(0)
      self.retrieved = True
    except urllib2.HTTPError:
      pass
    return

  @property
  def domains(self):
    if not self.retrieved:
      self.retrieve()
    
    self.tmp.seek(0)
    for line in self.tmp:
      l = line.strip()
      if l == '' or l[0] == '#':
        continue
       
      yield { "domain": l }
      
