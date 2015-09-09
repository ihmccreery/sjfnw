Recommended setup:

### Editorconfig

Helps maintain consistent per-project coding style by automating some of your text editor's settings (indentation in particular) based on the [`.editorconfig`](https://github.com/aisapatino/sjfnw/blob/master/.editorconfig) file. See [editorconfig.org](http://editorconfig.org/) for more info.

- [Sublime](https://github.com/sindresorhus/editorconfig-sublime#readme)
- [vim](https://github.com/editorconfig/editorconfig-vim#readme)

### Pylint plugin

Show lint warnings in your editor so you don't need to run the command line script. [Install pylint](linters.md) first.

Sublime3: [SublimeLinter](http://sublimelinter.readthedocs.org/en/latest/) + [SublimeLinter-pylint](https://packagecontrol.io/packages/SublimeLinter-pylint) + [SublimeLinter-eslint](https://github.com/roadhump/SublimeLinter-eslint)

In your [user settings](http://sublimelinter.readthedocs.org/en/latest/settings.html#settings-sources), under `"linters"`, include

```json
"pylint": {
  "rcfile": "[path to repo]/.pylintrc",
  "args": "--load-plugins pylint_django"
}
```

Vim: [syntastic](https://github.com/scrooloose/syntastic)

In your `.vimrc`, include

```vim
let g:syntastic_python_checkers = ['pylint']
let g:syntastic_python_pylint_args = '--load-plugins pylint_django --rcfile=[path to repo]/.pylintrc'
```

