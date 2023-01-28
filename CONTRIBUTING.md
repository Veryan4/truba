### Development Requirement

The following applications should be installed for development:

- [docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [node.js](https://nodejs.org/en/download/)
- [python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installing/)

Using VSCode is recommended since the `.vscode` directory in the repo will suggest and configure the required extensions.

### Style and Formatting

Automated formatting tools such as yapf and prettier are used for both the Javascript and Python services

In order to be as standard as possible, the google style guides have been adopted.

Python: https://google.github.io/styleguide/pyguide.html
Angular: https://angular.io/guide/styleguide

### Testing

Unit tests are not required for the front-end since it's subject to frequent updating.
On the python services, a unit-test must be produced for each new function.
All contributed code must be wrapped in functions.

### N.B.

- The ml service is still very much work in progress, and is subject to change. That is why there is currently no docstrings.

### Questions

Contact the maintainer: veryan.goodship@truba.news for access to the cluster
