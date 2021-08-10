[![CircleCI](https://circleci.com/gh/ENCODE-DCC/snovault-search/tree/dev.svg?style=svg)](https://circleci.com/gh/ENCODE-DCC/snovault-search/tree/dev)
[![Coverage Status](https://coveralls.io/repos/github/ENCODE-DCC/snovault-search/badge.svg?branch=dev)](https://coveralls.io/github/ENCODE-DCC/snovault-search?branch=dev)
# snovault-search
Framework-independent package for converting query strings to Elasticsearch queries.

### Run tests
```bash
$ pip install -e .[test]
$ pytest
```

### Publish on PyPI
Bump version in `setup.cfg`, then build and upload:
```bash
$ python -m build
$ twine upload dist/*
```
