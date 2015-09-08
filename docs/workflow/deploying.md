Current process: manual deploy with `appcfg.py`, tag using the date. Tagging is so we can easily see what exact code is live, and compare it to the last release, in cases where something is going wrong.

#### Prepare for release

1. Merge the desired change into `master`.
2. Verify that the changes don't break anything. (This should have been done before merging to `master`, too)  
  a. Make sure all tests pass.  
  b. Checkout master locally and test the app; particularly the parts that have been changed.

#### Release

1. Tag the commit you will be releasing. Currently we're using a format like this:  
  `git tag -a 2015-08-09 -m "summary of changes"`  
  a. Make sure the first line is under 72 chars like with commit messages.  
  b. The message doesn't need to be comprehensive; commit messages and diffs can be used to get the full details.  
  c. If it's not the first tag in a day, do `2015-08-09.2` etc.
2. Deploy the code.  
  a. Make sure you don't have any local uncommitted changes; they will be deployed.  
  b. `appcfg.py update .` (if you are in root of repo) to deploy to app engine.  
  c. `git push --tags` to push the release tag.
3. Verify that the live site is working


More info:

- [appcfg](https://cloud.google.com/appengine/docs/python/tools/uploadinganapp#Python_Uploading_the_app)
- [git tags](https://git-scm.com/book/en/v1/Git-Basics-Tagging)
