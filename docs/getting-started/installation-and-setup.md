Instructions assume you're running linux or mac osx and can use a package manager ([`homebrew`](http://brew.sh/), `apt-get`, etc.) as needed.

#### Code

`git clone https://github.com/aisapatino/sjfnw.git`

#### Python & pip

The project uses python 2.7, which is probably already installed with your OS. Confirm by doing `python --version`. Install using package manager if needed.

You'll also need `pip`, python's package manager. It is included with python 2.7.9 and above, so you should have it already. Try `pip --version`.

If you don't have it, you can upgrade your python installation to 2.7.9 or 2.7.10, or [install pip directly](https://pip.pypa.io/en/stable/installing.html).

#### Git

May be installed already, check with `git --version`. Install/update using package manager if needed.

#### MySQL

Install mysql and a python-mysql adapter.

Linux: `apt-get install mysql-server python-mysqldb`  
OSX: `brew install mysql`, `pip install mysql-python`

When prompted, enter the password from [`sjfnw/settings.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py#L43)

Create the database:

1. `mysql -uroot -p` to get into the mysql shell. This will prompt you for the password you set when you installed.
2. `create database sjfdb_multi character set utf8 collate utf8_general_ci;`

#### Google App Engine SDK

[Download](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) & unzip (somewhere outside the repo).
Follow the instructions to install using the GoogleAppEngineLauncher.

#### Project dependencies

`./scripts/install-libs`

This will install everything listed in `requirements.txt` into the `libs` folder.

#### Update paths

Update your `~/.bashrc` (or other file depending on the shell you use)

```sh
export PATH=$PATH:/[path to gae]
export PYTHONPATH=$PYTHONPATH:[path to Google App Engine]
export PYTHONPATH=$PYTHONPATH:[path to GAE]/lib/webob-1.2.3
export PYTHONPATH=$PYTHONPATH:[path to repo]/sjfnw/libs
```

#### Verify

Run `./scripts/verify-install` to verify that you've installed everything successfully. It doesn't verify everything (for instance, database creation), but can check the basics. You should see output like this:

```
Checking installation...

Python: 2.7.6 (required: 2.7.x)
pip: 7.1.2 (required: any)
Mysql: 5.5.44 (required: 5.5.x or 5.6.x)
Google AppEngine SDK: Found in PATH and PYTHONPATH

Checking libs...
  - django: found
  - pytz: found
  - unicodecsv: found

✔ Basic installation checks passed.
```

#### Set up your local database

`./manage.py migrate`

You should see output as tables are created in the local database based on the project's model definitions.

For more info on what this does, see the [django docs](https://docs.djangoproject.com/en/1.8/topics/migrations/) and the [project migration docs](../how-to/database.md).

_If that didn't work, make sure `manage.py` has execute permissions. `chmod u+x manage.py` should work._

#### Create a superuser

`./manage.py createsuperuser`

A superuser is a django user account with the highest access levels - you can use it to log into the admin site on your local server.

#### Load fixtures

We have fixtures with data from the real site. To load that data into your local db:

`./manage.py load_testing_data`

---

Installation complete! Now check out [running a local server](./local-server.md) and [running tests](./running-tests.md).
