Consistent code formatting and style makes it easier to read and maintain. This is a work in progress in the current code; existing code is being updated gradually. **All new code should follow the guidelines below**.

### Code style guidelines

Generally follow google's [Python style guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html). A few exceptions/clarifications:

- 2 space indents  
- Single quotes except for docstrings  
- We're not as stringent with line length; aim for <100

See the [linters](../getting-started/linters.md) page for information on plugins that check syntax/style. Note that pylint does _not_ check quotes or indentation, but should catch most other issues.
