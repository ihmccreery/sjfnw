### Short version

1. Branch off of the latest `master`
2. Use concise, descriptive commit messages
3. Add/update tests
4. Open a PR against `master`

### Branches

`master` is for code that is tested, reviewed and ready to deploy. When working on a feature/change, create a new branch:

```sh
git checkout master
git pull
git checkout -b new-branch-name
```
### Commits

- Try to keep commits granular - group related changes into commits rather than one huge commit at the end
- The first line of the commit message should be a short overview of the changes (<72 chars so it isn't truncated)
- Use the commit body to give more detail and/or [link issues](https://help.github.com/articles/closing-issues-via-commit-messages/) if applicable

Example:
```
clean up grant application javascript

remove console.logs, use more description function names
fixes #43
```
### Pull requests

When your changes are ready, open a [pull request](https://help.github.com/articles/using-pull-requests/) so the code can be reviewed and merged.
