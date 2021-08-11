[![CircleCI](https://circleci.com/gh/ENCODE-DCC/snovault-search/tree/dev.svg?style=svg)](https://circleci.com/gh/ENCODE-DCC/snovault-search/tree/dev)
[![Coverage Status](https://coveralls.io/repos/github/ENCODE-DCC/snovault-search/badge.svg?branch=dev)](https://coveralls.io/github/ENCODE-DCC/snovault-search?branch=dev)
# snovault-search
Framework-independent package for converting query strings to Elasticsearch queries.

### Install
```bash
$ pip install snovault-search
```

### Example
```python
from snosearch.defaults import DEFAULT_ITEM_TYPES
from snosearch.fields import BasicSearchResponseField
from snosearch.parsers import ParamsParser
from snosearch.responses import FieldedResponse


def basic_search_view(request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            BasicSearchResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            )
        ]
    )
    return fr.render()
```

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
