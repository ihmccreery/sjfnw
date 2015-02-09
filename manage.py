#!/usr/bin/env python
import os, sys

from django.core.management import execute_from_command_line

from sjfnw.log import configure_logging

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sjfnw.settings")
  configure_logging()
  execute_from_command_line(sys.argv)
