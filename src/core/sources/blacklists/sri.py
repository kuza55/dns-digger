import os
import re
import urllib2
from datetime import date, timedelta

import source
class sri(source.Base):

  def __init__(self):
    self.retrieved = False
    
    yesterday = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
    # self.url = "http://cgi.mtc.sri.com/download/malware_dns/%s/Get_Top-100_30-Day_WatchList.html" % (yesterday,)
    self.url = "http://cgi.mtc.sri.com/download/malware_dns/%s/Get_Top-18_30-Day_WatchList.html" % (yesterday,)
    self.dir = os.path.join('log', 'blacklists', str(date.today()))
    self.filename = os.path.join(self.dir, 'cgi.mtc.sri.com')
    
  @property
  def name(self):
    return "cgi.mtc.sri.com"
    
  def retrieve(self):  
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
       
    req = urllib2.urlopen(self.url)
    page = req.read()
    with open(self.filename, 'w') as f: 
      f.write(page.split('<pre>')[1].rsplit('</pre>')[0])
    self.retrieved = True
      
    return
    
  @property
  def domains(self):
    if not self.retrieved:
      self.retrieve()
    
    with open(self.filename) as f:
      for line in f:
        l = line.strip()
        if l == '' or l[0] in ('#', '!',):
          continue
        
        domain =  re.split('\s', l, 1)[0]
        yield { "domain": domain, "label":"malware"}
      
