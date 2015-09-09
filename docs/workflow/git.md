#### Commits

- Try to keep commits granular - group related changes into commits rather than one huge commit at the end
- First line of the commit message should be a short overview of the changes (<72 chars so it isn't truncated)
- Use the commit body to give more detail and/or [link issues](https://help.github.com/articles/closing-issues-via-commit-messages/) if applicable

Example:

```
clean up grant application javascript

remove console.logs, use more description function names
fixes #43
```

#### Branches

`master` is the main branch. Avoid ever pushing directly to `master`. Instead, when working on a feature/change, create a new branch:

```sh
git checkout master
git pull
git checkout -b new-branch-name
```

For a long-running feature, use a feature branch based off of `master`. Open PRs/merge into that branch, and base new feature-related branches off of it. Then when the feature is complete, merge that branch into `master`.
  
#### Pull requests

When your changes are ready, open a [pull request](https://help.github.com/articles/using-pull-requests/) so the code can be reviewed and merged into `master`.
