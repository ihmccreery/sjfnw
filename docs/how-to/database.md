### Migrations

Whenever you add/change/delete a model or a model field, you should add a migration. See the django docs on [migration workflow](https://docs.djangoproject.com/en/1.8/topics/migrations/#workflow) for more info.

1. Make the change in your local code
2. Record the change with `./manage.py makemigrations`
  - Do `--dry-run` first to make sure it looks correct.
  - Use `--name` to give it a descriptive name. E.g. `--name add_cycle_question`
3. Update your local database: `./manage.py migrate` will run the migration you created.
4. Run local server and verify that it doesn't crash.
5. Add/update tests as needed, verify that all tests are passing
6. Always put the model change and the new migration file in the same commit.

See the linked docs for more detail on migrations and the commands used.

### Databases

See [sjfnw/settings.py](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py) where databases are configured. Each environment uses a different db:

- **Testing**: `sqlite3`, a local, in-memory, super fast db. It is managed automatically by the testing framework. See [intro to testing](../tests/intro-to-testing.md#django-and-python-testing) for more info.
- **Local server**: Local `mysql` instance. See [installation and setup](../getting-started/installation-and-setup.md#mysql).
- **Production**: The deployed app uses a CloudSQL database, which is basically a hosted MySQL.

### Connecting to MySQL

#### Locally

1. `mysql -uroot -p`
2. Enter password when prompted
3. `use sjfdb_multi;`

#### Remote CloudSQL database

1. `mysql --host=111.111.111.111 -uroot -p` (replace with actual IP)
2. Enter password when prompted
3. `use sjfdb;`

Note: To connect to CloudSQL, you need to configure it to allow connections from your IP address. Every time you connect to CloudSQL from a different IP address, you'll need to repeat this.

1. Find your IP address. Googling 'my ip' works.
2. Convert it to CIDR notation: use [this tool](http://www.ipaddressguide.com/cidr#range) and enter your IP in both fields.
3. Take the output and enter it in the [CloudSQL console](https://console.developers.google.com/project/1038977021851/sql/instances/sjf/access-control/authorization) under 'Allowed Networks'
