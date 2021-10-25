import pytest


def test_searches_configs_config_init():
    from snosearch.configs import Config
    c = Config()
    assert isinstance(c, Config)


def test_searches_configs_terms_aggregation_config_init():
    from snosearch.configs import TermsAggregationConfig
    tac = TermsAggregationConfig()
    assert isinstance(tac, TermsAggregationConfig)


def test_searches_configs_exists_aggregation_config_init():
    from snosearch.configs import ExistsAggregationConfig
    eac = ExistsAggregationConfig()
    assert isinstance(eac, ExistsAggregationConfig)


def test_searches_configs_config_allowed_kwargs():
    from snosearch.configs import Config
    c = Config()
    assert c._allowed_kwargs == []
    c = Config(allowed_kwargs=['size'])
    assert c._allowed_kwargs == ['size']


def test_searches_configs_config_kwargs():
    from snosearch.configs import Config
    c = Config()
    assert c._kwargs == {}
    c = Config(other_thing='abc', something_else=True)
    assert c._kwargs == {'other_thing': 'abc', 'something_else': True}


def test_searches_configs_config_allowed_kwargs_and_kwargs():
    from snosearch.configs import Config
    c = Config(
        allowed_kwargs=['first_thing'],
        other_thing='abc',
        something_else=True
    )
    assert c._allowed_kwargs == ['first_thing']
    assert c._kwargs == {'other_thing': 'abc', 'something_else': True}


def test_searches_configs_config_filtered_kwargs():
    from snosearch.configs import Config
    c = Config()
    assert c._filtered_kwargs() == {}
    c = Config(
        allowed_kwargs=['first_thing'],
        other_thing='abc',
        something_else=True
    )
    assert c._filtered_kwargs() == {}
    c = Config(
        allowed_kwargs=['first_thing', 'other_thing'],
        other_thing='abc',
        something_else=True
    )
    assert c._filtered_kwargs() == {'other_thing': 'abc'}
    c = Config(
        allowed_kwargs=['first_thing', 'other_thing'],
        other_thing=None,
        something_else=True
    )
    assert c._filtered_kwargs() == {}


def test_searches_configs_config_iter():
    from snosearch.configs import Config
    c = Config(
        allowed_kwargs=['first_thing', 'other_thing'],
        other_thing='abc',
        something_else=True
    )
    assert {k: v for k, v in c.items()} == {'other_thing': 'abc'}


def test_searches_configs_config_len():
    from snosearch.configs import Config
    c = Config(
        allowed_kwargs=['first_thing', 'other_thing'],
        other_thing='abc',
        something_else=True
    )
    assert len(c) == 1


def test_searches_configs_config_getitem():
    from snosearch.configs import Config
    c = Config(
        allowed_kwargs=['first_thing', 'other_thing'],
        other_thing='abc',
        something_else=True
    )
    assert c['other_thing'] == 'abc'
    with pytest.raises(KeyError):
        c['nothing']


def test_searches_configs_terms_aggregation_config_allowed_kwargs():
    from snosearch.configs import TermsAggregationConfig
    from snosearch.defaults import DEFAULT_TERMS_AGGREGATION_KWARGS
    tac = TermsAggregationConfig()
    assert tac._allowed_kwargs == ['size', 'exclude', 'missing', 'include', 'aggs']
    tac = TermsAggregationConfig(allowed_kwargs=['size'])
    assert tac._allowed_kwargs == ['size']


def test_searches_configs_exists_aggregatin_config_allowed_kwargs():
    from snosearch.configs import ExistsAggregationConfig
    from snosearch.defaults import DEFAULT_TERMS_AGGREGATION_KWARGS
    eac = ExistsAggregationConfig()
    assert eac._allowed_kwargs == []
    eac = ExistsAggregationConfig(allowed_kwargs=['size'])
    assert eac._allowed_kwargs == ['size']


