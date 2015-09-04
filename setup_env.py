import os, sys

setup_complete = False

if not setup_complete:
  # path - add project root and libs directory
  sys.path.append(os.path.dirname(__file__))
  sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libs'))

  # env
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sjfnw.settings')

  setup_complete = True
