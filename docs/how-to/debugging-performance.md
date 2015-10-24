[Django Debug Toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar):

> The Django Debug Toolbar is a configurable set of panels that display various debug information about the current request/response

A good tool for examining the time it takes to make a request - in particular, for looking at what queries are made and how much time they're taking up. Queries can be logged to the console if you use `--log-level debug`, but this is a much more readable format, and shows information about timing.

### Setup

1. Install: `pip install django-debug-toolbar`
    - Make sure it's on your path. To install it somewhere specific add `-t [target directory]` 
    - If it installs django as a dependency, delete that copy; otherwise it may clash with the version of Django you already have installed.
2. Configure: In `settings.py`, uncomment the django debug toolbar config
3. Copy static files: `cp -r [install location]/static/debug_toolbar [sjfnw repo]/sjfnw/static`
    - Currently, we don't do any build step, which the toolbar expects in order to serve its static assets, so copying is a quick hacky way to make it work
    - Make sure to avoid committing the copied static files

### Use

Run your local server and load a page. You'll see a panel on the right side. Click a section to see more information. Check the [django debug toolbar docs](http://django-debug-toolbar.readthedocs.org/en/latest/panels.html) for details.

The main thing to look at is queries:

- Look at the total time compared to the SQL time to see if queries are a major part of the page load time.
- Look for redundant or unnecessary queries
    - Queries that aren't being used
    - Repeats of the same query
    - Similar queries that could be combined
    - Queries for related objects that could be combined