def test_searches_configs_terms_aggregation_config_pass_filtered_kwargs():
    from snosearch.configs import TermsAggregationConfig
    def return_kwargs(**kwargs):
        return kwargs
    kwargs = return_kwargs(**TermsAggregationConfig({}))
    assert kwargs == {}
    kwargs = return_kwargs(**TermsAggregationConfig(size=100))
    assert kwargs == {'size': 100}
    kwargs = return_kwargs(**TermsAggregationConfig(**{'size': 100}))
    assert kwargs == {'size': 100}
    kwargs = return_kwargs(
         **TermsAggregationConfig(
             size=100,
             exclude=None,
             missing='fake'
         )
     )
    assert kwargs == {'size': 100, 'missing': 'fake'}


def test_searches_configs_exists_aggregation_config_pass_filtered_kwargs():
    from snosearch.configs import ExistsAggregationConfig
    def return_kwargs(**kwargs):
        return kwargs
    kwargs = return_kwargs(**ExistsAggregationConfig({}))
    assert kwargs == {}
    e = ExistsAggregationConfig(size=100)
    kwargs = return_kwargs(**ExistsAggregationConfig(size=100))
    assert kwargs == {}
    kwargs = return_kwargs(
         **ExistsAggregationConfig(
             size=100,
             exclude=None,
             missing='fake'
         )
     )
    assert kwargs == {}


def test_searches_configs_sorted_tuple_map_init(dummy_request):
    from snosearch.configs import SortedTupleMap
    s = SortedTupleMap()
    assert isinstance(s, SortedTupleMap)


def test_searches_configs_sorted_tuple_map_convert_key_to_sorted_tuple(dummy_request):
    from snosearch.configs import SortedTupleMap
    s = SortedTupleMap()
    assert s._convert_key_to_sorted_tuple('Experiment') == ('Experiment',)
    assert s._convert_key_to_sorted_tuple(['File' ,'Experiment']) == ('Experiment', 'File')
    assert s._convert_key_to_sorted_tuple(('File' ,'Experiment')) == ('Experiment', 'File')


def test_searches_configs_sorted_tuple_map_add_drop_get_and_as_dict(dummy_request):
    from snosearch.configs import SortedTupleMap
    s = SortedTupleMap()
    s['x'] = ['y']
    assert s.as_dict() == {('x',): ['y']}
    s['x'].extend(['z', 'p'])
    assert s.as_dict() == {('x',): ['y', 'z', 'p']}
    s.drop('x')
    assert s.as_dict() == {}
    s.drop(('x',))
    assert s.as_dict() == {}
    s[['File', 'Experiment', 'QualityMetric']] = ['FileConfig', 'OtherConfig']
    assert s.get(('File', 'Experiment', 'QualityMetric')) == ['FileConfig', 'OtherConfig']
    s[['Experiment', 'QualityMetric', 'File']].extend([{'x', 'y'}])
    assert s.get(('File', 'Experiment', 'QualityMetric')) == ['FileConfig', 'OtherConfig', {'x', 'y'}]
    s.drop(['Experiment', 'QualityMetric', 'File'])
    assert s.get(('File', 'Experiment', 'QualityMetric')) is None
    assert s.get(('File', 'Experiment', 'QualityMetric'), default={}) == {}


def test_searches_configs_sorted_tuple_map_contains(dummy_request):
    from snosearch.configs import SortedTupleMap
    s = SortedTupleMap()
    assert 'x' not in s
    s['x'] = [1, 2, 3]
    assert 'x' in s
    assert ('x',) in s
    assert ['x'] in s
    assert ['x', 'y', 'z'] not in s
    s[('y', 'z', 'x')] = 'abc'
    assert ['x', 'y', 'z'] in s


