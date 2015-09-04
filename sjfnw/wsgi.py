import setup_env

from django.core.wsgi import get_wsgi_application
from django.core.signals import got_request_exception

from sjfnw.log import configure_logging, log_exception

configure_logging()

got_request_exception.connect(log_exception)

application = get_wsgi_application()
