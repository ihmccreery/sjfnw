### Travis CI

[travis-ci.org/aisapatino/sjfnw](https://travis-ci.org/aisapatino/sjfnw)

Travis runs tests whenever a new commit is pushed to github. The 'build' badge at the top of the readme reflects the results of the most recent test run on `master`.

When previewing or creating a pull request, there will be icons next to some commits indicating test success or failure on travis. Click to see details.

### Codecov.io

[codecov.io/github/aisapatino/sjfnw](https://codecov.io/github/aisapatino/sjfnw)

Tool for tracking test coverage over time. Provides the 'coverage' badge in the readme. Coverage details can be accessed at the link above. You can click on a commit to see a breakdown by file, and click on a file to see line-by-line coverage.

The coverage data comes from the python [coverage](http://coverage.readthedocs.org/en/latest/) package, which is installed and run as part of travis - see [`.travis.yml`](https://github.com/aisapatino/sjfnw/blob/master/.travis.yml)

If coverage drops below the target specified in `.codecov.yml`, codecov's commit check will report failure.

### Landscape.io

[landscape.io/github/aisapatino/sjfnw](https://landscape.io/github/aisapatino/sjfnw)

Tool for checking code "health" - runs `prospector` on every commit. See [linting](/getting-started/linters.md) for details. It provides the 'health' badge in the readme.