def test_searches_configs_search_config_registry(dummy_request):
    from snosearch.interfaces import SEARCH_CONFIG
    config = dummy_request.registry[SEARCH_CONFIG].get('TestingSearchSchema')
    assert list(config.facets.items()) == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]
    assert list(config.boost_values.items()) == [
        ('accession', 1.0), ('status', 1.0),
        ('label', 1.0)
    ]
    assert list(config.facets.items()) == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]
    original_kwargs = config._kwargs
    config._kwargs = original_kwargs.copy()
    with pytest.raises(AttributeError):
        config.fake_field
    config._allowed_kwargs.append('fake_field')
    config.update(fake_field={'x': 1, 'y': [1, 2]})
    assert config.fake_field == {'x': 1, 'y': [1, 2]}
    config.update(**{'facets': {'new': 'values'}})
    assert config.facets == {'new': 'values'}
    config._kwargs = original_kwargs


def test_searches_configs_search_config_registry_add_aliases_and_defaults(dummy_request):
    from snosearch.interfaces import SEARCH_CONFIG
    search_registry = dummy_request.registry[SEARCH_CONFIG]
    config = search_registry.get('TestingSearchSchema')
    assert list(config.facets.items()) == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]
    aliases = {
        'SomeAlias': ['AliasesItem1', 'AliasesItem2']
    }
    defaults = {
        'SomeItem': ['DefaultConfig']
    }
    search_registry.add_aliases(aliases)
    assert search_registry.aliases.as_dict() == {
        ('SomeAlias',): ['AliasesItem1', 'AliasesItem2']
    }
    search_registry.add_defaults(defaults)
    assert search_registry.defaults.as_dict() == {
        ('SomeItem',): ['DefaultConfig']
    }
    search_registry.add_aliases({('AnotherAlias', 'Multkey', 'AndSorted'): ['XYZ']})
    assert search_registry.aliases.as_dict() == {
        ('AndSorted', 'AnotherAlias', 'Multkey'): ['XYZ'],
        ('SomeAlias',): ['AliasesItem1', 'AliasesItem2']
    }


def test_searches_configs_search_config_registry_resolve_config_names(dummy_request):
    from snosearch.interfaces import SEARCH_CONFIG
    search_registry = dummy_request.registry[SEARCH_CONFIG]
    registry = search_registry.registry
    config_names = search_registry._resolve_config_names(['TestingSearchSchema'])
    assert len(config_names) == 1
    assert config_names == ['TestingSearchSchema']
    search_registry.add_aliases(
        {
            'AllConfigs': ['TestingSearchSchema']
        }
    )
    config_names = search_registry._resolve_config_names(['AllConfigs'])
    assert len(config_names) == 1
    assert config_names == ['TestingSearchSchema']
    search_registry.add_aliases(
        {
            'AllConfigs': ['TestingSearchSchema', 'TestingSearchSchema']
        }
    )
    config_names = search_registry._resolve_config_names(['AllConfigs'])
    assert len(config_names) == 2
    assert config_names == ['TestingSearchSchema', 'TestingSearchSchema']
    search_registry.add_defaults(
        {
            'TestingSearchSchema': ['SomeOtherConfig']
        }
    )
    config_names = search_registry._resolve_config_names(['AllConfigs'])
    assert len(config_names) == 2
    assert config_names == ['SomeOtherConfig', 'SomeOtherConfig']
    config_names = search_registry._resolve_config_names(['AllConfigs'], use_defaults=False)
    assert len(config_names) == 2
    assert config_names == ['TestingSearchSchema', 'TestingSearchSchema']
    search_registry.clear()
    search_registry.registry = registry


def test_searches_configs_search_config_registry_get_configs_by_names(dummy_request):
    from snosearch.interfaces import SEARCH_CONFIG
    search_registry = dummy_request.registry[SEARCH_CONFIG]
    configs = search_registry.get_configs_by_names(['TestingSearchSchema'])
    assert len(configs) == 1
    assert list(configs[0].facets.items()) == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]


def test_searches_configs_search_config_registry_flatten_single_values():
    from snosearch.configs import flatten_single_values
    assert flatten_single_values(('abc',)) == 'abc'
    assert flatten_single_values(('abc', 'xyz')) == ('abc', 'xyz')


