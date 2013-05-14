#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sjfnw.settings")

  from django.core.management import execute_from_command_line

  #test setup - hacky?
  sys.path.append(os.path.dirname(__file__) + '\\sjfnw')
  sys.path.append('C:\Program Files (x86)\Google\google_appengine\lib\webob-1.2.3')
  #print("\n".join(sys.path))

  execute_from_command_line(sys.argv)