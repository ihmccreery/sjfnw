Most of the project structure is determined by Django (more info in [resources](../resources.md)).

Dependencies that aren't provided by Google App Engine are listed in `requirements.txt` and installed into `libs/` via `pip`. See [setup](../getting-started/installation-and-setup.md#project-dependencies) for details. Current packages in `libs` are:

- `django` is included with GAE, but only up to 1.5. We're using 1.8.4 manually instead.
- `pytz` is [highly recommended](https://docs.djangoproject.com/en/1.8/topics/i18n/timezones/) by Django for handling time zones/time zone aware datetimes.
- `unicodecsv` is a pretty small wrapper around python's `csv` module, which [does not support Unicode input](https://docs.python.org/2/library/csv.html) in 2.7.9. There is some export functionality through the admin site that uses it.
