## Migrations (changes to models)

Whenever you add/change/delete a model or a model field, you should add a migration. See the docs for [migration workflow](https://docs.djangoproject.com/en/1.8/topics/migrations/#workflow). Short version:

1. Make the change in your local code
2. Record the change: `./manage.py makemigrations`. Preferably, use `-n` to give it a descriptive name.
3. Update your local database: `./manage.py migrate` will run the migration you created.
4. Run local server and verify that it doesn't crash.
5. Add/update tests as needed, verify that all tests are passing
6. Always put the model change and the new migration file in the same commit.

See the linked docs for more detail on migrations and the commands used.

## Background

See [sjfnw/settings.py](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py) where databases are configured.

- **Testing**: `sqlite3`, a local, in-memory, super fast db. It is managed automatically by the testing framework. See [intro to testing](../tests/intro-to-testing.md#django-and-python-testing) for more info.
- **Local server**: Local `mysql` instance. See [installation and setup](../getting-started/installation-and-setup.md#mysql).
- **Production**: The deployed app uses a CloudSQL database, which is basically a hosted MySQL.

## Connecting to MySQL

1. Connect to a mysql instance from the command line
  local: `mysql -uroot -p`
  remote: `mysql --host=111.111.111.111 -uroot -p`
  `-uroot` means sign in as the user 'root'
  `-p` means prompt for password
  `-host` specifies the IP of the remote host (replace with actual IP)
  _Every time you connect to CloudSQL from a different IP address, you'll need to adjust permissions as described below._

2. Use the app's database

  local: `use sjfdb_local;`
  remote: `use sjfdb;`

#### CloudSQL permissions

To connect to CloudSQL, you need to configure it to allow connections from your IP address.

1. Find your ip address. Googling 'my ip' works.
2. Convert it to CIDR notation: use [this tool](http://www.ipaddressguide.com/cidr#range) and enter your IP in both fields.
3. Take the output and enter it in the [CloudSQL console](https://console.developers.google.com/project/1038977021851/sql/instances/sjf/access-control/authorization) under 'Allowed Networks'
