This documentation is kept the `docs/` directory of the [`sjfnw` repo](https://github.com/aisapatino/sjfnw). It is written in markdown, converted to html using [mkdocs](http://www.mkdocs.org/), and published using Github Pages.

### File structure

- `mkdocs.yml` configures mkdocs. It includes an index of all the pages, which is used to build the navigation menus.
- `docs/` contains the source files. They're grouped into folders to match the way they're grouped in nav.
- `docs/_theme/` contains files for customizing the appearance/layout of the output.
- `docs/README.md` shows when you browse [`docs/` in the repo](https://github.com/aisapatino/sjfnw/tree/master/docs) to point people to the processed version.

### Updating

- To preview the docs site locally, use `mkdocs serve`, then go to `http://127.0.0.1:8000/`. It will automatically update as you make changes.
- If you add, remove or rename a file, make sure you update `mkdocs.yml` accordingly.
- `mkdocs gh-deploy` will build and then push to the `gh-pages` branch which updates the docs site.
