#!/usr/bin/env python
import os
import sys
import logging

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sjfnw.settings")

  from django.core.management import execute_from_command_line

  logging.basicConfig(format='%(levelname)-8s %(asctime)s %(filename)s:%(lineno)d %(funcName)s]: %(message)s', 
      datefmt = '%Y-%m-%d %H:%M:%S')

  execute_from_command_line(sys.argv)
