import logging, os

def configure_logging():
  datefmt = '%Y-%m-%d %H:%M:%S'

  if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    log_format = '[%(filename)s:%(lineno)d %(funcName)s]: %(message)s'
  else:
    log_format = '%(levelname)-8s %(asctime)s %(filename)s %(funcName)s:%(lineno)d]: %(message)s'

  handlers = logging.getLogger().handlers
  if handlers:
    handlers[0].setFormatter(logging.Formatter(fmt=log_format, datefmt=datefmt))
  else:
    logging.basicConfig(format=log_format, datefmt=datefmt)

def log_exception(*args, **kwargs):
  # stack trace is automatically added, as is basic request info
  logging.exception('Exception in request:')
