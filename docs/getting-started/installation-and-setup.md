Instructions assume you're running linux or mac osx and can use a package manager ([`homebrew`](http://brew.sh/), `apt-get`, etc.) as needed.

#### Code

`git clone https://github.com/aisapatino/sjfnw.git`

#### Python

The project uses python 2.7, which is probably already installed with your OS. Confirm by doing `python --version`. Install using package manager if needed.

#### Git

May be installed already, check with `git --version`. Install/update using package manager if needed.

#### MySQL

Install mysql and a python-mysql adapter.

Linux: `apt-get install mysql-server python-mysqldb`  
OSX: `brew install mysql`, `pip install mysql-python` (you should have `pip` already, see [below](#prerequisite-pip) if not)

When prompted, enter the password from [`sjfnw/settings.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py#L43)

Once those have installed, create the database:

1. `mysql -uroot -p` to get into the mysql shell. This will prompt you for the password you set when you installed.
2. `create database sjfdb_local character set utf8 collate utf8_general_ci;`

#### Set up the database

`./manage.py syncdb`

You should see output as tables are created in the local database based on the project's model definitions.
Create a superuser when prompted - that creates a user account that you can use to log into the admin site on your local server.

_If this doesn't work, make sure `manage.py` has execute permissions. `chmod u+x manage.py` should work._

#### Load fixtures

To populate your local db with data:

`./manage.py load_testing_data`

#### Google App Engine SDK

[Download](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) & unzip (somewhere outside the repo).

#### Project dependencies

##### Prerequisite: `pip`

You'll need `pip`, python's package manager. It is included with python 2.7.9 and above, so you should have it already. Try `pip --version`.

If you don't have it, you can [install it directly](https://pip.pypa.io/en/stable/installing.html) or upgrade your python installation.

##### Install dependencies

`./scripts/install-libs`

This will install everything listed in `requirements.txt` into the `libs` folder.

#### Update paths

Update your `~/.bashrc` (or other file depending on the shell you use)

```sh
export PATH=$PATH:/[path to gae]
export PYTHONPATH=$PYTHONPATH:[path to gae]
export PYTHONPATH=$PYTHONPATH:[path to gae]/lib/webob-1.2.3
export PYTHONPATH=$PYTHONPATH:[path to repo]/sjfnw/libs
```

#### Verify

Run `./scripts/verify-install` to verify that you've installed everything successfully. It doesn't verify everything (for instance, database setup), but can check the basics. You should see output like this:

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