def test_searches_configs_search_config_registry_as_dict(dummy_request):
    from snosearch.interfaces import SEARCH_CONFIG
    search_registry = dummy_request.registry[SEARCH_CONFIG]
    expected = {
        'TestConfigItem': {
            'facets': {
                'a': 'b'
            }
        },
        'TestingSearchSchema': {
            'facet_groups': [
                {
                    'title': 'Test group',
                    'facet_fields': ['status', 'name']
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
        'TestingPostPutPatch': {},
        'TestingSearchSchemaSpecialFacets': {
            'facets': {
                'status': {
                    'title': 'Status',
                    'type': 'exists'
                },
                'read_count': {
                    'title': 'Read count range',
                    'type': 'stats'
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
            },
            'matrix': {
                'x': {
                    'group_by': 'accession'
                },
                'y': {
                    'group_by': ['status', 'name']
                }
            }
        },
        'TestingDownload': {
            'columns': {
                'attachment': {
                    'title': 'Attachment'
                }
            }
        },
        'Item': {}
    }
    actual = search_registry.as_dict()
    assert actual == expected


def test_searches_configs_search_config_can_update():
    from snosearch.configs import SearchConfig
    from snosearch.configs import SearchConfigRegistry
    registry = SearchConfigRegistry()
    config = SearchConfig(
        'my-custom-config',
        {
            'facets': {'a': 'b'},
            'columns': ['x', 'y']
        }
    )
    assert list(config.items()) == [
        ('facets', {'a': 'b'}),
        ('columns', ['x', 'y'])
    ]
    registry.add(config)
    empty = SearchConfig('empty', {})
    assert registry.get('my-custom-config', empty).facets == {'a': 'b'}
    assert registry.get('my-custom-config', empty).columns == ['x', 'y']
    assert registry.get('my-custom-config', empty).boost_values == {}
    related_config = SearchConfig(
        'my-custom-config',
        {
            'facets': {'c': 'd'},
            'boost_values': {'t': 'z'}
        }
    )
    registry.update(related_config)
    assert registry.get('my-custom-config', empty).facets == {'c': 'd'}
    assert registry.get('my-custom-config', empty).columns == ['x', 'y']
    assert registry.get('my-custom-config', empty).boost_values == {'t': 'z'}


def test_searches_configs_to_camel_case():
    from snosearch.configs import to_camel_case
    assert to_camel_case('my_custom_name') == 'MyCustomName'
    assert to_camel_case('aThing') == 'Athing'
    assert to_camel_case('facets') == 'Facets'
    assert to_camel_case('') == ''


def test_searches_configs_make_name_for_piece():
    from snosearch.configs import make_name_for_piece
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
        }
    assert make_name_for_piece(MyCustomItem, 'facets') == 'MyCustomItemFacets'
    assert make_name_for_piece(MyCustomItem, 'facet_groups') == 'MyCustomItemFacetGroups'


def test_searches_configs_extract_piece_from_item_pieces():
    from snosearch.configs import extract_piece_from_item_pieces
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
        }
    assert extract_piece_from_item_pieces(MyCustomItem.schema, 'facets') == {
        'facets': {'a': 'b'},
    }
    assert extract_piece_from_item_pieces(MyCustomItem.schema, 'columns') == {
        'columns': ['x', 'y'],
    }
    assert extract_piece_from_item_pieces(MyCustomItem.schema, 'nothing') == {}


def test_searches_configs_search_config_values_from_item():
    from snosearch.configs import SearchConfig
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
        }
    values = SearchConfig._values_from_item(MyCustomItem)
    assert values == MyCustomItem.schema
    class AbstractItem:
        schema = None
    values = SearchConfig._values_from_item(AbstractItem)
    assert values is None


def test_searches_configs_search_config_from_item():
    from snosearch.configs import SearchConfig
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
            'other': {'not': 'this'},
        }
    mci = MyCustomItem
    config = SearchConfig.from_item(mci)
    assert config.name == 'MyCustomItem'
    assert config._kwargs == {
        'facets': {'a': 'b'},
        'columns': ['x', 'y'],
    }


