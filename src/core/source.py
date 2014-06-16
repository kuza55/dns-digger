__author__ = "Kevin Warrick"
__email__ = "kwarrick@uga.edu"

import os
import abc
import shutil
import urllib2
import datetime

class ParseBeforeRetrieve(Exception):
  """ Exception for calling parse method before retrieve. """
  pass

class Base(object):
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractproperty
  def name(self):
    return
    
  @abc.abstractmethod
  def retrieve(self):
    """ Retrieve domains from source. """
    return
    
  @abc.abstractproperty
  def domains(self):
    """ Parse domains from retrieve source """
    return
