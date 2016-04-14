There's no particular setup _needed_ for this project, but a few tools may be helpful:

### Editorconfig

Tool for maintaining consistent per-project coding style by automating some of your text editor's settings (indentation in particular) based on the [`.editorconfig`](https://github.com/aisapatino/sjfnw/blob/master/.editorconfig) file. See [editorconfig.org](http://editorconfig.org/) for more info. There are plugins for many editors, including:

  - [Sublime](https://github.com/sindresorhus/editorconfig-sublime#readme)
  - [Vim](https://github.com/editorconfig/editorconfig-vim#readme)

### Prospector plugin

Shows lint warnings in your editor so you don't need to run the command line script. [Install pylint](linters.md) first.

**Sublime3**: [SublimeLinter](http://sublimelinter.readthedocs.org/en/latest/) + [SublimeLinter-pylint](https://packagecontrol.io/packages/SublimeLinter-pylint)

_TODO: check for Sublime prospector plugin_

In your [user settings](http://sublimelinter.readthedocs.org/en/latest/settings.html#settings-sources), under `"linters"`, include

```json
"pylint": {
  "rcfile": "[path to repo]/.pylintrc"
}
```

**Vim**: [syntastic](https://github.com/scrooloose/syntastic)

In your `.vimrc`, include

```vim
let g:syntastic_python_checkers = ['prospector']
let g:syntastic_python_prospector_args = '--profile=[path to repo]/.landscape.yml'
```
