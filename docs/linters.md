Project is set up for [pylint](http://www.pylint.org/) and [eslint](http://eslint.org/docs/), syntax & style checkers for python and javascript.

##### Installation
  - pylint:
    - `sudo apt-get install pylint` or `pip install pylint` (details [here](http://www.pylint.org/#install))
    - make sure you have v1.4+ (do `pip list` to see, `pip -U pylint` to upgrade)
    - `pip install pylint-django` - [plugin](https://github.com/landscapeio/pylint-django) that makes pylint more django friendly
  - eslint: _(optional)_
    - You'll need npm first: `sudo apt-get install node` + `sudo apt-get install npm` or see their [docs](https://docs.npmjs.com/getting-started/installing-node) for instructions.
    - `npm install -g eslint` See [this page](https://docs.npmjs.com/getting-started/fixing-npm-permissions) if you get a permissions error.

##### Usage - in text editor

See [[text editor setup|text-editor-setup]] for more info.

##### Usage - CLI
  - To lint the whole project: `./scripts/lint.sh`
  - That will output results to the console. If you want to save results to a file, you can do `./scripts/lint.sh > filename.txt`

##### Configuration
  - [.pylintrc](https://github.com/aisapatino/sjfnw/blob/master/.pylintrc) ([docs](http://docs.pylint.org/features.html))
  - [.eslintrc](https://github.com/aisapatino/sjfnw/blob/master/.eslintrc) ([docs](http://eslint.org/docs/rules/))