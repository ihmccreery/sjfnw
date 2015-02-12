import os, sys

# put pytz on path first so django can find it
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libs'))

from django.core.wsgi import get_wsgi_application
from django.core.signals import got_request_exception

from sjfnw.log import configure_logging, log_exception

# path & env vars
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sjfnw.settings")

configure_logging()
got_request_exception.connect(log_exception)

# define wsgi app
application = get_wsgi_application()

