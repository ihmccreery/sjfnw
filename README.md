[Installation](#installation)  
[Running a local server](#running-a-local-server)  
[Using fixtures](#using-fixtures-to-populate-your-local-database)  
[Running tests](#running-tests)  
[Project conventions](#project-conventions)  
[Deploying](#deploying)  

-----

## Installation

Instructions assume you're running linux or mac osx and can use a package manager as needed - homebrew, apt-get, etc.

#### Python 2.7x & git
Should come installed with your OS. Confirm with `python --version` and `git --version` and install/update if needed.

#### [Google App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) (includes Django)

Download & unzip. Update your `~/.bashrc`:
```
export PATH=$PATH:/[path to gae]`
export PYTHONPATH=$PYTHONPATH:[path to gae]
export PYTHONPATH=$PYTHONPATH:[path to gae]/lib/yaml/lib
export PYTHONPATH=$PYTHONPATH:[path to gae]/lib/webob-1.2.3
```

#### MySQL

Install **mysql-server** and **python-mysqldb**. When prompted, enter the password used in `sjfnw/settings.py` under database.

Once those have installed, create the database:

1. `mysql -uroot -p` to get into the mysql shell. This will prompt you for the password you set when you installed.
2. Make sure mysql is set to use `utf8` encoding everywhere. You can check with `show variables like 'char%';`. If anything is set to `latin1`, change it with `set [variable name]=utf8;`
3. `create database sjfdb_local;`

## Running a local server

The first time, or after adding new models, you'll need to sync the database first. From root level of the repo, run:

`./manage.py syncdb`

You should see output as tables are created in the local database.
Create a superuser when prompted - that creates a user account that you can use to log into the admin site on your local server.

_If this doesn't work, make sure `manage.py` has execute permissions. `chmod a+x manage.py` should work._

##### To run the server:

Move up one level to the directory containing the repo and run:

`dev_appserver.py sjfnw`

_If you get something like 'command not found', make sure GAE is in your path. Use `echo $PATH` to confirm._

## Using fixtures to populate your local database

To populate your local db with data, do `./manage.py load_testing_data`. This olds old fixtures from the live database.

## Running tests

`./manage.py test fund grants`

To check test coverage, install [coverage.py](http://nedbatchelder.com/code/coverage/), then do

`sh check_coverage.sh`

which will output coverage details as html files in `/.coverage-html`

## Project conventions

#### Code

- **2 space indents** Python is space/indent sensitive and varying indents will throw errors.
  - An [editorconfig](http://editorconfig.org/#download) plugin may be useful if you use other indentation levels in other projects.
- Generally follow google's [Python style guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html) (a work in progress in the current code)

##### Linters
- Project contains configs for [pylint](http://www.pylint.org/) and [eslint](http://eslint.org/docs/) which check the syntax and style of the python and javascript code in the project.
- Installation
  - pylint:
    - `sudo apt-get install pylint` or `pip install pylint` on mac os (more details [here](http://www.pylint.org/#install)
    - make sure you have v1.4+ (do `pip list` to see, `pip -U pylint` to upgrade)
  - eslint:
    - You'll need npm first, which requires node. `sudo apt-get install node` + `sudo apt-get install npm` or see their [docs](https://docs.npmjs.com/getting-started/installing-node) for instructions.
    - `npm install -g eslint` See [this page](https://docs.npmjs.com/getting-started/fixing-npm-permissions) if you get a permissions error.
- Usage
  - You can run each from the command line (see links for details)
  - Some text editors have plugins to run them from within the editor. For example, with vim, you can use [syntastic](https://github.com/scrooloose/syntastic).
  

#### Issue tracking

- Issues are filed in github: [sjfnw issues](https://github.com/aisapatino/sjfnw/issues)
- The goal setup is something like
  - Milestones with no due date for broad sorting ('p1', 'p2', etc)
  - Sprints have their own milestones with a due date. Issues are pulled from the highest priority bucket milestone.
  - Sprint milestones are closed at the end of the sprint and unfinished issues are moved into the next sprint.
- Always search issues before creating a new one to make sure it hasn't already been filed.

#### Git

- `master` represents code that is in production.
- `develop` is the main integration branch.
- Short-lived branches should be created and then merged into develop.
- Generally aim for small commits with descriptive summaries.
- [Link issues](https://help.github.com/articles/closing-issues-via-commit-messages/) in your commit descriptions when applicable.

See [this post](http://nvie.com/posts/a-successful-git-branching-model/) for more details on the general git branching model we're going for.

## Deploying

There are currently a couple ways to deploy code to app engine:

1. Recommended: Set up push-to-deploy. See 'existing repository' section of [these instructions](https://console.developers.google.com/project/sjf-nw/clouddev/source/repo). You can either install gcloud, or click the link at the bottom to set up auth without it (it's quite quick to do so). Once you're set up, you can deploy by just pushing to that remote, i.e. `git push google master`
2. Use `appcfg.py` from the GAE SDK. Instructions [here](https://cloud.google.com/appengine/docs/python/tools/uploadinganapp#Python_Uploading_the_app)

I recommend 1 because it fits nicely into git workflow and makes it very easy to tell exactly what code is in production - you can browse code and commits though the cloud console. `appcfg.py` is useful if you want to deploy at a non-default version without having to change the `app.yaml` file accordingly.
