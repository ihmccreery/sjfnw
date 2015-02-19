<p align="center">
  <a href="https://travis-ci.org/aisapatino/sjfnw">
    <img src="https://travis-ci.org/aisapatino/sjfnw.svg?branch=master">
  </a>
  <a href="https://coveralls.io/r/aisapatino/sjfnw?branch=master">
   <img src="https://coveralls.io/repos/aisapatino/sjfnw/badge.svg?branch=master">
  </a>
</p>

- **[Installation and setup](#installation-and-setup)**
  - [Code](#code)
  - [Python](#python)
  - [Git](#git)
  - [Google App Engine SDK & Django](#google-app-engine-sdk-includes-django)
  - [MySQL](#mysql)
  - [Setting up the database](#setting-up-the-database)
  - [Loading fixtures](#loading-fixtures)
- **[Running a local server](#running-a-local-server)**
  - [Logging in](#logging-in)
- **[Running tests](#running-tests)**
- **[Project structure](#project-structure)**
- **[Code conventions](#code-conventions)**
  - [Linters](#linters)
- **[Git workflow](#git-workflow)**
- **[Tools](#tools)**
  - [Issue tracking](#issue-tracking)
  - [Travis CI](#travis-ci)
  - [Coveralls.io](#coverallsio)
- **[Deploying](#deploying)**
- **[References](#references)**

-----

## Installation and setup

Instructions assume you're running linux or mac osx and can use a package manager as needed - homebrew, apt-get, etc.

#### Code

`git clone https://github.com/aisapatino/sjfnw.git`

#### Python

The project uses python 2.7, which is probably already installed with your OS. To confirm:

`python --version`

Install using package manager if needed.

#### Git

May be installed already, check with

`git --version`

Install/update using package manager if needed.

#### [Google App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) (includes Django)

Download & unzip. Update your `~/.bashrc`:

```
export PATH=$PATH:/[path to gae]`
export PYTHONPATH=$PYTHONPATH:[path to gae]
export PYTHONPATH=$PYTHONPATH:[path to gae]/lib/yaml/lib
export PYTHONPATH=$PYTHONPATH:[path to gae]/lib/webob-1.2.3
```

_Note: Project currently uses Django 1.5, which is the latest version included with GAE. See #691 for discussion of upgrading._

#### MySQL

Install: `mysql-server`, `python-mysqldb`

When prompted, enter the password from [`sjfnw/settings.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py#L43)

Once those have installed, create the database:

1. `mysql -uroot -p` to get into the mysql shell. This will prompt you for the password you set when you installed.
2. Make sure mysql is set to use `utf8` encoding everywhere.
- You can check with `show variables like 'char%';`
- If anything is set to `latin1`, change it with `set [variable name]=utf8;`
3. `create database sjfdb_local;`

#### Setting up the database

`./manage.py syncdb`

You should see output as tables are created in the local database based on the project's model definitions.
Create a superuser when prompted - that creates a user account that you can use to log into the admin site on your local server.

_If this doesn't work, make sure `manage.py` has execute permissions. `chmod a+x manage.py` should work._

#### Loading fixtures

To populate your local db with data:

`./manage.py load_testing_data`

## Running a local server

`dev_appserver.py ../sjfnw`

_If you get something like 'command not found', make sure GAE is in your path. Use `echo $PATH` to confirm._

#### Logging in

The superuser you created in the `syncdb` step gives you access to the admin site. For testing locally you'll want to be able to log into the fundraising and grant application areas too.

1. Go to `/admin-advanced`* and log in with superuser email & pw you created when you ran `syncdb`.
2. Create a `Member` object so you can log into the fundraising app:
  - Click on `+ Add` next to `Members`
  - Enter the email you used to log in, and whatever first & last name you want.
  - Hit `Save`
3. Go back to `/admin-advanced` to create an `Organization` for yourself:
  - Click on `+Add` next to `Organizations`
  - Enter the same email, fill in whatever other fields are required
  - Hit `Save`
4. You should now be able to log into both sides of the app: `/fund/login` and `/apply/login`

\* The advanced admin site is only used by devs (and should eventually be replaced with better admin permissions). Staff use `/admin`, which you can use most of the time, but for this you need additional access.

## Running tests

`./manage.py test fund grants`

To check test coverage, install [coverage.py](http://nedbatchelder.com/code/coverage/), then do

`./scripts/coverage.sh`

which will output coverage details as html files in `./coverage-html`

## Project structure

Most of the project structure is determined by Django; see link under [references](#references).

Some things that may warrant explaining:
- `pytz` is [highly recommended](https://docs.djangoproject.com/en/1.5/topics/i18n/timezones/) by Django for handling time zones/time zone aware datetimes.
- `unicodecsv` a pretty small wrapper around python's `csv` module, which [does not support Unicode input](https://docs.python.org/2/library/csv.html)) in 2.7.9. There is some export functionality through the admin site that uses it.
- `sjfnw/static/django_admin` is a copy of `django/contrib/admin/media`. GAE can provide the library, but [does not provide the assets](http://stackoverflow.com/a/9863345).

## Code conventions

All of this is a work in progress in the current code. Expect a lot of pylint errors for the time being.

- 2 space indents! Python is space/indent sensitive and varying indents will throw errors.
  - An [editorconfig](http://editorconfig.org/#download) plugin may be useful if you use other indentation levels in other projects.
- Generally follow google's [Python style guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)

#### Linters

Project contains configs for [pylint](http://www.pylint.org/) and [eslint](http://eslint.org/docs/), syntax & style checkers for python and javascript.

Installation
  - pylint:
    - `sudo apt-get install pylint` or `pip install pylint` (details [here](http://www.pylint.org/#install))
    - make sure you have v1.4+ (do `pip list` to see, `pip -U pylint` to upgrade)
    - `pip install pylint-django` - [plugin](https://github.com/landscapeio/pylint-django) that makes pylint more django friendly
  - eslint:
    - You'll need npm first: `sudo apt-get install node` + `sudo apt-get install npm` or see their [docs](https://docs.npmjs.com/getting-started/installing-node) for instructions.
    - `npm install -g eslint` See [this page](https://docs.npmjs.com/getting-started/fixing-npm-permissions) if you get a permissions error.

Usage
  - There are a lot of lint errors currently, so you'll often want to lint just the file(s) you're currently working on.
  - Some text editors have plugins to run them from within the editor.
      - Vim: [syntastic](https://github.com/scrooloose/syntastic)
      - Sublime3: [SublimeLinter](http://sublimelinter.readthedocs.org/en/latest/) + [SublimeLinter-pylint](https://packagecontrol.io/packages/SublimeLinter-pylint) + [SublimeLinter-eslint](https://github.com/roadhump/SublimeLinter-eslint)
  - To lint the whole project: `./scripts/lint.sh`

Configuration
  - [.pylintrc](https://github.com/aisapatino/sjfnw/blob/master/.pylintrc) ([docs](http://docs.pylint.org/features.html))
  - [.eslintrc](https://github.com/aisapatino/sjfnw/blob/master/.eslintrc) ([docs](http://eslint.org/docs/rules/))

## Git workflow

#### Commits

- Try to keep commits pretty granular - group related changes into commits rather than one huge commit at the end
- First line of the commit message should be a short overview of the changes
- Use the commit body to give more detail and/or [link issues](https://help.github.com/articles/closing-issues-via-commit-messages/) if applicable

#### Branches

`master` is the main branch\*. - To start, avoid ever pushing directly to `master`. Instead, when working on a feature/change, create a new branch:

```
  git checkout master
  git pull
  git checkout -b new-feature
```

When your changes are ready, open a [pull request](https://help.github.com/articles/using-pull-requests/) so the code can be reviewed and merged into master.

\* _We can add a `develop` branch if needed, but for now it doesn't seem necessary_

## Database management

TODO - keeping models and db table structure synced over time

## Tools

#### Issue tracking

- Issues are filed in github: [sjfnw issues](https://github.com/aisapatino/sjfnw/issues)
- The goal setup is something like
  - Milestones with no due date for broad sorting ('p1', 'p2', etc)
  - Sprints have their own milestones with a due date. Issues are pulled from the highest priority bucket milestone.
  - Sprint milestones are closed at the end of the sprint and unfinished issues are moved into the next sprint.
- Always search issues before creating a new one to make sure it hasn't already been filed.

#### Travis CI

https://travis-ci.org/aisapatino/sjfnw

Travis runs tests whenever a new commit is pushed to github. The badge at the top of the README reflects the results of the most recent test run on `master`

When previewing or creating a pull request, there will be icons next to some commits indicating test success or failure on travis. Click to see details.

#### Coveralls.io

https://coveralls.io/r/aisapatino/sjfnw

Tool for tracking test coverage over time. When Travis runs tests, it reports the coverage results and they're recorded at the link above. You can click on a commit to see a breakdown by file, and click on a file to see line-by-line coverage.

Coveralls is configured to leave a comment on every pull request with the change in code coverage.

_Note: Coveralls is currently very slow to update, so if you see "no data" or your PR status stays at pending, that's probably why._

## Deploying

There are currently a couple ways to deploy code to app engine:

1. Recommended: Set up push-to-deploy. See 'existing repository' section of [these instructions](https://console.developers.google.com/project/sjf-nw/clouddev/source/repo). You can either install gcloud, or click the link at the bottom to set up auth without it (it's quite quick to do so). Once you're set up, you can deploy by just pushing to that remote, i.e. `git push google master`
2. Use `appcfg.py` from the GAE SDK. Instructions [here](https://cloud.google.com/appengine/docs/python/tools/uploadinganapp#Python_Uploading_the_app)

I recommend 1 because it fits nicely into git workflow and makes it very easy to tell exactly what code is in production - you can browse code and commits though the cloud console. `appcfg.py` is useful if you want to deploy at a non-default version without having to change the `app.yaml` file accordingly.

## References

- [Git](http://git-scm.com/docs)
  - Has links to a good cheatsheet and an interactive intro to git
- [Django](https://docs.djangoproject.com/en/1.5/)
  - Note: If you google something you'll often wind up at the most recent docs. Make sure you're looking at the docs version that matches our current Django version (currently 1.5)
- [Python](https://docs.python.org/2/library/index.html)
  - [TestCase built-in methods & assertions](https://docs.python.org/2/library/unittest.html#unittest.TestCase)
  - [Regular expressions](http://doc.pyschools.com/html/regex.html)
- [Google App Engine](https://cloud.google.com/appengine/docs/python/)
  - Note: Those docs don't apply to this project in many cases since we use Django
  - [app.yaml](https://cloud.google.com/appengine/docs/python/config/appconfig) is the GAE app config file
  - The project's [cron tasks](https://cloud.google.com/appengine/docs/python/config/cron) use GAE
- [MySQL reference/tutorial](http://sqlzoo.net/wiki/Main_Page)
- [Intro to CSS](https://developer.mozilla.org/en-US/docs/Web/Guide/CSS/Getting_started)
- [CSS properties reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference)
- [HTML guide](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML)
- [Intro to HTTP and REST](http://code.tutsplus.com/tutorials/a-beginners-guide-to-http-and-rest--net-16340)
