The repo is set up to use [prospector](http://prospector.landscape.io/en/master/index.html), a tool that combines several python code-checkers including [pylint](http://www.pylint.org/).

`prospector` is run for every commit pushed to github via [landscape.io](https://landscape.io/github/aisapatino/sjfnw); see [CI page](../workflow/continuous-integration.md) for more info.

### Installation

`./scripts/install-lint`

### Usage

`prospector`

For info on usage through a text editor see [text editor setup](text-editor-setup.md).

### Configuration

- Prospector: [.landscape.yml](https://github.com/aisapatino/sjfnw/blob/master/.landscape.yml)
    - Thus named because it also configures landscape.io runs
    - More info: [prospector profiles](http://prospector.landscape.io/en/master/profiles.html#builtin-profiles)
- Pylint: [.pylintrc](https://github.com/aisapatino/sjfnw/blob/master/.pylintrc)
    - More info: [pylint docs](http://docs.pylint.org/features.html)
