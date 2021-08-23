import pytest


@pytest.fixture
def dummy_registry(testing_types, testing_configs):
    from snosearch.adapters.types import register_type_from_dict
    from snosearch.adapters.configs import register_search_config_from_dict
    from snosearch.configs import SearchConfigRegistry
    from snosearch.interfaces import TYPES
    from snosearch.interfaces import ELASTIC_SEARCH
    from snosearch.interfaces import SEARCH_CONFIG
    from pyramid.registry import Registry
    registry = Registry()
    type_registry = {}
    for type_dict in testing_types:
        register_type_from_dict(type_registry, type_dict)
    registry[TYPES] = type_registry
    registry[ELASTIC_SEARCH] = None
    config_registry = SearchConfigRegistry()
    for config_dict in testing_configs:
        register_search_config_from_dict(config_registry, config_dict)
    registry[SEARCH_CONFIG] = config_registry
    return registry


@pytest.fixture
def pyramid_dummy_request(dummy_registry):
    from snosearch.tests.dummy_requests import PyramidDummyRequest
    dummy_request = PyramidDummyRequest({}).blank('/dummy')
    dummy_request.registry = dummy_registry
    return dummy_request


@pytest.fixture
def flask_dummy_request(dummy_registry):
    from snosearch.tests.dummy_requests import FlaskDummyRequestAdapter
    from flask import Request
    from flask import Response
    dummy_request = FlaskDummyRequestAdapter(
        Request(
            {
                'PATH_INFO': '/dummy'
            }
        )
    )
    dummy_request.registry = dummy_registry
    dummy_request.response = Response()
    return dummy_request


@pytest.fixture
def dummy_request(request, pyramid_dummy_request, flask_dummy_request):
    if hasattr(request, 'param') and request.param == 'flask':
        return flask_dummy_request
    return pyramid_dummy_request


@pytest.fixture
def testing_search_schema_type():
    return {
        'name': 'TestingSearchSchema',
        'item_type': 'testing_search_schema',
        'schema': {
            'type': 'object',
            'properties': {
                '@id': {
                    'notSubmittable': True,
                    'type': 'string',
                    'title': 'ID'
                },
                '@type': {
                    'notSubmittable': True,
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'title': 'Type'
                },
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
            'facet_groups': [
                {
                    'title': 'Test group',
                    'facet_fields': [
                        'status',
                        'name',
                    ]
                }
            ],
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
                '@id': {
                    'notSubmittable': True,
                    'type': 'string',
                    'title': 'ID'
                },
                '@type': {
                    'notSubmittable': True,
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'title': 'Type'
                },
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
                '@id': {
                    'notSubmittable': True,
                    'type': 'string',
                    'title': 'ID'
                },
                '@type': {
                    'notSubmittable': True,
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'title': 'Type'
                },
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


@pytest.fixture()
def testing_download_type():
    return {
        'name': 'TestingDownload',
        'item_type': 'testing_download',
        'schema': {
            'type': 'object',
            'properties': {
                '@id': {
                    'notSubmittable': True,
                    'type': 'string',
                    'title': 'ID'
                },
                '@type': {
                    'notSubmittable': True,
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'title': 'Type'
                },
                'attachment': {
                    'type': 'object',
                    'attachment': True,
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['image/png'],
                        }
                    }
                },
                'attachment2': {
                    'type': 'object',
                    'attachment': True,
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['image/png'],
                        }
                    }
                },
                'attachment3': {
                    'type': 'object',
                    'attachment': True,
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['application/json'],
                        }
                    }
                },
                'attachment4': {
                    'type': 'object',
                    'attachment': True,
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['application/json'],
                        }
                    }
                }
            }
        }
    }


@pytest.fixture()
def testing_item_type():
    return {
        'name': 'Item',
        'schema': {},
        'subtypes': [
            'TestingServerDefault',
            'TestingCustomEmbedSource',
            'TestingCustomEmbedTarget',
            'TestingPostPutPatch',
            'TestingDependencies',
            'TestingLinkTarget',
            'TestingLinkSource',
            'TestingSearchSchema',
            'TestingDownload',
            'TestingBadAccession',
            'TestingSearchSchemaSpecialFacets',
        ],
    }


@pytest.fixture
def test_config_item_search_config():
    return {
        'name': 'TestConfigItem',
        'facets': {'a': 'b'},
    }


@pytest.fixture
def testing_types(testing_search_schema_type, testing_post_put_patch_type, testing_search_schema_special_facets_type, testing_download_type, testing_item_type):
    return [
        testing_search_schema_type,
        testing_post_put_patch_type,
        testing_search_schema_special_facets_type,
        testing_download_type,
        testing_item_type,
    ]


@pytest.fixture
def testing_configs(test_config_item_search_config, testing_types):
    return [
        test_config_item_search_config,
    ] + [
        {
            'name': testing_type['name'],
            **testing_type.get('schema', {}),
        }
        for testing_type in testing_types
    ]
