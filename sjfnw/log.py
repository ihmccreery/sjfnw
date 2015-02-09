import logging, os, sys

RED = '\033[00;31m'
YELLOW = '\033[00;33m'
RESET '\033[00m'
BOLD= '\033[1m'

def configure_logging():
  datefmt = '%Y-%m-%d %H:%M:%S'
  if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    log_format = '[%(filename)s:%(lineno)d %(funcName)s]: %(message)s'
  else:
    log_format = '%(levelname)-8s %(asctime)s %(filename)s %(funcName)s:%(lineno)d]: %(message)s'

  handlers = logging.getLogger().handlers
  if handlers:
    sys.stdout.write('setting formatter')
    handlers[0].setFormatter(logging.Formatter(fmt=log_format, datefmt=datefmt))
  else:
    sys.stdout.write('basicconfig')
    logging.basicConfig(format=log_format, datefmt=datefmt)


# log errors
def log_exception(*args, **kwds):
  logging.exception('Exception in request:')
