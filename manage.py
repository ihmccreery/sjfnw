#!/usr/bin/env python
import setup_env

import sys

from django.core.management import execute_from_command_line

from sjfnw.log import configure_logging

if __name__ == "__main__":
  configure_logging()
  execute_from_command_line(sys.argv)
