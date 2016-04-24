Overview of current process: verify that everything works locally, then use `scripts/deploy` to deploy.

### Prepare for release

1. Merge the desired change into `master`.
2. Verify that the changes don't break anything. (This should have been done before merging to `master`, too)
  a. Make sure all tests pass.
  b. Checkout master locally and test the app; particularly the parts that have been changed.

### Release

If your change involves migrations, these instructions don't cover that. Contact @aisapatino.

1. Run `scripts/deploy`
  a. If you want to be safe, you can first deploy to an alternate version (I usually use '2') and check that it works before updating the live site.
2. Check deployment
  a. The output of the script should include a link. Navigate to the affected areas and verify that they work.
3. Tag updates to default version
  a. The output of the script should include instructions for tagging. Add an annotated tag with the current date.
  b. If it's not the first tag in a day, do `yyyy-mm-dd.2`, etc.
  c. **`git push --tags`** to push the release tag.

### More info

- [deploy script source](https://github.com/aisapatino/sjfnw/blob/master/scripts/deploy)
- [appcfg](https://cloud.google.com/appengine/docs/python/tools/uploadinganapp#Python_Uploading_the_app)
- [git tags](https://git-scm.com/book/en/v1/Git-Basics-Tagging)
