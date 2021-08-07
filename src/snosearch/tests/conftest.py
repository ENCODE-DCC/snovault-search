import pytest


@pytest.fixture
def dummy_registry(testing_types):
    from snosearch.adapters.types import register_type_from_dict
    from snosearch.interfaces import TYPES
    from pyramid.registry import Registry
    registry = Registry()
    type_registry = {}
    for type_dict in testing_types:
        register_type_from_dict(type_registry, type_dict)
    registry[TYPES] = type_registry
    return registry


@pytest.fixture
def dummy_request(dummy_registry):
    from pyramid.request import Request
    dummy_request = Request({})
    dummy_request.registry = dummy_registry
    return dummy_request


@pytest.fixture
def testing_search_schema_type():
    return {
        'name': 'TestingSearchSchema',
        'item_type': 'testing_search_schema',
        'schema': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'uniqueKey': True,
                },
                'status': {
                    'type': 'string',
                },
                'uuid': {
                    'title': 'UUID',
                    'description': 'Unique identifier',
                    'type': 'string',
                    'format': 'uuid',
                    'permission': 'import_items',
                    'requestMethod': 'POST',
                },
                'accession': {
                    'title': 'Accession',
                    'description': '',
                    'type': 'string',
                    'format': 'accession',
                    'permission': 'import_items'
                },
                'label': {
                    'type': 'string',
                }
            },
            'additionalProperties': False,
            'facets': {
                'status': {
                    'title': 'Status',
                    'open_on_load': True
                },
                'name': {
                    'title': 'Name'
                }
            },
            'boost_values': {
                'accession': 1.0,
                'status': 1.0,
                'label': 1.0
            },
            'columns': {
                'accession': {
                    'title': 'Accession'
                },
                'status': {
                    'title': 'Status'
                }
            }
        },
        'audit_inherit': ['*'],
        'matrix': {
            'x': {
                'group_by': 'label'
            },
            'y': {
                'group_by': ['status', 'name']
            }
        },
        'missing_matrix': {
            'x': {
                'group_by': 'label'
            },
            'y': {
                'group_by': ['status', ('name', 'default_name')]
            }
        },
        'audit': {
            'audit.ERROR.category': {
                'group_by': 'audit.ERROR.category',
                'label': 'Error'
            },
            'audit.INTERNAL_ACTION.category': {
                'group_by': 'audit.INTERNAL_ACTION.category',
                'label': 'Internal Action'},
            'audit.NOT_COMPLIANT.category': {
                'group_by': 'audit.NOT_COMPLIANT.category',
                'label': 'Not Compliant'
            },
            'audit.WARNING.category': {
                'group_by': 'audit.WARNING.category',
                'label': 'Warning'
            },
            'x': {
                'group_by': 'status', 'label': 'Status'
            }
        }
    }


@pytest.fixture
def testing_post_put_patch_type():
    return {
        'name': 'TestingPostPutPatch',
        'item_type': 'testing_post_put_patch',
        'schema': {
            'required': ['required'],
            'type': 'object',
            'properties': {
                "schema_version": {
                    "type": "string",
                    "pattern": "^\\d+(\\.\\d+)*$",
                    "requestMethod": [],
                    "default": "1",
                },
                "uuid": {
                    "title": "UUID",
                    "description": "",
                    "type": "string",
                    "format": "uuid",
                    "permission": "import_items",
                    "requestMethod": "POST",
                },
                "accession": {
                    "title": "Accession",
                    "description": "",
                    "type": "string",
                    "format": "accession",
                    "permission": "import_items"
                },
                'required': {
                    'type': 'string',
                },
                'simple1': {
                    'type': 'string',
                    'default': 'simple1 default',
                },
                'simple2': {
                    'type': 'string',
                    'default': 'simple2 default',
                },
                'protected': {
                    'type': 'string',
                    'default': 'protected default',
                    'permission': 'import_items',
                },
                'protected_link': {
                    'type': 'string',
                    'linkTo': 'TestingLinkTarget',
                    'permission': 'import_items',
                },
            }
        }
    }


@pytest.fixture
def testing_search_schema_special_facets_type():
    return {
        'name': 'TestingSearchSchemaSpecialFacets',
        'item_type': 'testing_search_schema_special_facets',
        'schema':  {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'uniqueKey': True,
                },
                'status': {
                    'type': 'string',
                },
                'read_count': {
                    'type': 'number',
                },
                'uuid': {
                    'title': 'UUID',
                    'description': 'Unique identifier',
                    'type': 'string',
                    'format': 'uuid',
                    'permission': 'import_items',
                    'requestMethod': 'POST',
                },
                'accession': {
                    'title': 'Accession',
                    'description': '',
                    'type': 'string',
                    'format': 'accession',
                    'permission': 'import_items'
                },
                'label': {
                    'type': 'string',
                }
            },
            'additionalProperties': False,
            'facets': {
                'status': {
                    'title': 'Status',
                    'type': 'exists',
                },
                'read_count': {
                    'title': 'Read count range',
                    'type': 'stats',
                },
                'name': {
                    'title': 'Name'
                }
            },
            'boost_values': {
                'accession': 1.0,
                'status': 1.0,
                'label': 1.0
            },
            'columns': {
                'accession': {
                    'title': 'Accession'
                },
                'status': {
                    'title': 'Status'
                }
            }
        }
    }


@pytest.fixture
def test_config_item_search_config():
    return {
        'name': 'TestConfigItem',
        'facets': {'a': 'b'},
    }


@pytest.fixture
def testing_types(testing_search_schema_type, testing_post_put_patch_type, testing_search_schema_special_facets_type):
    return [
        testing_search_schema_type,
        testing_post_put_patch_type,
        testing_search_schema_special_facets_type,
    ]