def test_searches_configs_search_config_from_item_piece():
    from snosearch.configs import SearchConfig
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
            'other': {'not': 'this'},
            'facet_groups': ['t', 'z'],
        }
    mci = MyCustomItem
    config = SearchConfig.from_item_piece(mci, 'columns')
    assert config.name == 'MyCustomItemColumns'
    assert config._kwargs == {
        'columns': ['x', 'y'],
    }
    assert len(config) == 1
    config = SearchConfig.from_item_piece(mci, 'facets')
    assert config.name == 'MyCustomItemFacets'
    assert config._kwargs == {
        'facets': {'a': 'b'},
    }
    assert len(config) == 1
    config = SearchConfig.from_item_piece(mci, 'facet_groups')
    assert config.name == 'MyCustomItemFacetGroups'
    assert config._kwargs == {
        'facet_groups': ['t', 'z'],
    }
    assert len(config) == 1
    config = SearchConfig.from_item_piece(mci, 'other')
    assert config.name == 'MyCustomItemOther'
    assert config._kwargs == {}
    class AbstractItem:
        schema = None
    config = SearchConfig.from_item_piece(AbstractItem, 'facets')
    assert len(config) == 0


def test_searches_configs_search_config_registry_register_from_item():
    from snosearch.configs import SearchConfig
    from snosearch.configs import SearchConfigRegistry
    registry = SearchConfigRegistry()
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
            'other': {'not': 'this'},
            'facet_groups': ['t', 'z'],
        }
    registry.register_from_item(MyCustomItem)
    assert len(registry.registry.as_dict()) == 1
    config = registry.get('MyCustomItem')
    assert config.name == 'MyCustomItem'
    assert config._kwargs == {
        'facets': {'a': 'b'},
        'columns': ['x', 'y'],
        'facet_groups': ['t', 'z']
    }
    assert len(config) == 3


def test_searches_configs_search_config_registry_register_pieces_from_item():
    from snosearch.configs import SearchConfig
    from snosearch.configs import SearchConfigRegistry
    registry = SearchConfigRegistry()
    class MyCustomItem:
        schema = {
            'facets': {'a': 'b'},
            'columns': ['x', 'y'],
            'other': {'not': 'this'},
            'facet_groups': ['t', 'z'],
        }
    registry.register_pieces_from_item(MyCustomItem)
    assert len(registry.registry.as_dict()) == 3
    registry.register_from_item(MyCustomItem)
    assert len(registry.registry.as_dict()) == 4
    config = registry.get('MyCustomItemFacets')
    assert config.name == 'MyCustomItemFacets'
    assert config._kwargs == {
        'facets': {'a': 'b'},
    }
    assert len(config) == 1
    config = registry.get('MyCustomItemFacetGroups')
    assert config.name == 'MyCustomItemFacetGroups'
    assert config._kwargs == {
        'facet_groups': ['t', 'z'],
    }
    assert len(config) == 1
    config = registry.get('MyCustomItemColumns')
    assert config.name == 'MyCustomItemColumns'
    assert config._kwargs == {
        'columns': ['x', 'y'],
    }
    config = registry.get('MyCustomItem')
    assert config.name == 'MyCustomItem'
    assert config._kwargs == {
        'facets': {'a': 'b'},
        'columns': ['x', 'y'],
        'facet_groups': ['t', 'z']
    }
    assert len(config) == 3
    class TypeWithNoPieces:
        schema = {}
    registry = SearchConfigRegistry()
    assert len(registry.registry.as_dict()) == 0
    registry.register_pieces_from_item(TypeWithNoPieces)
    assert len(registry.registry.as_dict()) == 0
