import os
import logging

def setup_logger():
  LOG_FORMAT = '%(asctime)s [%(levelname)s] (%(module)s): %(message)s'

  formatter = logging.Formatter(LOG_FORMAT)

  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  console.setFormatter(formatter)

  logpath = os.path.join(os.path.dirname(__file__), '..', '..', 'log', 'digger.log')
  logfile = logging.FileHandler(filename=logpath)

  logfile.setLevel(logging.INFO)
  logfile.setFormatter(formatter)

  logger = logging.getLogger('digger')
  logger.setLevel(logging.INFO)
  logger.addHandler(console)
  logger.addHandler(logfile)
  return logger

logger = setup_logger()
