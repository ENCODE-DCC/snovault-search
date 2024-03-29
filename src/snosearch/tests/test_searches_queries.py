import pytest


integrations = [
    'pyramid',
    'flask',
]


@pytest.fixture
def params_parser(request, pyramid_dummy_request, flask_dummy_request):
    if hasattr(request, 'param') and request.param == 'flask':
        dummy_request = flask_dummy_request
    else:
        dummy_request = pyramid_dummy_request
    from snosearch.parsers import ParamsParser
    from snosearch.interfaces import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&assembly=GRCh38&biosample_ontology.classification=primary+cell'
        '&target.label=H3K27me3&biosample_ontology.classification%21=cell+line'
        '&biosample_ontology.term_name%21=naive+thymus-derived+CD4-positive%2C+alpha-beta+T+cell'
        '&limit=10&status=released&searchTerm=chip-seq&sort=date_created&sort=-files.file_size'
        '&field=@id&field=accession'
    )
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch()
    return ParamsParser(dummy_request)


@pytest.fixture
def params_parser_snovault_types(request, pyramid_dummy_request, flask_dummy_request):
    if hasattr(request, 'param') and request.param == 'flask':
        dummy_request = flask_dummy_request
    else:
        dummy_requuest = pyramid_dummy_request
    dummy_request = flask_dummy_request
    from snosearch.parsers import ParamsParser
    from snosearch.interfaces import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession'
    )
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch()
    return ParamsParser(dummy_request)


def test_searches_queries_abstract_query_factory_init():
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory({})
    assert isinstance(aq, AbstractQueryFactory)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_or_create_search(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    from elasticsearch_dsl import Search
    aq = AbstractQueryFactory(params_parser)
    assert aq.search is None
    s = aq._get_or_create_search()
    assert s is aq.search
    assert isinstance(aq.search, Search)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_client(params_parser):
    from snosearch.queries import AbstractQueryFactory
    from elasticsearch import Elasticsearch
    aq = AbstractQueryFactory(params_parser, client={'a': 'client'})
    c = aq._get_client()
    assert c == {'a': 'client'}
    aq = AbstractQueryFactory(params_parser)
    c = aq._get_client()
    assert isinstance(c, Elasticsearch)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_index(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.interfaces import RESOURCES_INDEX
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == RESOURCES_INDEX


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_index_variations(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == ['testing_search_schema']
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&type=TestingPostPutPatch&status=released'
        '&limit=10&field=@id&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == ['testing_search_schema', 'testing_post_put_patch']
    dummy_request.environ['QUERY_STRING'] = (
        'type=Item&status=released'
        '&limit=10&field=@id&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == ['snovault-resources']
    dummy_request.environ['QUERY_STRING'] = (
        'type=Item&type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == ['snovault-resources']
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&limit=10'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_index() == ['snovault-resources']
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&limit=10'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema',
            'TestingPostPutPatch',
            'TestingDownload'
        ]
    )
    assert aq._get_index() == [
        'snovault-resources'
    ]
    dummy_request.environ['QUERY_STRING'] = (
        '&type=Item&status=released&limit=10'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema',
            'TestingPostPutPatch',
            'TestingDownload'
        ]
    )
    assert aq._get_index() == ['snovault-resources']
    dummy_request.environ['QUERY_STRING'] = (
        '&type=TestingSearchSchema&status=released&limit=10'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema',
            'TestingPostPutPatch',
            'TestingDownload'
        ]
    )
    assert aq._get_index() == ['testing_search_schema']


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_wildcard_in_item_types(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert not aq._wildcard_in_item_types([('type', 'Experiment'), ('type!', 'File')])
    assert aq._wildcard_in_item_types([('type', 'Experiment'), ('type', '*')])
    assert aq._wildcard_in_item_types([('type', '*')])


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_item_types(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    item_types = aq._get_item_types()
    assert item_types == [
        ('type', 'Experiment')
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_principals(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    principals = aq._get_principals()
    assert principals == ['system.Everyone']


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_registered_types(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    registered_types = aq._get_registered_types()
    assert isinstance(registered_types, dict)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_search_config_registry(params_parser_snovault_types):
    from snosearch.configs import SearchConfigRegistry
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    search_config_registry = aq._get_search_config_registry()
    assert isinstance(search_config_registry, SearchConfigRegistry)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_factory_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    factory = aq._get_factory_for_item_type('TestingSearchSchema')
    assert factory.item_type == 'testing_search_schema'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_schema_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    schema = aq._get_schema_for_item_type('TestingSearchSchema')
    assert isinstance(schema, dict)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_search_config_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    aq = AbstractQueryFactory(params_parser_snovault_types)
    config = aq._get_search_config_for_item_type('TestingSearchSchema')
    assert isinstance(config, SearchConfig)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_search_configs_by_names(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    aq = AbstractQueryFactory(params_parser_snovault_types)
    configs = aq._get_search_configs_by_names(['TestingSearchSchema'])
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_properties_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    actual = aq._get_properties_for_item_type('TestingSearchSchema')
    expected = {
        '@id': {
            'notSubmittable': True,
            'type': 'string',
            'title': 'ID'
        },
        'status': {
            'type': 'string'
        },
        'accession': {
            'type': 'string',
            'description': '',
            'format': 'accession',
            'permission': 'import_items',
            'title': 'Accession'},
        '@type': {
            'notSubmittable': True,
            'type': 'array',
            'items': {
                'type': 'string'
            },
            'title': 'Type'
        },
        'uuid': {
            'permission': 'import_items',
            'format': 'uuid',
            'type': 'string',
            'description': 'Unique identifier',
            'title': 'UUID',
            'requestMethod': 'POST'
        },
        'name': {
            'uniqueKey': True,
            'type': 'string'
        },
        'label': {
            'type': 'string'
        }
    }
    assert set(actual.keys()) == set(expected.keys())
    assert actual['accession']['title'] == 'Accession'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_subtypes_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    subtypes = aq._get_subtypes_for_item_type('TestingSearchSchema')
    assert subtypes == ['TestingSearchSchema']
    subtypes = aq._get_subtypes_for_item_type('Item')
    assert sorted(subtypes) == sorted([
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
        'TestingSearchSchemaSpecialFacets'
    ])


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_name_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._get_name_for_item_type('TestingSearchSchema') == 'TestingSearchSchema'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_collection_name_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._get_collection_name_for_item_type('TestingSearchSchema') == 'testing_search_schema'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_facets_from_configs(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    facets = aq._get_facets_from_configs()
    expected = [
        ('name', {'title': 'Name'}),
        ('status', {'title': 'Status', 'open_on_load': True})
    ]
    assert all(e in facets for e in expected)
    assert len(expected) == len(facets)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_base_columns(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._get_base_columns() == {'@id': {'title': 'ID'}}


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_columns_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._get_default_columns_for_item_type('TestingSearchSchema') == {
        'accession': {'title': 'Accession'},
        'name': {'title': 'Name'}
    }
    assert aq._get_default_columns_for_item_type('TestingPostPutPatch') == {
        'accession': {'title': 'Accession'}
    }
    assert aq._get_default_columns_for_item_type('TestingDownload') == {}


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_columns_for_item_type(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    columns = aq._get_columns_for_item_type('TestingSearchSchema').items()
    expected = [
        ('accession', {'title': 'Accession'}),
        ('status', {'title': 'Status'})
    ]
    assert all(e in columns for e in expected)
    assert len(expected) == len(columns)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_columns_for_item_types(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_for_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingPostPutPatch'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_for_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'}
    }


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_columns_from_configs_or_item_types(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    from snosearch.interfaces import SEARCH_CONFIG
    search_registry = dummy_request.registry[SEARCH_CONFIG]
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_from_configs_or_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingPostPutPatch'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_from_configs_or_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'}
    }
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingPostPutPatch'
        '&config=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_from_configs_or_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingPostPutPatch'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_from_configs_or_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }
    defaults = {
        ('TestingPostPutPatch', 'TestingSearchSchema'): ['TestingDownload']
    }
    search_registry.add_defaults(defaults)
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingPostPutPatch'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    columns = aq._get_columns_from_configs_or_item_types()
    assert dict(columns) == {
        '@id': {'title': 'ID'},
        'attachment': {'title': 'Attachment'},
    }


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_extract_columns_from_configs(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_individual_keys()
    columns = aq._extract_columns_from_configs(configs)
    assert columns == {
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_extract_facets_from_configs(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_individual_keys()
    facets = aq._extract_facets_from_configs(configs)
    assert facets == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_extract_matrix_from_configs(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_param_values_or_item_types_as_combined_key()
    assert not aq._extract_matrix_from_configs(configs)
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchemaSpecialFacets'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_config_param_values()
    assert not aq._extract_matrix_from_configs(configs)
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
        '&config=TestingSearchSchema&config=TestingSearchSchemaSpecialFacets'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_param_values_or_item_types_as_combined_key()
    assert aq._extract_matrix_from_configs(configs) == {
        'x': {
            'group_by': 'accession'
        },
        'y': {
            'group_by': ['status', 'name']
        }
    }


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_invalid_item_types(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    item_types = ['TestingSearchSchema']
    invalid_types = aq._get_invalid_item_types(item_types)
    assert not invalid_types


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_validate_item_types(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    item_types = ['TestingSearchSchema']
    aq.validate_item_types(item_types)
    item_types = ['Sno']
    with pytest.raises(HTTPBadRequest):
        aq.validate_item_types(item_types)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_normalize_item_types(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    item_types = ['TestingSearchSchema']
    normalized_item_types = aq._normalize_item_types(item_types=item_types)
    assert normalized_item_types == item_types
    item_types = ['testing_search_schema']
    normalized_item_types = aq._normalize_item_types(item_types=item_types)
    assert normalized_item_types == ['TestingSearchSchema']


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_collection_names_for_item_types(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._get_collection_names_for_item_types(['TestingSearchSchema']) == ['testing_search_schema']
    assert aq._get_collection_names_for_item_types(['Item']) == []
    assert aq._get_collection_names_for_item_types(
        [
            'TestingSearchSchema',
            'Item',
            'TestingPostPutPatch'
        ]
    ) == ['testing_search_schema', 'testing_post_put_patch']


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_escape_regex_slashes(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._escape_regex_slashes('ctcf') == 'ctcf'
    assert aq._escape_regex_slashes(
        '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    ) == '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    assert aq._escape_regex_slashes(
        '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (@type:File)'
    ) == '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (@type:File)'
    assert aq._escape_regex_slashes(
        'Wnt/β-catenin'
    ) == 'Wnt\\/β-catenin'
    assert aq._escape_regex_slashes(
        '/targets/H3K9me3-human/'
    ) == '\\/targets\\/H3K9me3-human\\/'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_escape_fuzzy_tilde(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._escape_fuzzy_tilde('ctcf') == 'ctcf'
    assert aq._escape_fuzzy_tilde(
        '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    ) == '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    assert aq._escape_fuzzy_tilde(
        '(ctcf) AND (myers)~ AND NOT (~snyder or pacha) AND (@type:File)'
    ) == '(ctcf) AND (myers)\\~ AND NOT (\\~snyder or pacha) AND (@type:File)'
    assert aq._escape_fuzzy_tilde(
        'Wnt/β-~catenin'
    ) == 'Wnt/β-\\~catenin'
    assert aq._escape_fuzzy_tilde(
        '/targets/H3K9me3-human/~'
    ) == '/targets/H3K9me3-human/\\~'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_escape_boost_caret(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._escape_boost_caret('ctcf') == 'ctcf'
    assert aq._escape_boost_caret(
        'eclip^'
    ) == 'eclip\\^'
    assert aq._escape_boost_caret(
        '(ctcf) AND (my^ers)^'
    ) == '(ctcf) AND (my\\^ers)\\^'
    assert aq._escape_boost_caret(
        '^^Wnt/β-catenin'
    ) == '\\^\\^Wnt/β-catenin'
    assert aq._escape_boost_caret(
        '/targets/H3K9me3-human/'
    ) == '/targets/H3K9me3-human/'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_escape_reserved_query_string_characters(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._escape_reserved_query_string_characters('ctcf') == 'ctcf'
    assert aq._escape_reserved_query_string_characters(
        '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    ) == '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    assert aq._escape_reserved_query_string_characters(
        '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (@type:File)'
    ) == '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (@type:File)'
    assert aq._escape_reserved_query_string_characters(
        'Wnt/β-catenin'
    ) == 'Wnt\\/β-catenin'
    assert aq._escape_reserved_query_string_characters(
        '/targets/H3K9me3-human/'
    ) == '\\/targets\\/H3K9me3-human\\/'
    assert aq._escape_reserved_query_string_characters(
        '(ctcf)~ AND (myers) AND NOT^ (snyder or pacha) AND (@type:File)'
    ) == '(ctcf)\\~ AND (myers) AND NOT\\^ (snyder or pacha) AND (@type:File)'
    assert aq._escape_reserved_query_string_characters(
        '^Wnt/β-catenin~~'
    ) == '\\^Wnt\\/β-catenin\\~\\~'
    assert aq._escape_reserved_query_string_characters(
        '/targets/H3K9me3-human~/'
    ) == '\\/targets\\/H3K9me3-human\\~\\/'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_validated_query_string_query(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    aq = AbstractQueryFactory(params_parser_snovault_types)
    assert aq._validated_query_string_query('ctcf') == 'ctcf'
    assert aq._validated_query_string_query(
        '@type:Experiment date_created:[01-01-2018 TO 01-02-2018]'
    ) == 'embedded.@type:Experiment embedded.date_created:[01-01-2018 TO 01-02-2018]'
    assert aq._validated_query_string_query(
        '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (@type:File)'
    ) == '(ctcf) AND (myers) AND NOT (snyder or pacha) AND (embedded.@type:File)'
    assert aq._validated_query_string_query(
        'Wnt\\/β-catenin'
    ) == 'Wnt\\/β-catenin'
    special_chars = '&& || > < ! ( ) { } [ ] ^ " ~ \\ :'
    for c in special_chars.split(' '):
        with pytest.raises(HTTPBadRequest):
            aq._validated_query_string_query(c)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_item_types(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'Snowflake',
            'Pancake'
        ]
    )
    default_item_types = aq._get_default_item_types()
    assert default_item_types == [
        ('type', 'Snowflake'),
        ('type', 'Pancake')
    ]
    aq = AbstractQueryFactory(
        params_parser,
    )
    default_item_types = aq._get_default_item_types()
    assert not default_item_types


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_item_types_mode_picker(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser
    )
    default_item_types = aq._get_default_item_types()
    assert default_item_types == [('type', 'Item')]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_facets(params_parser):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.testing import DummyResource
    params_parser._request.context = DummyResource()
    aq = AbstractQueryFactory(
        params_parser,
        default_facets=[
            ('type', {'title': 'Data Type', 'exclude': ['Item']}),
            ('file_format', {'title': 'File Format'}),
        ]
    )
    default_facets = aq._get_default_facets()
    assert default_facets == [
        ('type', {'title': 'Data Type', 'exclude': ['Item']}),
        ('file_format', {'title': 'File Format'}),
    ]
    aq = AbstractQueryFactory(
        params_parser
    )
    assert aq._get_default_facets() == [
        ('type', {'title': 'Data Type', 'exclude': ['Item']})
    ]
    assert aq._get_audit_facets() == [
        ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
        ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
        ('audit.WARNING.category', {'title': 'Audit category: WARNING'})
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_facets_from_configs(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    facets = aq._get_facets_from_configs()
    assert facets == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema&config=TestConfigItem'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    facets = aq._get_facets_from_configs()
    assert facets == [
        ('a', 'b')
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema&config=TestingSearchSchemaSpecialFacets'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    facets = aq._get_facets_from_configs()
    assert facets == [
        ('status', {'title': 'Status', 'type': 'exists'}),
        ('read_count', {'title': 'Read count range', 'type': 'stats'}),
        ('name', {'title': 'Name'})
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema&config=TestingPostPutPatch'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    facets = aq._get_facets_from_configs()
    assert facets == [
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_and_maybe_item_facets(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.testing import DummyResource
    params_parser_snovault_types._request.context = DummyResource()
    aq = AbstractQueryFactory(
        params_parser_snovault_types
    )
    expected = [
        ('type', {'title': 'Data Type', 'exclude': ['Item']}),
        ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
        ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
        ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
        ('status', {'title': 'Status', 'open_on_load': True}),
        ('name', {'title': 'Name'})
    ]
    actual = aq._get_default_and_maybe_item_facets()
    assert all(e in actual for e in expected)


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_query_string_query(params_parser, dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    search_terms = aq._get_query_string_query()
    assert search_terms is None
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=object&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_query_string_query() is None
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&advancedQuery=cherry'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_query_string_query() == '(cherry)'
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&advancedQuery=cherry'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_query_string_query() == '(cherry)'
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&advancedQuery=@type:Experiment date_created:[01-01-2018 TO 01-02-2018'
        '&searchTerm=ctcf'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_query_string_query() == '(@type:Experiment date_created:[01-01-2018 TO 01-02-2018)'


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_simple_query_string_query(params_parser, dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    search_terms = aq._get_simple_query_string_query()
    assert search_terms == '(chip-seq)'
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=object&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_simple_query_string_query() is None
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&searchTerm=cherry'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_simple_query_string_query() == '(cherry)'
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&advancedQuery=cherry'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_simple_query_string_query() is None
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&advancedQuery=@type:Experiment date_created:[01-01-2018 TO 01-02-2018'
        '&searchTerm=ctcf'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_simple_query_string_query() == '(ctcf)'


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_reserved_keys(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'Snowflake',
            'Pancake'
        ],
        reserved_keys=[
            'searchTerm',
            'limit',
        ],
    )
    reserved_keys = aq._get_reserved_keys()
    assert reserved_keys == [
        'searchTerm',
        'limit',
    ]
    filters = aq._get_filters()
    assert filters == [
        ('type', 'Experiment'),
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('assembly', 'GRCh38'),
        ('biosample_ontology.classification', 'primary cell'),
        ('target.label', 'H3K27me3'),
        ('biosample_ontology.classification!', 'cell line'),
        ('biosample_ontology.term_name!', 'naive thymus-derived CD4-positive, alpha-beta T cell'),
        ('status', 'released'),
        ('sort', 'date_created'),
        ('sort', '-files.file_size'),
        ('field', '@id'),
        ('field', 'accession')
    ]
    aq = AbstractQueryFactory(
        params_parser,
    )
    reserved_keys = aq._get_reserved_keys()
    assert reserved_keys == [
        'type',
        'limit',
        'mode',
        'annotation',
        'format',
        'frame',
        'datastore',
        'field',
        'region',
        'genome',
        'sort',
        'from',
        'referrer',
        'filterresponse',
        'remove',
        'cart',
        'debug',
        'config',
        'searchTerm',
        'advancedQuery'
    ]
    filters = aq._get_filters()
    assert filters == [
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('assembly', 'GRCh38'),
        ('biosample_ontology.classification', 'primary cell'),
        ('target.label', 'H3K27me3'),
        ('biosample_ontology.classification!', 'cell line'),
        ('biosample_ontology.term_name!', 'naive thymus-derived CD4-positive, alpha-beta T cell'),
        ('status', 'released')
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_filters(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    filters = aq._get_filters()
    assert filters == [
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('assembly', 'GRCh38'),
        ('biosample_ontology.classification', 'primary cell'),
        ('target.label', 'H3K27me3'),
        ('biosample_ontology.classification!', 'cell line'),
        ('biosample_ontology.term_name!', 'naive thymus-derived CD4-positive, alpha-beta T cell'),
        ('status', 'released')
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_post_filters(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_post_filters() == [
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('assembly', 'GRCh38'),
        ('biosample_ontology.classification', 'primary cell'),
        ('target.label', 'H3K27me3'),
        ('biosample_ontology.classification!', 'cell line'),
        ('biosample_ontology.term_name!', 'naive thymus-derived CD4-positive, alpha-beta T cell'),
        ('status', 'released'),
        ('type', 'Experiment')
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_should_add_default_sort(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&limit=50&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._should_add_default_sort()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&searchTerm=ctcf'
        '&limit=10&limit=50&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_add_default_sort()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&advancedQuery=ctcf'
        '&limit=10&limit=50&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_add_default_sort()


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_sort(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&limit=50&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_default_sort() == [
        {'embedded.date_created': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.label': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.uuid': {'order': 'desc', 'unmapped_type': 'keyword'}}
    ]
    aq = AbstractQueryFactory(
        params_parser,
        default_sort=[
            '-expression.tpm',
            '-gene.symbol',
            'file.@id',
        ],
    )
    assert aq._get_default_sort() == [
        {'embedded.expression.tpm': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.gene.symbol': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.file.@id': {'order': 'asc', 'unmapped_type': 'keyword'}}
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_sort(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    sort_by = aq._get_sort()
    assert sort_by == [
        {'embedded.date_created': {'order': 'asc', 'unmapped_type': 'keyword'}},
        {'embedded.files.file_size': {'order': 'desc', 'unmapped_type': 'keyword'}}
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_sort_key(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._make_sort_key('status') == 'embedded.status'
    assert aq._make_sort_key('internal_warning', prefix='audit.') == 'audit.internal_warning'


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_sort_value(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._make_sort_value('desc') == {'order': 'desc', 'unmapped_type': 'keyword'}
    assert aq._make_sort_value('asc') == {'order': 'asc', 'unmapped_type': 'keyword'}


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_sort_key_and_value(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._make_sort_key_and_value('status') == {'embedded.status': {'order': 'asc', 'unmapped_type': 'keyword'}}
    assert aq._make_sort_key_and_value('-file_type') == {'embedded.file_type': {'order': 'desc', 'unmapped_type': 'keyword'}}


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_one_value(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=10&sort=color&field=@id&mode=picker&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    value = aq.params_parser.get_one_value(
        params=aq._get_from()
    )
    assert value == '10'
    value = aq.params_parser.get_one_value(
        params=[]
    )
    assert not value


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_assert_one_or_none(dummy_request):
    from pyramid.httpexceptions import HTTPBadRequest
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&limit=50&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    with pytest.raises(HTTPBadRequest):
        aq._get_mode()
    with pytest.raises(HTTPBadRequest):
        aq._get_limit()


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_from(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=300'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    from_ = aq.params_parser.param_values_to_list(aq._get_from())
    assert from_ == [
        '300'
    ]


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_from(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=300'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    default_from = aq._get_default_from()
    assert default_from == [('from', 0)]


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_from_value_as_int(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_from_value_as_int() == 0
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=50'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_from_value_as_int() == 50
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=blah'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_from_value_as_int() == 0
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=0'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_from_value_as_int() == 0


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_limit(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    limit = aq.params_parser.param_values_to_list(aq._get_limit())
    assert limit == [
        '10'
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=0'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    limit = aq.params_parser.param_values_to_list(aq._get_limit())
    assert limit == ['0']


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_default_limit(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    default_limit = aq._get_default_limit()
    assert default_limit == [('limit', 25)]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_max_result_window(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    max_result_window = aq._get_max_result_window()
    assert max_result_window == 9999
    aq = AbstractQueryFactory(
        params_parser,
        max_result_window=99999,
    )
    max_result_window = aq._get_max_result_window()
    assert max_result_window == 99999



@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_scan_size(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    scan_size = aq._get_scan_size()
    assert scan_size == 1000
    aq = AbstractQueryFactory(
        params_parser,
        scan_size=200000,
    )
    scan_size = aq._get_scan_size()
    assert scan_size == 200000


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_limit_value(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_limit_value()
    assert limit == 10
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=0'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_limit_value()
    assert limit == 0


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_limit_value_as_int(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_limit_value_as_int() == 10
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=30000'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_limit_value_as_int() == 30000
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=blah'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_limit_value_as_int() == 25
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_limit_value_as_int() == 25
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=0'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_limit_value_as_int() == 0


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_limit_is_all(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_all()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=all&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._limit_is_all()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=blah&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_all()


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_limit_is_over_maximum_window(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=all&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=1000&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10000&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(
        dummy_request
    )
    aq = AbstractQueryFactory(
        params_parser,
        max_result_window=10000,
    )
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=100000&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=blah&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=9&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        max_result_window=10,
    )
    assert not aq._limit_is_over_maximum_window()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=11&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        max_result_window=10,
    )
    assert aq._limit_is_over_maximum_window()


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_should_scan_over_results(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_scan_over_results()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=100000&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._should_scan_over_results()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=all&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._should_scan_over_results()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=blah&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_scan_over_results()


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_should_search_over_all_indices(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_search_over_all_indices()
    dummy_request.environ['QUERY_STRING'] = (
        'type=Item&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._should_search_over_all_indices()
    dummy_request.environ['QUERY_STRING'] = (
        'type=Item&type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._should_search_over_all_indices()
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingPostPutPatch&type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert not aq._should_search_over_all_indices()


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_bounded_limit_value_or_default(params_parser, dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_bounded_limit_value_or_default()
    assert limit == 10
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=25&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_bounded_limit_value_or_default()
    assert limit == 25
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=all&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_bounded_limit_value_or_default()
    assert limit == 0
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=100000&field=@id&mode=picker&mode=chair&field=accession'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    limit = aq._get_bounded_limit_value_or_default()
    assert limit == 0


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_frame(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    from pyramid.exceptions import HTTPBadRequest
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=object&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_frame() == [('frame', 'object')]
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=embedded&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_frame() == [('frame', 'embedded')]
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=embedded&frame=object'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    with pytest.raises(HTTPBadRequest):
         aq._get_frame()


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_frame_value(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=object&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_frame_value() == 'object'
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_frame_value() is None


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_search_fields(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    search_fields = aq._get_search_fields()
    assert search_fields == ['_all']
    aq = AbstractQueryFactory(
        params_parser_snovault_types,
        search_fields=[
            'embedded.title',
            'embedded.@id',
            '_all',
            '_exact',
        ]
    )
    search_fields = aq._get_search_fields()
    assert search_fields == [
        'embedded.title',
        'embedded.@id',
        '_all',
        '_exact'
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_search_fields_mode_picker(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=object&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    search_fields = aq._get_search_fields()
    assert set(search_fields) == set([
        '_all'
    ])


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_fields(params_parser, dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_fields() == [
        ('field', '@id'),
        ('field', 'accession')
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&field=status&field=@id&field=lab.name'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_fields() == [
        ('field', 'status'),
        ('field', '@id'),
        ('field', 'lab.name')
    ]


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_return_fields_from_field_params(params_parser, dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    fields = [('field', '@id'), ('field', 'accession'), ('field', 'status'), ('field', 'audit')]
    expected = [
        'embedded.@id',
        'embedded.accession',
        'embedded.status',
        'audit',
    ]
    actual = aq._get_return_fields_from_field_params(fields)
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_return_fields_from_schema_columns(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    expected = ['embedded.@id', 'embedded.accession', 'embedded.status']
    actual = aq._get_return_fields_from_schema_columns()
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_return_fields(params_parser, dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    expected = [
        'embedded.@id',
        'embedded.@type',
        'embedded.accession'
    ]
    actual = aq._get_return_fields()
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)
    dummy_request.environ['QUERY_STRING'] = (
        'status=released&frame=embedded'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    expected = [
        'embedded.*',
        'audit.*',
    ]
    actual = aq._get_return_fields()
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_combine_search_term_queries(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    combined_search_terms = aq._combine_search_term_queries(
        must_match_filters=aq.params_parser.get_must_match_search_term_filters(),
        must_not_match_filters=aq.params_parser.get_must_not_match_search_term_filters()
    )
    assert combined_search_terms == '(chip-seq) AND (rna) AND NOT (ENCODE 2)'
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    combined_search_terms = aq._combine_search_term_queries(
        must_match_filters=aq.params_parser.get_must_match_search_term_filters(),
        must_not_match_filters=aq.params_parser.get_must_not_match_search_term_filters()
    )
    assert combined_search_terms == '(chip-seq)'
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm!=rna&searchTerm!=ENCODE+2'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    combined_search_terms = aq._combine_search_term_queries(
        must_match_filters=aq.params_parser.get_must_match_search_term_filters(),
        must_not_match_filters=aq.params_parser.get_must_not_match_search_term_filters()
    )
    assert combined_search_terms == 'NOT (rna) AND NOT (ENCODE 2)'
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    combined_search_terms = aq._combine_search_term_queries(
        must_match_filters=aq.params_parser.get_must_match_search_term_filters(),
        must_not_match_filters=aq.params_parser.get_must_not_match_search_term_filters()
    )
    assert combined_search_terms is None


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_facets(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.testing import DummyResource
    params_parser_snovault_types._request.context = DummyResource()
    aq = AbstractQueryFactory(params_parser_snovault_types)
    expected = [
        ('type', {'title': 'Data Type', 'exclude': ['Item']}),
        ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
        ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
        ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
        ('status', {'title': 'Status', 'open_on_load': True}), ('name', {'title': 'Name'})
    ]
    actual = aq._get_facets()
    assert all(e in actual for e in expected)
    aq = AbstractQueryFactory(
        params_parser_snovault_types,
        facets=[]
    )
    assert aq._get_facets() == []


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_facet_size(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_facet_size() is None


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_boost_values_for_item_type(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_boost_values_for_item_type(
        'TestingSearchSchema'
    ) == {'accession': 1.0, 'status': 1.0, 'label': 1.0}


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_config_param_values(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&config=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_config_param_values()
    assert len(configs) == 1
    assert configs == ['TestingSearchSchema']
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&config=TestingSearchSchema&config=custom'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_config_param_values()
    assert len(configs) == 2
    assert configs == ['TestingSearchSchema', 'custom']
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_config_param_values()
    assert len(configs) == 0
    assert configs == []


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_configs_from_config_param_values(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&config=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_config_param_values()
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'
    assert len(aq._get_configs_from_item_types_as_combined_key()) == 0
    assert len(aq._get_configs_from_item_types_as_individual_keys()) == 0


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_configs_from_item_types_as_combined_key(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_combined_key()
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'
    assert len(aq._get_configs_from_item_types_as_individual_keys()) == 1
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema&type=TestingSearchSchemaSpecialFacets'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_combined_key()
    assert len(configs) == 0
    assert len(aq._get_configs_from_item_types_as_individual_keys()) == 2


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_configs_from_item_types_as_individual_keys(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_individual_keys()
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'
    assert len(aq._get_configs_from_item_types_as_combined_key()) == 1
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema&type=TestingSearchSchemaSpecialFacets'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_item_types_as_individual_keys()
    assert len(configs) == 2
    assert len(aq._get_configs_from_item_types_as_combined_key()) == 0


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_configs_from_default_item_types_as_individual_keys(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_default_item_types_as_individual_keys()
    assert len(configs) == 0
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema',
        ],
    )
    configs = aq._get_configs_from_default_item_types_as_individual_keys()
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'
    assert len(aq._get_configs_from_item_types_as_combined_key()) == 0
    assert len(aq._get_configs_from_item_types_as_individual_keys()) == 0
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema',
            'TestingSearchSchemaSpecialFacets',
        ],
    )
    configs = aq._get_configs_from_default_item_types_as_individual_keys()
    assert len(configs) == 2
    assert 'read_count' in configs[1].facets
    assert len(aq._get_configs_from_item_types_as_combined_key()) == 0
    assert len(aq._get_configs_from_item_types_as_individual_keys()) == 0


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_configs_from_param_values_or_item_types_as_combined_key(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.configs import SearchConfig
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&type=TestingSearchSchema'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_param_values_or_item_types_as_combined_key()
    assert len(configs) == 1
    assert isinstance(configs[0], SearchConfig)
    assert configs[0].name == 'TestingSearchSchema'
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_param_values_or_item_types_as_combined_key()
    assert len(configs) == 0
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&searchTerm=rna&searchTerm!=ENCODE+2'
        '&config=TestingSearchSchema&config=TestConfigItem'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    configs = aq._get_configs_from_param_values_or_item_types_as_combined_key()
    assert len(configs) == 2
    assert configs[0].name == 'TestingSearchSchema'
    assert configs[1].name == 'TestConfigItem'


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_show_internal_audits(dummy_request):
    from pyramid.testing import DummyResource
    from pyramid.security import Allow
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['REMOTE_USER'] = 'TEST_SUBMITTER'
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&assembly=GRCh38&biosample_ontology.classification=primary+cell'
        '&target.label=H3K27me3&biosample_ontology.classification%21=cell+line'
        '&biosample_ontology.term_name%21=naive+thymus-derived+CD4-positive%2C+alpha-beta+T+cell'
        '&limit=10&status=released&searchTerm=chip-seq&sort=date_created&sort=-files.file_size'
        '&field=@id&field=accession'
    )
    dummy_request.context = DummyResource()
    dummy_request.context.__acl__ = lambda: [(Allow, 'group.submitter', 'search_audit')]
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._show_internal_audits() == True
    dummy_request.context.__acl__ = lambda: []
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._show_internal_audits() == False


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_get_audit_facets(dummy_request):
    from pyramid.testing import DummyResource
    from pyramid.security import Allow
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    from snosearch.defaults import BASE_AUDIT_FACETS, INTERNAL_AUDIT_FACETS
    dummy_request.environ['REMOTE_USER'] = 'TEST_SUBMITTER'
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&assembly=GRCh38&biosample_ontology.classification=primary+cell'
        '&target.label=H3K27me3&biosample_ontology.classification%21=cell+line'
        '&biosample_ontology.term_name%21=naive+thymus-derived+CD4-positive%2C+alpha-beta+T+cell'
        '&limit=10&status=released&searchTerm=chip-seq&sort=date_created&sort=-files.file_size'
        '&field=@id&field=accession'
    )
    dummy_request.context = DummyResource()
    dummy_request.context.__acl__ = lambda: [(Allow, 'group.submitter', 'search_audit')]
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_audit_facets() == BASE_AUDIT_FACETS + INTERNAL_AUDIT_FACETS
    dummy_request.context.__acl__ = lambda: []
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    assert aq._get_audit_facets() == BASE_AUDIT_FACETS


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_prefix_value(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._prefix_value(
        'embedded.',
        'uuid'
    ) == 'embedded.uuid'


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_prefix_values(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    assert aq._prefix_values(
        'embedded.',
        ['uuid', 'status', '@type']
    ) == ['embedded.uuid', 'embedded.status', 'embedded.@type']


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_bool_filter_query(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    bf = aq._make_bool_query(
        filter=[
            aq._make_must_equal_terms_query(
                field='embedded.status',
                terms=['revoked', 'archived']
            )
        ]
    )
    assert bf.to_dict() == {
        'bool': {
            'filter': [
                {
                    'terms': {
                        'embedded.status': [
                            'revoked',
                            'archived'
                        ]
                    }
                }
            ]
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_bool_filter_query_must_not(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    bf = aq._make_bool_query(
        filter=[
            ~aq._make_must_equal_terms_query(
                field='embedded.status',
                terms=['revoked', 'archived']
            )
        ]
    )
    assert bf.to_dict() == {
        'bool': {
            'filter': [
                {
                    'bool': {
                        'must_not': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'revoked',
                                        'archived'
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_bool_filter_query_must_and_must_not(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    bf = aq._make_bool_query(
        filter=[
            ~aq._make_must_equal_terms_query(
                field='embedded.status',
                terms=['revoked', 'archived']
            ),
            ~aq._make_field_must_exist_query(
                field='embedded.file_size'
            ),
            aq._make_must_equal_terms_query(
                field='embedded.@type',
                terms=['Item']
            ),
            aq._make_field_must_exist_query(
                field='embedded.@type'
            )
        ]
    )
    assert bf.to_dict() == {
        'bool': {
            'filter': [
                {'bool': {'must_not': [{'terms': {'embedded.status': ['revoked', 'archived']}}]}},
                {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}},
                {'terms': {'embedded.@type': ['Item']}},
                {'exists': {'field': 'embedded.@type'}}
            ]
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_bool_filter_and_query_context(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    bf = aq._make_bool_query(
        filter=[
            ~aq._make_must_equal_terms_query(
                field='embedded.status',
                terms=['revoked', 'archived']
            ),
            ~aq._make_field_must_exist_query(
                field='embedded.file_size'
            ),
            aq._make_must_equal_terms_query(
                field='embedded.@type',
                terms=['Item']
            ),
            aq._make_field_must_exist_query(
                field='embedded.@type'
            )
        ]
    )
    aq.search = aq._get_or_create_search().query(bf)
    aq.search = aq.search.query(
        aq._make_query_string_query('test query', fields=['name', 'title'])
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {'bool': {'must_not': [{'terms': {'embedded.status': ['revoked', 'archived']}}]}},
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}},
                    {'terms': {'embedded.@type': ['Item']}},
                    {'exists': {'field': 'embedded.@type'}}
                ],
                'must': [
                    {
                        'query_string': {
                            'query': 'test query',
                            'default_operator': 'AND',
                            'fields': ['name', 'title']
                        }
                    }
                ]
            }
        }
    }
    fa = aq._make_filter_aggregation(
        filter_context=aq._make_must_equal_terms_query(
            field='embedded.@type',
            terms=['File']
        )
    )
    assert fa.to_dict() == {
        'filter': {
            'terms': {
                'embedded.@type': ['File']
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_filter_aggregation_bool_context(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    fa = aq._make_filter_aggregation(
        filter_context=aq._make_bool_query(
            filter=[
                aq._make_field_must_exist_query(
                    field='embedded.status'
                ),
                ~aq._make_field_must_exist_query(
                    field='embedded.audit'
                )
            ]
        )
    )
    assert fa.to_dict() == {
        'filter': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}},
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.audit'}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_filter_and_subaggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    fasa = aq._make_filter_and_subaggregation(
        title='Lab name terms on Experiments that have files with file_size',
        filter_context=(
            aq._make_must_equal_terms_query(
                field='@type',
                terms=['Experiment']
            )
            & aq._make_bool_query(
                filter=[
                    aq._make_field_must_exist_query(
                        field='embeddded.files.file_size'
                    )
                ]
            )
        ),
        subaggregation=aq._make_terms_aggregation(
            field='embedded.lab.name',
            size=123
        )
    )
    assert fasa.to_dict() == {
        'aggs': {
            'Lab name terms on Experiments that have files with file_size': {
                'terms': {
                    'field': 'embedded.lab.name',
                    'size': 123,
                }
            }
        },
        'filter': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embeddded.files.file_size'}}
                ],
                'must': [
                    {'terms': {'@type': ['Experiment']}}
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_filter_and_subaggregation_bool(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    fasa = aq._make_filter_and_subaggregation(
        title='Small processed versus raw files on first day of ENCODE4',
        filter_context=aq._make_bool_query(
            must=[
                aq._make_field_must_exist_query(
                    field='embedded.file_type'
                )
            ],
            should=[
                aq._make_must_equal_terms_query(
                    field='embedded.file_size',
                    terms=['1', '2', '3']
                )
            ],
            must_not=[
                aq._make_must_equal_terms_query(
                    field='embedded.@type',
                    terms=['Publication']
                ),
                aq._make_must_equal_terms_query(
                    field='embedded.award.rfa',
                    terms=['ENCODE2']
                )
            ],
            filter=[
                aq._make_must_equal_terms_query(
                    field='embedded.date_created',
                    terms=['05/01/2017']
                )
            ]
        ),
        subaggregation=aq._make_exists_aggregation(
            field='embedded.derived_from'
        )
    )
    assert fasa.to_dict() == {
        'aggs': {
            'Small processed versus raw files on first day of ENCODE4': {
                'filters': {
                    'filters': {
                        'no': {
                            'bool': {
                                'must_not': [{'exists': {'field': 'embedded.derived_from'}}]}
                        },
                        'yes': {
                            'exists': {'field': 'embedded.derived_from'}}}
                }
            }
        },
        'filter': {
            'bool': {
                'must_not': [
                    {'terms': {'embedded.@type': ['Publication']}},
                    {'terms': {'embedded.award.rfa': ['ENCODE2']}}
                ],
                'filter': [
                    {'terms': {'embedded.date_created': ['05/01/2017']}}
                ],
                'must': [
                    {'exists': {'field': 'embedded.file_type'}}
                ],
                'should': [
                    {'terms': {'embedded.file_size': ['1', '2', '3']}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_query_string_query(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    qsq = aq._make_query_string_query(
        'my TEST',
        fields=['embedded.description'],
        default_operator='OR'
    )
    assert qsq.to_dict() == {
        'query_string': {
            'default_operator': 'OR',
            'fields': ['embedded.description'],
            'query': 'my TEST'
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_must_equal_terms_query(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    mtq = aq._make_must_equal_terms_query(
        field='embedded.status',
        terms=['released']
    )
    assert mtq.to_dict() == {
        'terms': {
            'embedded.status': ['released']
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_must_equal_terms_queries_from_params(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    mtqs = aq._make_must_equal_terms_queries_from_params(
        params=sorted(aq._get_filters())
    )
    actual = [m.to_dict() for m in mtqs]
    expected = [
        {'terms': {'embedded.assay_title': ['Histone ChIP-seq']}},
        {'terms': {'embedded.status': ['released']}},
        {'terms': {'embedded.biosample_ontology.term_name': ['naive thymus-derived CD4-positive, alpha-beta T cell']}},
        {'terms': {'embedded.biosample_ontology.classification': ['primary cell', 'cell line']}},
        {'terms': {'embedded.target.label': ['H3K27me3']}},
        {'terms': {'embedded.assembly': ['GRCh38']}},
        {'terms': {'embedded.award.project': ['Roadmap']}}
    ]
    assert all(e in actual for e in expected)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_field_must_exist_query(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    meq = aq._make_field_must_exist_query(
        field='embedded.file_size'
    )
    assert meq.to_dict() == {
        'exists': {
            'field': 'embedded.file_size'
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_field_must_exist_queries_from_params(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    meqs = aq._make_field_must_exist_queries_from_params(
        params=aq._get_filters()
    )
    actual = [m.to_dict() for m in meqs]
    expected = [
        {'exists': {'field': 'embedded.assay_title'}},
        {'exists': {'field': 'embedded.assembly'}},
        {'exists': {'field': 'embedded.biosample_ontology.classification'}},
        {'exists': {'field': 'embedded.status'}},
        {'exists': {'field': 'embedded.biosample_ontology.term_name'}},
        {'exists': {'field': 'embedded.target.label'}},
        {'exists': {'field': 'embedded.award.project'}}
    ]
    assert all(e in actual for e in expected)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_convert_terms_to_range_syntax(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    ranges = aq._convert_terms_to_range_syntax(
        [
            'lt:5',
            'lte:3000',
            'gt:9999999999999',
            'gte:2022', # Test duplicate key overridden.
            'gte:3033',
        ]
    )
    assert ranges == {
        'lt': '5',
        'lte': '3000',
        'gt': '9999999999999',
        'gte': '3033',
    }
    assert aq._convert_terms_to_range_syntax(['lte:3000:asd']) == {
        'lte': '3000:asd'
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_range_query(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    rq = aq._make_range_query(
        field='embedded.read_count',
        terms=['gt:5', 'lte:30']
    )
    assert rq.to_dict() == {
        'range': {
            'embedded.read_count': {
                'gt': '5',
                'lte': '30'
            }
        }
    }


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_range_queries_from_params(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        '&file_size=gte:30000&file_size=lt:2560000&replicates.read_count=lte:99999999'
        '&biosample.replicate.size=gt:2&quality_metric.RSC1!=lt:30'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    rqs = aq._make_range_queries_from_params(
        params=sorted(aq._get_filters())
    )
    actual = [r.to_dict() for r in rqs]
    expected = [
        {
            'range': {
                'embedded.biosample.replicate.size': {
                    'gt': '2'
                }
            }
        },
        {
            'range': {
                'embedded.file_size': {
                    'gte': '30000',
                    'lt': '2560000'
                }
            }
        },
        {
            'range': {
                'embedded.quality_metric.RSC1': {
                    'lt': '30'
                }
            }
        },
        {
            'range': {
                'embedded.replicates.read_count': {
                    'lte': '99999999'
                }
            }
        }
    ]
    assert all(e in actual for e in expected)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_default_filters(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser_snovault_types)
    df = aq._make_default_filters()
    assert df[0].to_dict() == {
        'terms': {
            'principals_allowed.view': ['system.Everyone']
        }
    }
    assert df[1].to_dict() == {
        'terms': {
            'embedded.@type': ['TestingSearchSchema']
        }
    }


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_default_filters_default_types(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&assembly=GRCh38&biosample_ontology.classification=primary+cell'
        '&target.label=H3K27me3&biosample_ontology.classification%21=cell+line'
    )
    p = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(p, default_item_types=['Snowflake', 'Pancake'])
    df = aq._make_default_filters()
    assert df[0].to_dict() == {
        'terms': {
            'principals_allowed.view': ['system.Everyone']
        }
    }
    assert df[1].to_dict() == {
        'terms': {
            'embedded.@type': [
                'Snowflake', 'Pancake'
            ]
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_terms_aggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    ta = aq._make_terms_aggregation(
        field='embedded.lab.name',
        exclude=['other lab'],
        size=14
    )
    assert ta.to_dict() == {
        'terms': {
            'exclude': ['other lab'],
            'field': 'embedded.lab.name',
            'size': 14
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_exists_aggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    eq = aq._make_exists_aggregation(
        field='embedded.file_available'
    )
    assert eq.to_dict() == {
        'filters': {
            'filters': {
                'no': {
                    'bool': {
                        'must_not': [
                            {'exists': {'field': 'embedded.file_available'}}
                        ]
                    }
                },
                'yes': {
                    'exists': {'field': 'embedded.file_available'}
                }
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_stats_aggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    sa = aq._make_stats_aggregation(
        field='embedded.files.read_count',
    )
    assert sa.to_dict() == {
        'stats': {
            'field': 'embedded.files.read_count'
        }
    }


def test_searches_queries_abstract_query_factory_map_param_to_elasticsearch_field():
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory({})
    assert aq._map_param_to_elasticsearch_field('type') == 'embedded.@type'
    assert aq._map_param_to_elasticsearch_field('audit.WARNING.category') == 'audit.WARNING.category'
    assert aq._map_param_to_elasticsearch_field('status') == 'embedded.status'


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_map_param_keys_to_elasticsearch_fields(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&status=released'
        '&audit.WARNING.category=missing+biosample+characterization&file_size=12'
        '&limit=all'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    mapped_keys = list(aq._map_param_keys_to_elasticsearch_fields(
        params=aq._get_filters() + aq._get_item_types()
    ))
    assert mapped_keys == [
        ('embedded.status', 'released'),
        ('audit.WARNING.category', 'missing biosample characterization'),
        ('embedded.file_size', '12'),
        ('embedded.@type', 'TestingSearchSchema')
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_map_param_values_to_elasticsearch_fields(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&status=released'
        '&audit.WARNING.category=missing+biosample+characterization&file_size=12'
        '&field=status&field=@id&field=type&field=audit'
        '&limit=all'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    mapped_values = list(aq._map_param_values_to_elasticsearch_fields(
        params=aq._get_fields()
    ))
    assert mapped_values == [
        ('field', 'embedded.status'),
        ('field', 'embedded.@id'),
        ('field', 'embedded.@type'),
        ('field', 'audit')
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_simple_query_string_query(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_simple_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'simple_query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['simple_query_string']['query']
        == expected_query['query']['simple_query_string']['query']
    )
    assert (
        constructed_query['query']['simple_query_string']['default_operator']
        == expected_query['query']['simple_query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['simple_query_string']['fields'])
        == set(expected_query['query']['simple_query_string']['fields'])
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_query(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=chip-seq'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )
    assert (
        constructed_query['query']['query_string']['default_operator']
        == expected_query['query']['query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['query_string']['fields'])
        == set(expected_query['query']['query_string']['fields'])
    )
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=cherry^'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(cherry\\^)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=cherry~'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(cherry\\~)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=/cherry^~'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(\\/cherry\\^\\~)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_query_and_simple_query_string_query(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&advancedQuery=date_released:[01-01-2018 TO 01-01-2019]'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    aq.add_simple_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'query_string': {
                            'query': '(embedded.date_released:[01-01-2018 TO 01-01-2019])',
                            'default_operator': 'AND',
                            'fields': ['_all']
                        }
                    },
                    {
                        'simple_query_string': {
                            'query': '(chip-seq)',
                            'default_operator': 'AND',
                            'fields': ['_all']
                        }
                    }
                ]
            }
        }
    }
    actual_must = constructed_query['query']['bool']['must']
    actual_query_string = [
        a.get('query_string')
        for a in actual_must
        if 'query_string' in a
    ][0]
    actual_simple_query_string = [
        a.get('simple_query_string')
        for a in actual_must
        if 'simple_query_string' in a
    ][0]
    expected_must = expected_query['query']['bool']['must']
    expected_query_string = [
        e.get('query_string')
        for e in expected_must
        if 'query_string' in e
    ][0]
    expected_simple_query_string = [
        e.get('simple_query_string')
        for e in expected_must
        if 'simple_query_string' in e
    ][0]
    assert len(actual_must) == len(expected_must)
    assert actual_query_string == expected_query_string
    assert actual_simple_query_string == expected_simple_query_string


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_query_with_type(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=chip-seq&type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )
    assert (
        constructed_query['query']['query_string']['default_operator']
        == expected_query['query']['query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['query_string']['fields'])
        == set(expected_query['query']['query_string']['fields'])
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_simple_query_string_query_with_type(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_simple_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'simple_query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['simple_query_string']['query']
        == expected_query['query']['simple_query_string']['query']
    )
    assert (
        constructed_query['query']['simple_query_string']['default_operator']
        == expected_query['query']['simple_query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['simple_query_string']['fields'])
        == set(expected_query['query']['simple_query_string']['fields'])
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_query_with_default_type(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'advancedQuery=chip-seq'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema'
        ]
    )
    aq.add_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['query_string']['query']
        == expected_query['query']['query_string']['query']
    )
    assert (
        constructed_query['query']['query_string']['default_operator']
        == expected_query['query']['query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['query_string']['fields'])
        == set(expected_query['query']['query_string']['fields'])
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_simple_query_string_query_with_default_type(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        default_item_types=[
            'TestingSearchSchema'
        ]
    )
    aq.add_simple_query_string_query()
    constructed_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'simple_query_string': {
                'default_operator': 'AND',
                'fields': [
                    '_all'
                ],
                'query': '(chip-seq)'
            }
        }
    }
    assert (
        constructed_query['query']['simple_query_string']['query']
        == expected_query['query']['simple_query_string']['query']
    )
    assert (
        constructed_query['query']['simple_query_string']['default_operator']
        == expected_query['query']['simple_query_string']['default_operator']
    )
    assert (
        set(constructed_query['query']['simple_query_string']['fields'])
        == set(expected_query['query']['simple_query_string']['fields'])
    )


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_query_no_search_term(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_query_string_query()
    assert aq.search is None


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_simple_query_string_query_no_search_term(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_simple_query_string_query()
    assert aq.search is None


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_equal_terms_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_equal_terms_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {
                        'terms': {
                            'status': [
                                'released',
                                'archived'
                            ]
                        }
                    }
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_equal_terms_post_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_equal_terms_post_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'terms': {'status': ['released', 'archived']}}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_not_equal_terms_post_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_not_equal_terms_post_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'bool': {
                'filter': [
                    {'bool': {'must_not': [{'terms': {'status': ['released', 'archived']}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_not_equal_terms_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_not_equal_terms_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must_not': [
                                {
                                    'terms': {
                                        'status': [
                                            'released',
                                            'archived'
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }


def test_searches_queries_abstract_query_factory_add_field_must_exist_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [{'exists': {'field': 'embedded.status'}}]
                }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_exist_post_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_post_filter(
        'embedded.status'
    )
    assert aq.search.to_dict() == {
        'post_filter': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}}]
            }
        },
        'query': {
            'match_all': {}
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_exist_filter_multiple(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    aq._add_field_must_exist_filter(
        'embedded.lab'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}},
                    {'exists': {'field': 'embedded.lab'}}
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_not_exist_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_not_exist_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
       'query': {
            'bool': {
                'filter': [{'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_not_exist_post_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_not_exist_post_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'bool': {
                'filter': [
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_and_must_not_exist_filter(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    aq._add_field_must_not_exist_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}},
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_terms_aggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    aq._add_terms_aggregation('Statuses', 'embedded.status', size=10)
    assert aq.search.to_dict() == {
        'aggs': {
            'Statuses': {
                'terms': {
                    'field': 'embedded.status',
                    'size': 10,
                }
            }
        },
        'query': {'match_all': {}}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_split_filter_queries(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    must, must_not, exists, not_exists, ranges, not_ranges = aq._make_split_filter_queries()
    expected_must = [
        {'terms': {'embedded.award.project': ['Roadmap']}},
        {'terms': {'embedded.target.label': ['H3K27me3']}},
        {'terms': {'embedded.assembly': ['GRCh38']}},
        {'terms': {'embedded.status': ['released']}},
        {'terms': {'embedded.biosample_ontology.classification': ['primary cell']}},
        {'terms': {'embedded.assay_title': ['Histone ChIP-seq']}}
    ]
    actual_must = [m.to_dict() for m in must]
    assert all(e in actual_must for e in expected_must)
    expected_must_not = [
        {'terms': {'embedded.biosample_ontology.classification': ['cell line']}},
        {
            'terms': {
                'embedded.biosample_ontology.term_name': [
                    'naive thymus-derived CD4-positive, alpha-beta T cell'
                ]
            }
        }
    ]
    actual_must_not = [m.to_dict() for m in must_not]
    assert all(e in actual_must_not for e in expected_must_not)
    assert [e.to_dict() for e in exists] == []
    assert [e.to_dict() for e in not_exists] == []
    assert [e.to_dict() for e in ranges] == []
    assert [e.to_dict() for e in not_ranges] == []


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_split_filter_queries_wildcards(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=*&restricted!=*&no_file_available!=*'
        '&limit=10&field=@id&field=accession&lab.name=*&file_type=bam'
    )
    p = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(p)
    must, must_not, exists, not_exists, ranges, not_ranges = aq._make_split_filter_queries()
    actual_must = [m.to_dict() for m in must]
    expected_must = [
        {'terms': {'embedded.file_type': ['bam']}},
        {'terms': {'embedded.@type': ['TestingSearchSchema']}}
    ]
    assert all(e in actual_must for e in expected_must)
    assert [m.to_dict() for m in must_not] == []
    expected_exists = [{'exists': {'field': 'embedded.lab.name'}}, {'exists': {'field': 'embedded.status'}}]
    actual_exists = [e.to_dict() for e in exists]
    assert all(e in actual_exists for e in expected_exists)
    expected_not_exists = [
        {'exists': {'field': 'embedded.restricted'}},
        {'exists': {'field': 'embedded.no_file_available'}}
    ]
    actual_not_exists = [e.to_dict() for e in not_exists]
    assert all(e in actual_not_exists for e in expected_not_exists)
    assert [r.to_dict() for r in ranges] == []
    assert [r.to_dict() for r in not_ranges] == []


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_split_filter_queries_ranges(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=*&restricted!=*&no_file_available!=*'
        '&limit=10&field=@id&field=accession&lab.name=*&file_type=bam'
        '&file_size=gte:30000&file_size=lt:2560000&replicates.read_count=lte:99999999'
        '&biosample.replicate.size=gt:2&quality_metric.RSC1!=lt:30'
    )
    p = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(p)
    must, must_not, exists, not_exists, ranges, not_ranges = aq._make_split_filter_queries()
    actual_must = [m.to_dict() for m in must]
    expected_must = [
        {'terms': {'embedded.file_type': ['bam']}},
        {'terms': {'embedded.@type': ['TestingSearchSchema']}}
    ]
    assert all(e in actual_must for e in expected_must)
    assert [m.to_dict() for m in must_not] == []
    expected_exists = [
        {'exists': {'field': 'embedded.lab.name'}},
        {'exists': {'field': 'embedded.status'}}
    ]
    actual_exists = [e.to_dict() for e in exists]
    assert all(e in actual_exists for e in expected_exists)
    expected_not_exists = [
        {'exists': {'field': 'embedded.restricted'}},
        {'exists': {'field': 'embedded.no_file_available'}}
    ]
    actual_not_exists = [e.to_dict() for e in not_exists]
    assert all(e in actual_not_exists for e in expected_not_exists)
    assert [r.to_dict() for r in ranges] == [
        {'range': {'embedded.file_size': {'gte': '30000', 'lt': '2560000'}}},
        {'range': {'embedded.replicates.read_count': {'lte': '99999999'}}},
        {'range': {'embedded.biosample.replicate.size': {'gt': '2'}}}
    ]
    assert [r.to_dict() for r in not_ranges] == [
        {'range': {'embedded.quality_metric.RSC1': {'lt': '30'}}}
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_make_filter_aggregation(params_parser):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    fa = aq._make_filter_aggregation(
        filter_context=aq._make_must_equal_terms_query(
            field='embedded.@type',
            terms=['File']
        )
    )
    assert fa.to_dict() == {
        'filter': {
            'terms': {
                'embedded.@type': ['File']
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_equal_terms_post_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_equal_terms_post_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'terms': {'status': ['released', 'archived']}}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_not_equal_terms_post_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_not_equal_terms_post_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'bool': {
                'filter': [
                    {'bool': {'must_not': [{'terms': {'status': ['released', 'archived']}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_must_not_equal_terms_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_must_not_equal_terms_filter(
        field='status',
        terms=['released', 'archived']
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must_not': [
                                {
                                    'terms': {
                                        'status': [
                                            'released',
                                            'archived'
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_exist_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [{'exists': {'field': 'embedded.status'}}]
                }
        }
    }


def test_searches_queries_abstract_query_factory_add_field_must_exist_post_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_post_filter(
        'embedded.status'
    )
    assert aq.search.to_dict() == {
        'post_filter': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}}]
            }
        },
        'query': {
            'match_all': {}
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_exist_filter_multiple(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    aq._add_field_must_exist_filter(
        'embedded.lab'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}},
                    {'exists': {'field': 'embedded.lab'}}
                ]
            }
        }
    }


def test_searches_queries_abstract_query_factory_add_field_must_not_exist_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_not_exist_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [{'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_not_exist_post_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_not_exist_post_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
        'query': {
            'match_all': {}
        },
        'post_filter': {
            'bool': {
                'filter': [
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_field_must_and_must_not_exist_filter(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_field_must_exist_filter(
        'embedded.status'
    )
    aq._add_field_must_not_exist_filter(
        'embedded.file_size'
    )
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {'exists': {'field': 'embedded.status'}},
                    {'bool': {'must_not': [{'exists': {'field': 'embedded.file_size'}}]}}
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_terms_aggregation(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_terms_aggregation('Statuses', 'embedded.status', size=10)
    assert aq.search.to_dict() == {
        'aggs': {
            'Statuses': {
                'terms': {
                    'field': 'embedded.status',
                    'size': 10,
                }
            }
        },
        'query': {'match_all': {}}
    }


def test_searches_queries_abstract_query_factory_add_terms_aggregation_with_exclusion(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_terms_aggregation('Statuses', 'embedded.status', exclude=['Item'])
    assert aq.search.to_dict() == {
        'aggs': {
            'Statuses': {
                'terms': {
                    'exclude': ['Item'],
                    'field': 'embedded.status',
                    'size': 200
                }
            }
        },
        'query': {'match_all': {}}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_exists_aggregation(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq._add_exists_aggregation('Processed file', 'embedded.derived_from')
    assert aq.search.to_dict() == {
        'aggs': {
            'Processed file': {
                'filters': {
                    'filters': {
                        'no': {
                            'bool': {
                                'must_not': [
                                    {
                                        'exists': {
                                            'field': 'embedded.derived_from'
                                        }
                                    }
                                ]
                            }
                        },
                        'yes': {
                            'exists': {
                                'field': 'embedded.derived_from'
                            }
                        }
                    }
                }
            }
        },
        'query': {'match_all': {}}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_filters(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq.add_filters()
    assert aq.search.to_dict() == {
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must': [
                                {'terms': {'principals_allowed.view': ['system.Everyone']}},
                                {'terms': {'embedded.@type': ['Experiment']}}
                            ]
                        }
                    }
                ]
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_post_filters(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq.add_post_filters()
    actual_must = aq.search.to_dict()['post_filter']['bool']['must']
    expected_must = [
        {'terms': {'embedded.@type': ['Experiment']}},
        {'terms': {'embedded.target.label': ['H3K27me3']}},
        {'terms': {'embedded.assembly': ['GRCh38']}},
        {'terms': {'embedded.award.project': ['Roadmap']}},
        {'terms': {'embedded.assay_title': ['Histone ChIP-seq']}},
        {'terms': {'embedded.status': ['released']}},
        {'terms': {'embedded.biosample_ontology.classification': ['primary cell']}}
    ]
    assert all(e in actual_must for e in expected_must)
    actual_must_not = aq.search.to_dict()['post_filter']['bool']['must_not']
    expected_must_not = [
        {
            'terms': {
                'embedded.biosample_ontology.term_name': [
                    'naive thymus-derived CD4-positive, alpha-beta T cell'
                ]
            }
        },
        {
            'terms': {
                'embedded.biosample_ontology.classification': [
                    'cell line'
                ]
            }
        }
    ]
    assert all(e in actual_must_not for e in expected_must_not)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_query_string_and_post_filters_wildcards(dummy_request):
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&status=*&restricted!=*'
        '&no_file_available!=*&limit=10&field=@id&field=accession&lab.name=*'
        '&file_type=bam'
    )
    p = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(p)
    aq.add_simple_query_string_query()
    aq.add_post_filters()
    actual_query = aq.search.to_dict()
    expected_query = {
        'query': {
            'simple_query_string': {
                'query': '(chip-seq)',
                'fields': [
                    '_all',
                    '*.uuid',
                    'unique_keys.*',
                    'embedded.accession',
                    'embedded.status',
                    '*.submitted_file_name',
                    '*.md5sum'
                ],
                'default_operator': 'AND'
            }
        },
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                    {'terms': {'embedded.file_type': ['bam']}},
                    {'exists': {'field': 'embedded.lab.name'}},
                    {'exists': {'field': 'embedded.status'}}
                ],
                'must_not': [
                    {'exists': {'field': 'embedded.restricted'}},
                    {'exists': {'field': 'embedded.no_file_available'}}
                ]
            }
        }
    }
    assert (
        expected_query['query']['simple_query_string']['query']
        == actual_query['query']['simple_query_string']['query']
    )
    assert all(
        e in actual_query['post_filter']['bool']['must_not']
        for e in expected_query['post_filter']['bool']['must_not']
    )
    assert all(
        e in actual_query['post_filter']['bool']['must']
        for e in expected_query['post_filter']['bool']['must']
    )


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_source(params_parser, mocker):
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory(params_parser)
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq.add_source()
    expected = ['embedded.@id', 'embedded.@type', 'embedded.accession']
    actual = aq.search.to_dict()['_source']
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_source_object(dummy_request):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_source()
    expected = ['object.*', 'audit.*']
    actual = aq.search.to_dict()['_source']
    assert all([e in actual for e in expected])
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_slice(params_parser, dummy_request, mocker):
    from snosearch.queries import AbstractQueryFactory
    from snosearch.parsers import ParamsParser
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    aq = AbstractQueryFactory(params_parser)
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 10, 'query': {'match_all': {}}}
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object&limit=all'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 0, 'query': {'match_all': {}}}
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object&limit=3000'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 3000, 'query': {'match_all': {}}}
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object&limit=blah'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 25, 'query': {'match_all': {}}}
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object&limit=10000'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(params_parser)
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 0, 'query': {'match_all': {}}}
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=chip-seq&type=TestingSearchSchema&frame=object&limit=100000'
    )
    params_parser = ParamsParser(dummy_request)
    aq = AbstractQueryFactory(
        params_parser,
        max_result_window=200000,
    )
    aq.add_slice()
    assert aq.search.to_dict() == {'from': 0, 'size': 100000, 'query': {'match_all': {}}}


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_subaggregation_factory(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from elasticsearch_dsl.aggs import Filters, Terms, Stats
    aq = AbstractQueryFactory(params_parser_snovault_types)
    sa = aq._subaggregation_factory('exists')(field='')
    assert isinstance(sa, Filters)
    sa = aq._subaggregation_factory('terms')(field='')
    assert isinstance(sa, Terms)
    sa = aq._subaggregation_factory('typeahead')(field='')
    assert isinstance(sa, Terms)
    sa = aq._subaggregation_factory('stats')(field='')
    assert isinstance(sa, Stats)


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_abstract_query_factory_add_aggregations_and_aggregation_filters(params_parser_snovault_types):
    from snosearch.queries import AbstractQueryFactory
    from pyramid.testing import DummyResource
    params_parser_snovault_types._request.context = DummyResource()
    aq = AbstractQueryFactory(params_parser_snovault_types)
    aq.add_aggregations_and_aggregation_filters()
    expected = {
        'query': {
            'match_all': {}
        },
        'aggs': {
            'Audit category: WARNING': {
                'aggs': {
                    'audit-WARNING-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.WARNING.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Audit category: NOT COMPLIANT': {
                'aggs': {
                    'audit-NOT_COMPLIANT-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.NOT_COMPLIANT.category'
                        }
                    }
                }
                ,
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Status': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.status'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Name': {
                'aggs': {
                    'name': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.name'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Data Type': {
                'aggs': {
                    'type': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.@type'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}}
                        ]
                    }
                }
            },
            'Audit category: ERROR': {
                'aggs': {
                    'audit-ERROR-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.ERROR.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            }
        }
    }
    actual = aq.search.to_dict()
    assert all(
        k in actual.get('aggs', {}).keys()
        for k in expected.get('aggs', {}).keys()
    )
    assert actual['aggs']['Data Type']['aggs']['type']['terms']['exclude'] == ['Item']


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_add_aggregations_and_aggregation_filters_special_facets(dummy_request):
    from snosearch.queries import BasicSearchQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchemaSpecialFacets&status=released&dbxref=*&replcate.biosample.title=cell'
        '&read_count=gte:3000&size!=lt:555'
        '&limit=10'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    bsqf = BasicSearchQueryFactory(params_parser)
    bsqf.add_aggregations_and_aggregation_filters()
    partial_expected = {
        'query': {
            'match_all': {}
        },
        'aggs': {
            'Data Type': {
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}},
                            {'range': {'embedded.read_count': {'gte': '3000'}}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}},
                            {'range': {'embedded.size': {'lt': '555'}}}
                        ]
                    }
                },
                'aggs': {
                    'type': {
                        'terms': {
                            'field': 'embedded.@type', 'exclude': ['Item'], 'size': 200
                        }
                    }
                }
            },
            'Status': {
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchemaSpecialFacets']}},
                            {'exists': {'field': 'embedded.dbxref'}},
                            {'range': {'embedded.read_count': {'gte': '3000'}}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}},
                            {'range': {'embedded.size': {'lt': '555'}}}
                        ]
                    }
                },
                'aggs': {
                    'status': {
                        'filters': {
                            'filters': {
                                'yes': {
                                    'exists': {'field': 'embedded.status'}
                                },
                                'no': {
                                    'bool': {
                                        'must_not': [
                                            {'exists': {'field': 'embedded.status'}}
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            'Read count range': {
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchemaSpecialFacets']}},
                            {'exists': {'field': 'embedded.dbxref'}}],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}},
                            {'range': {'embedded.size': {'lt': '555'}}}
                        ]
                    }
                },
                'aggs': {
                    'read_count': {
                        'stats': {
                            'field': 'embedded.read_count'
                        }
                    }
                }
            },
            'Name': {
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchemaSpecialFacets']}},
                            {'exists': {'field': 'embedded.dbxref'}},
                            {'range': {'embedded.read_count': {'gte': '3000'}}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}},
                            {'range': {'embedded.size': {'lt': '555'}}}]}},
                'aggs': {
                    'name': {
                        'terms': {
                            'field': 'embedded.name',
                            'size': 200
                        }
                    }
                }
            }
        }
    }
    actual = bsqf.search.to_dict()
    assert all(
        k in actual.get('aggs', {}).keys()
        for k in partial_expected.get('aggs', {}).keys()
    )
    assert (
        actual['aggs']['Read count range']['aggs']['read_count']['stats']['field'] == 'embedded.read_count'
    )




def test_searches_queries_abstract_query_factory_build_query():
    from snosearch.queries import AbstractQueryFactory
    aq = AbstractQueryFactory({})
    with pytest.raises(NotImplementedError):
        aq.build_query()


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_init(params_parser):
    from snosearch.queries import BasicSearchQueryFactory
    bsqf = BasicSearchQueryFactory(params_parser)
    assert isinstance(bsqf, BasicSearchQueryFactory)
    assert bsqf.params_parser == params_parser


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_build_query(dummy_request):
    from snosearch.queries import BasicSearchQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&status=archived&file_format=bam'
        '&lab.name!=thermo&restricted!=*&dbxref=*&replcate.biosample.title=cell'
        '&limit=10'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    bsqf = BasicSearchQueryFactory(params_parser)
    query = bsqf.build_query()
    expected = {
        'query': {
            'bool': {
                'must': [
                    {'terms': {'principals_allowed.view': ['system.Everyone']}},
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                ]
            }
        },
        '_source': ['embedded.*'],
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                    {'terms': {'embedded.status': ['released', 'archived']}},
                    {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                    {'terms': {'embedded.file_format': ['bam']}},
                    {'exists': {'field': 'embedded.dbxref'}}
                ],
                'must_not': [
                    {'terms': {'embedded.lab.name': ['thermo']}},
                    {'exists': {'field': 'embedded.restricted'}}
                ]
            }
        }
    }
    actual = query.to_dict()
    expected_must = actual['post_filter']['bool']['must']
    actual_must = expected['post_filter']['bool']['must']
    assert all(e in actual_must for e in expected_must)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_build_query_with_ranges(dummy_request):
    from snosearch.queries import BasicSearchQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&status=archived&file_format=bam'
        '&lab.name!=thermo&restricted!=*&dbxref=*&replcate.biosample.title=cell'
        '&limit=10&type=*&status!=submitted&file_size=*'
        '&file_format%21=bigWig&restricted!=*&no_file_available!=*'
        '&file_size=gte:30000&file_size=lt:2560000&replicates.read_count=lte:99999999'
        '&biosample.replicate.size=gt:2&quality_metric.RSC1!=lt:30'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    bsqf = BasicSearchQueryFactory(params_parser)
    query = bsqf.build_query()
    expected = {
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must': [
                                {'terms': {'principals_allowed.view': ['system.Everyone']}},
                                {'terms': {'embedded.@type': ['Item']}}
                            ]
                        }
                    }
                ]
            }
        },
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.status': ['released', 'archived']}},
                    {'terms': {'embedded.file_format': ['bam']}},
                    {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                    {'terms': {'embedded.@type': ['Item']}},
                    {'exists': {'field': 'embedded.dbxref'}},
                    {'exists': {'field': 'embedded.file_size'}},
                    {'range': {'embedded.file_size': {'gte': '30000', 'lt': '2560000'}}},
                    {'range': {'embedded.replicates.read_count': {'lte': '99999999'}}},
                    {'range': {'embedded.biosample.replicate.size': {'gt': '2'}}}
                ],
                'must_not': [
                    {'terms': {'embedded.lab.name': ['thermo']}},
                    {'terms': {'embedded.status': ['submitted']}},
                    {'terms': {'embedded.file_format': ['bigWig']}},
                    {'exists': {'field': 'embedded.restricted'}},
                    {'exists': {'field': 'embedded.no_file_available'}},
                    {'range': {'embedded.quality_metric.RSC1': {'lt': '30'}}}
                ]
            }
        },
        '_source': [
            'audit.*',
            'embedded.@id',
            'embedded.@type',
            'embedded.accession',
            'embedded.status'
        ],
        'from': 0,
        'size': 10
    }
    actual = query.to_dict()
    expected_must = actual['post_filter']['bool']['must']
    actual_must = expected['post_filter']['bool']['must']
    assert all(e in actual_must for e in expected_must)
    expected_must_not = actual['post_filter']['bool']['must_not']
    actual_must_not = expected['post_filter']['bool']['must_not']
    assert all(e in actual_must_not for e in expected_must_not)


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_with_facets_init(params_parser):
    from snosearch.queries import BasicSearchQueryFactoryWithFacets
    bsqf = BasicSearchQueryFactoryWithFacets(params_parser)
    assert isinstance(bsqf, BasicSearchQueryFactoryWithFacets)
    assert bsqf.params_parser == params_parser


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_with_facets_build_query(dummy_request):
    from snosearch.queries import BasicSearchQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&status=archived&file_format=bam'
        '&lab.name!=thermo&restricted!=*&dbxref=*&replcate.biosample.title=cell'
        '&limit=10'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    bsqf = BasicSearchQueryFactoryWithFacets(params_parser)
    query = bsqf.build_query()
    expected = {
        'query': {
            'bool': {
                'must': [
                    {'terms': {'principals_allowed.view': ['system.Everyone']}},
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                ]
            }
        },
        'aggs': {
            'Status': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.status'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            },
            'Audit category: ERROR': {
                'aggs': {
                    'audit-ERROR-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.ERROR.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            },
            'Audit category: NOT COMPLIANT': {
                'aggs': {
                    'audit-NOT_COMPLIANT-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.NOT_COMPLIANT.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            },
            'Data Type': {
                'aggs': {
                    'type': {
                        'terms': {
                            'size': 200,
                            'exclude': ['Item'],
                            'field': 'embedded.@type'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            },
            'Name': {
                'aggs': {
                    'name': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.name'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            },
            'Audit category: WARNING': {
                'aggs': {
                    'audit-WARNING-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.WARNING.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released', 'archived']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                            {'terms': {'embedded.file_format': ['bam']}},
                            {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                            {'exists': {'field': 'embedded.dbxref'}}
                        ],
                        'must_not': [
                            {'terms': {'embedded.lab.name': ['thermo']}},
                            {'exists': {'field': 'embedded.restricted'}}
                        ]
                    }
                }
            }
        },
        '_source': ['embedded.*'],
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.status': ['released', 'archived']}},
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}},
                    {'terms': {'embedded.file_format': ['bam']}},
                    {'terms': {'embedded.replcate.biosample.title': ['cell']}},
                    {'exists': {'field': 'embedded.dbxref'}}
                ],
                'must_not': [
                    {'terms': {'embedded.lab.name': ['thermo']}},
                    {'exists': {'field': 'embedded.restricted'}}
                ]
            }
        }
    }
    actual = query.to_dict()
    expected_post_filter_bool_must = expected['post_filter']['bool']['must']
    actual_post_filter_bool_must = actual['post_filter']['bool']['must']
    assert all(e in actual_post_filter_bool_must for e in expected_post_filter_bool_must)
    assert 'aggs' in actual
    assert '_source' in actual
    assert 'sort' in actual


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_without_facets_init(params_parser):
    from snosearch.queries import BasicSearchQueryFactoryWithoutFacets
    bsqf = BasicSearchQueryFactoryWithoutFacets(params_parser)
    assert isinstance(bsqf, BasicSearchQueryFactoryWithoutFacets)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_search_query_factory_without_facets_build_query(dummy_request):
    from snosearch.queries import BasicSearchQueryFactoryWithoutFacets
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&status=archived&file_format=bam'
        '&lab.name!=thermo&restricted!=*&dbxref=*&replcate.biosample.title=cell'
        '&limit=10'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    bsqf = BasicSearchQueryFactoryWithoutFacets(params_parser)
    query = bsqf.build_query()
    actual = query.to_dict()
    assert 'aggs' not in actual
    assert actual['size'] == 10
    assert 'sort' in actual


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_cached_facet_query_factory_init(params_parser):
    from snosearch.queries import CachedFacetsQueryFactory
    cfqf = CachedFacetsQueryFactory(params_parser)
    assert isinstance(cfqf, CachedFacetsQueryFactory)


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_cached_facet_query_factory_build_query(dummy_request):
    from snosearch.queries import CachedFacetsQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released&status=archived&file_format=bam'
        '&lab.name!=thermo&restricted!=*&dbxref=*&replcate.biosample.title=cell'
        '&limit=10'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    cfqf = CachedFacetsQueryFactory(params_parser)
    query = cfqf.build_query()
    actual = query.to_dict()
    assert 'aggs' in actual
    assert '_source' not in actual
    assert actual['size'] == 0
    assert 'sort' not in actual


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_collection_search_query_factory_with_facets_get_item_types(params_parser):
    from snosearch.queries import CollectionSearchQueryFactoryWithFacets
    from snosearch.interfaces import TYPES
    context = params_parser._request.registry[TYPES]['TestingSearchSchema']
    params_parser._request.context = context
    cs = CollectionSearchQueryFactoryWithFacets(params_parser)
    item_types = cs._get_item_types()
    assert item_types == [
        ('type', 'TestingSearchSchema')
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_init(params_parser):
    from snosearch.queries import BasicReportQueryFactory
    brqf = BasicReportQueryFactory(params_parser)
    assert isinstance(brqf, BasicReportQueryFactory)
    assert brqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_with_facets_init(params_parser):
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    assert isinstance(brqf, BasicReportQueryFactoryWithFacets)
    assert brqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_without_facets_init(params_parser):
    from snosearch.queries import BasicReportQueryFactoryWithoutFacets
    brqf = BasicReportQueryFactoryWithoutFacets(params_parser)
    assert isinstance(brqf, BasicReportQueryFactoryWithoutFacets)
    assert brqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_report_query_factory_with_facets_get_item_types(params_parser, dummy_request):
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    from pyramid.exceptions import HTTPBadRequest
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    item_types = brqf._get_item_types()
    assert item_types == [
        ('type', 'Experiment')
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&type=Experiment&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    with pytest.raises(HTTPBadRequest):
        brqf._get_item_types()
    dummy_request.environ['QUERY_STRING'] = (
        'status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    with pytest.raises(HTTPBadRequest):
        brqf._get_item_types()


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_with_facets_validate_item_type_subtypes(dummy_request):
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    from pyramid.exceptions import HTTPBadRequest
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.validate_item_type_subtypes()
    dummy_request.environ['QUERY_STRING'] = (
        'type=Item&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    with pytest.raises(HTTPBadRequest):
        brqf.validate_item_type_subtypes()


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_with_facets_add_slice(dummy_request):
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 0
    assert q['size'] == 10
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=100&from=25&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 25
    assert q['size'] == 100
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=all&from=25&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 25
    assert q['size'] == 0
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&from=25&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 25
    assert q['size'] == 25
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 0
    assert q['size'] == 25
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=9999&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 0
    assert q['size'] == 9999
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=100000&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    brqf.add_slice()
    q = brqf.search.to_dict()
    assert q['from'] == 0
    assert q['size'] == 0


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_with_facets_build_query(dummy_request):
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    params_parser._request.context = DummyResource()
    brqf = BasicReportQueryFactoryWithFacets(params_parser)
    q = brqf.build_query()
    q = q.to_dict()
    assert q['size'] == 10
    assert q['from'] == 0
    assert 'aggs' in q
    assert q['query']['bool']
    assert q['_source'] == ['embedded.@id', 'embedded.@type', 'embedded.accession']
    assert q['sort'] == [
        {'embedded.date_created': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.label': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.uuid': {'order': 'desc', 'unmapped_type': 'keyword'}}
    ]


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_basic_report_query_factory_without_facets_build_query(dummy_request):
    from snosearch.queries import BasicReportQueryFactoryWithoutFacets
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    params_parser._request.context = DummyResource()
    brqf = BasicReportQueryFactoryWithoutFacets(params_parser)
    q = brqf.build_query()
    q = q.to_dict()
    assert q['size'] == 10
    assert q['from'] == 0
    assert 'aggs' not in q
    assert q['query']['bool']
    assert q['_source'] == ['embedded.@id', 'embedded.@type', 'embedded.accession']
    assert q['sort'] == [
        {'embedded.date_created': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.label': {'order': 'desc', 'unmapped_type': 'keyword'}},
        {'embedded.uuid': {'order': 'desc', 'unmapped_type': 'keyword'}}
    ]


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_init(params_parser):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    assert isinstance(bmqf, BasicMatrixQueryFactoryWithFacets)
    assert bmqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_matrix_for_item_type(params_parser_snovault_types):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser_snovault_types)
    matrix = bmqf._get_matrix_for_item_type('TestingSearchSchema')
    assert 'x' in matrix
    assert 'y' in matrix
    assert 'group_by' in matrix['x']
    assert 'group_by' in matrix['y']


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_matrix_definition_name(params_parser_snovault_types):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser_snovault_types)
    assert bmqf._get_matrix_definition_name() == 'matrix'
    bmqf = BasicMatrixQueryFactoryWithFacets(
        params_parser_snovault_types,
        matrix_definition_name='new_matrix'
    )
    assert bmqf._get_matrix_definition_name() == 'new_matrix'


@pytest.mark.parametrize(
    'params_parser_snovault_types',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_matrix_for_item_type_with_no_matrix(params_parser_snovault_types):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from pyramid.exceptions import HTTPBadRequest
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser_snovault_types)
    with pytest.raises(HTTPBadRequest):
        bmqf._get_matrix_for_item_type('TestingPostPutPatch')


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_item_types(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from snosearch.parsers import ParamsParser
    from pyramid.exceptions import HTTPBadRequest
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    item_types = bmqf._get_item_types()
    assert item_types == [
        ('type', 'Experiment')
    ]
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&type=Experiment&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    with pytest.raises(HTTPBadRequest):
        bmqf._get_item_types()
    dummy_request.environ['QUERY_STRING'] = (
        'status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    params_parser = ParamsParser(dummy_request)
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    with pytest.raises(HTTPBadRequest):
        bmqf._get_item_types()


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_group_by_fields_by_item_type_and_value(params_parser):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from pyramid.exceptions import HTTPBadRequest
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    assert bmqf._get_group_by_fields_by_item_type_and_value('TestingSearchSchema', 'x') == ['label']
    assert bmqf._get_group_by_fields_by_item_type_and_value('TestingSearchSchema', 'y') == ['status', 'name']
    with pytest.raises(HTTPBadRequest):
        # No matrix defined.
        bmqf._get_group_by_fields_by_item_type_and_value('TestingPostPutPatch', 'y') == []


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_x_group_by_fields(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    assert bmqf._get_x_group_by_fields() == ['label']


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_y_group_by_fields(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    assert isinstance(bmqf, BasicMatrixQueryFactoryWithFacets)
    assert bmqf._get_y_group_by_fields() == ['status', 'name']


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_make_list_of_name_and_subagg_tuples(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from elasticsearch_dsl.aggs import Terms
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    nat = bmqf._make_list_of_name_and_subagg_tuples(['file_type', 'lab.name'])
    assert nat[0][0] == 'file_type'
    assert nat[1][0] == 'lab.name'
    assert isinstance(nat[0][1], Terms)
    assert isinstance(nat[1][1], Terms)
    assert nat[0][1].to_dict() == {
        'terms': {
            'field': 'embedded.file_type',
            'size': 999999
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_make_subaggregation_from_names(params_parser):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    name, subagg = bmqf._make_subaggregation_from_names(['biosample_term_name', 'biosample_title', 'assay_title'])
    assert name == 'biosample_term_name'
    expected = {
        'aggs': {
            'biosample_title': {
                'aggs': {
                    'assay_title': {
                        'terms': {
                            'field': 'embedded.assay_title',
                            'size': 999999,
                        }
                    }
                },
                'terms': {
                    'field': 'embedded.biosample_title',
                    'size': 999999,
                }
            }
        },
        'terms': {
            'field': 'embedded.biosample_term_name',
            'size': 999999,
        }
    }
    actual = subagg.to_dict()
    assert expected == actual
    name, subagg = bmqf._make_subaggregation_from_names(['assay_title'])
    assert name == 'assay_title'
    assert subagg.to_dict() == {
        'terms': {
            'field':
            'embedded.assay_title',
            'size': 999999
        }
    }
    name, subagg = bmqf._make_subaggregation_from_names([])
    assert name is None
    assert subagg is None


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_get_group_by_names(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    group_by_names = bmqf._get_group_by_names()
    assert group_by_names == [('x', ['label']), ('y', ['status', 'name', 'label'])]


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_add_matrix_aggregations(params_parser, dummy_request):
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    bmqf.add_matrix_aggregations()
    expected = {
        'aggs': {
            'y': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.status'
                        },
                        'aggs': {
                            'name': {
                                'terms': {
                                    'size': 999999,
                                    'field': 'embedded.name'
                                },
                                'aggs': {
                                    'label': {
                                        'terms': {
                                            'size': 999999,
                                            'field': 'embedded.label'
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            'x': {
                'aggs': {
                    'label': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.label'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        'query': {
            'match_all': {}
        }
    }
    actual = bmqf.search.to_dict()
    assert all([e in actual for e in expected])
    assert actual['aggs']['y']['aggs']['status']['terms']['field'] == 'embedded.status'
    assert actual['aggs']['y']['aggs']['status']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['field'] == 'embedded.name'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['size'] == 999999
    assert actual['aggs']['x']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['x']['aggs']['label']['terms']['size'] == 999999
    assert len(actual['aggs']['y']['filter']['bool']['must']) == 2
    assert len(actual['aggs']['x']['filter']['bool']['must']) == 2


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_basic_matrix_query_factory_with_facets_build_query(params_parser, dummy_request):
    from pyramid.testing import DummyResource
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    dummy_request.context = DummyResource({})
    bmqf = BasicMatrixQueryFactoryWithFacets(params_parser)
    bmqf.build_query()
    expected = {
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.status': ['released']}},
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                ]
            }
        },
        'aggs': {
            'Data Type': {
                'aggs': {
                    'type': {
                        'terms': {
                            'exclude': [
                                'Item'
                            ],
                            'size': 200,
                            'field': 'embedded.@type'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}}
                        ]
                    }
                }
            },
            'y': {
                'aggs': {
                    'status': {
                        'aggs': {
                            'name': {
                                'aggs': {
                                    'label': {
                                        'terms': {
                                            'size': 999999,
                                            'field': 'embedded.label'
                                        }
                                    }
                                },
                                'terms': {
                                    'size': 999999,
                                    'field': 'embedded.name'
                                }
                            }
                        },
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.status'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Audit category: NOT COMPLIANT': {
                'aggs': {
                    'audit-NOT_COMPLIANT-category': {
                        'terms': {
                            'size': 200,
                            'field':
                            'audit.NOT_COMPLIANT.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Audit category: ERROR': {
                'aggs': {
                    'audit-ERROR-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.ERROR.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Status': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 200,
                            'field':
                            'embedded.status'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}
                            }
                        ]
                    }
                }
            },
            'Audit category: WARNING': {
                'aggs': {
                    'audit-WARNING-category': {
                        'terms': {
                            'size': 200,
                            'field': 'audit.WARNING.category'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'Name': {
                'aggs': {
                    'name': {
                        'terms': {
                            'size': 200,
                            'field': 'embedded.name'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            },
            'x': {
                'aggs': {
                    'label': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.label'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            }
        },
        'from': 0,
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must': [
                                {'terms': {'principals_allowed.view': ['system.Everyone']}},
                                {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                            ]
                        }
                    }
                ]
            }
        },
        'size': 0
    }
    actual = bmqf.search.to_dict()
    assert set(actual.keys()) == set(expected.keys())
    assert set(actual['aggs'].keys()) == set(expected['aggs'].keys())
    assert actual['size'] == 0


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_missing_matrix_query_factory_with_facets_init(params_parser):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    mmqf = MissingMatrixQueryFactoryWithFacets(params_parser)
    assert isinstance(mmqf, MissingMatrixQueryFactoryWithFacets)
    assert mmqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_missing_matrix_query_factory_with_facets_parse_name_and_default_value_from_name(params_parser, dummy_request):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    from elasticsearch_dsl.aggs import Terms
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MissingMatrixQueryFactoryWithFacets(params_parser)
    name, default_value = mmqf._parse_name_and_default_value_from_name('target.label')
    assert name == 'target.label'
    assert default_value is None
    name, default_value = mmqf._parse_name_and_default_value_from_name(('target.label', 'no_target'))
    assert name == 'target.label'
    assert default_value == 'no_target'


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_missing_matrix_query_factory_with_facets_make_subaggregation_with_possible_default_value_from_name(params_parser, dummy_request):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    from elasticsearch_dsl.aggs import Terms
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MissingMatrixQueryFactoryWithFacets(params_parser)
    name, subagg_with_default_value = mmqf._make_subaggregation_with_possible_default_value_from_name(
        mmqf._subaggregation_factory('TERMS'),
        ('target.label', 'no_target')
    )
    assert name == 'target.label'
    assert subagg_with_default_value.to_dict() == {
        'terms': {
            'size': 999999,
            'field': 'embedded.target.label',
            'missing': 'no_target'
        }
    }


def test_searches_queries_missing_matrix_query_factory_with_facets_make_list_of_name_and_subagg_tuples(params_parser, dummy_request):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    from elasticsearch_dsl.aggs import Terms
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MissingMatrixQueryFactoryWithFacets(params_parser)
    nat = mmqf._make_list_of_name_and_subagg_tuples(['file_type', 'lab.name'])
    assert nat[0][0] == 'file_type'
    assert nat[1][0] == 'lab.name'
    assert isinstance(nat[0][1], Terms)
    assert isinstance(nat[1][1], Terms)
    assert nat[0][1].to_dict() == {
        'terms': {
            'field': 'embedded.file_type',
            'size': 999999
        }
    }
    nat = mmqf._make_list_of_name_and_subagg_tuples([('file_type', 'missing_file_type'), 'lab.name'])
    assert nat[0][0] == 'file_type'
    assert nat[1][0] == 'lab.name'
    assert isinstance(nat[0][1], Terms)
    assert isinstance(nat[1][1], Terms)
    assert nat[0][1].to_dict() == {
        'terms': {
            'field': 'embedded.file_type',
            'missing': 'missing_file_type',
            'size': 999999
        }
    }
    assert nat[1][1].to_dict() == {
        'terms': {
            'size': 999999,
            'field': 'embedded.lab.name'
        }
    }


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_missing_matrix_query_factory_with_facets_add_matrix_aggregations(params_parser, dummy_request):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MissingMatrixQueryFactoryWithFacets(params_parser)
    mmqf.add_matrix_aggregations()
    expected = {
        'aggs': {
            'y': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.status'
                        },
                        'aggs': {
                            'name': {
                                'terms': {
                                    'size': 999999,
                                    'field': 'embedded.name'
                                },
                                'aggs': {
                                    'label': {
                                        'terms': {
                                            'size': 999999,
                                            'field': 'embedded.label'
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            'x': {
                'aggs': {
                    'label': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.label'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        'query': {
            'match_all': {}
        }
    }
    actual = mmqf.search.to_dict()
    assert all([e in actual for e in expected])
    assert actual['aggs']['y']['aggs']['status']['terms']['field'] == 'embedded.status'
    assert actual['aggs']['y']['aggs']['status']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['field'] == 'embedded.name'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['size'] == 999999
    assert actual['aggs']['x']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['x']['aggs']['label']['terms']['size'] == 999999
    assert len(actual['aggs']['y']['filter']['bool']['must']) == 2
    assert len(actual['aggs']['x']['filter']['bool']['must']) == 2
    assert 'missing' not in actual['aggs']['y']['aggs']['status']['terms']
    assert 'missing' not in  actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']
    assert 'missing' not in actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_missing_matrix_query_factory_with_facets_add_matrix_aggregations_with_default_value(params_parser, dummy_request):
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MissingMatrixQueryFactoryWithFacets(
        params_parser,
        matrix_definition_name='missing_matrix'
    )
    mmqf.add_matrix_aggregations()
    expected = {
        'aggs': {
            'y': {
                'aggs': {
                    'status': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.status'
                        },
                        'aggs': {
                            'name': {
                                'terms': {
                                    'size': 999999,
                                    'field': 'embedded.name'
                                },
                                'aggs': {
                                    'label': {
                                        'terms': {
                                            'size': 999999,
                                            'field': 'embedded.label'
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            'x': {
                'aggs': {
                    'label': {
                        'terms': {
                            'size': 999999,
                            'field': 'embedded.label'
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'terms': {
                                    'embedded.status': [
                                        'released'
                                    ]
                                }
                            },
                            {
                                'terms': {
                                    'embedded.@type': [
                                        'TestingSearchSchema'
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        'query': {
            'match_all': {}
        }
    }
    actual = mmqf.search.to_dict()
    assert all([e in actual for e in expected])
    assert actual['aggs']['y']['aggs']['status']['terms']['field'] == 'embedded.status'
    assert actual['aggs']['y']['aggs']['status']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['field'] == 'embedded.name'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['size'] == 999999
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']['size'] == 999999
    assert actual['aggs']['x']['aggs']['label']['terms']['field'] == 'embedded.label'
    assert actual['aggs']['x']['aggs']['label']['terms']['size'] == 999999
    assert len(actual['aggs']['y']['filter']['bool']['must']) == 2
    assert len(actual['aggs']['x']['filter']['bool']['must']) == 2
    assert 'missing' not in actual['aggs']['y']['aggs']['status']['terms']
    assert  actual['aggs']['y']['aggs']['status']['aggs']['name']['terms']['missing'] == 'default_name'
    assert 'missing' not in actual['aggs']['y']['aggs']['status']['aggs']['name']['aggs']['label']['terms']


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_multitype_missing_matrix_query_factory_with_facets_init(params_parser):
    from snosearch.queries import MultitypeMissingMatrixQueryFactoryWithFacets
    mmmqf = MultitypeMissingMatrixQueryFactoryWithFacets(params_parser)
    assert isinstance(mmmqf, MultitypeMissingMatrixQueryFactoryWithFacets)
    assert mmmqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_multitype_missing_matrix_query_factory_with_facets_parse_name_and_default_value_from_name(params_parser, dummy_request):
    from snosearch.queries import MultitypeMissingMatrixQueryFactoryWithFacets
    from elasticsearch_dsl.aggs import Terms
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    mmqf = MultitypeMissingMatrixQueryFactoryWithFacets(params_parser)
    name, default_value = mmqf._parse_name_and_default_value_from_name('perturbation_type')
    assert name == 'perturbation_type'
    assert default_value is None
    name, default_value = mmqf._parse_name_and_default_value_from_name(('perturbation_type', 'no_perturbation'))
    assert name == 'perturbation_type'
    assert default_value == 'no_perturbation'


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_audit_matrix_query_factory_with_facets_init(params_parser):
    from snosearch.queries import AuditMatrixQueryFactoryWithFacets
    amqf = AuditMatrixQueryFactoryWithFacets(params_parser)
    assert isinstance(amqf, AuditMatrixQueryFactoryWithFacets)
    assert amqf.params_parser == params_parser


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_audit_matrix_query_factory_with_facets_get_matrix_for_item_type(params_parser):
    from snosearch.queries import AuditMatrixQueryFactoryWithFacets
    amqf = AuditMatrixQueryFactoryWithFacets(params_parser)
    assert amqf._get_matrix_for_item_type('TestingSearchSchema') == {
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


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_audit_matrix_query_factory_with_facets_get_group_by_names(params_parser, dummy_request):
    from snosearch.queries import AuditMatrixQueryFactoryWithFacets
    dummy_request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
        '&limit=10&field=@id&field=accession&mode=picker'
    )
    amqf = AuditMatrixQueryFactoryWithFacets(params_parser)
    expected = [
        ('x', ['status']),
        ('audit.ERROR.category', ['audit.ERROR.category', 'status']),
        ('audit.NOT_COMPLIANT.category', ['audit.NOT_COMPLIANT.category', 'status']),
        ('audit.WARNING.category', ['audit.WARNING.category', 'status']),
        ('audit.INTERNAL_ACTION.category', ['audit.INTERNAL_ACTION.category', 'status'])
    ]
    actual = amqf._get_group_by_names()
    assert len(expected) == len(actual)
    assert all(e in actual for e in expected)    


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_init(params_parser):
    from snosearch.queries import TopHitsQueryFactory
    thqf = TopHitsQueryFactory(params_parser)
    assert isinstance(thqf, TopHitsQueryFactory)
    assert thqf.params_parser == params_parser


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_build_query(dummy_request):
    from snosearch.queries import TopHitsQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=ep300'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    thqf = TopHitsQueryFactory(params_parser)
    query = thqf.build_query()
    expected = {
        'size': 0,
        'query': {
            'bool': {
                'must': [
                    {
                        'query_string': {
                            'query': '(ep300)',
                            'fields': ['_all'],
                            'default_operator': 'AND'
                        }
                    }
                ],
                'filter': [
                    {
                        'bool': {
                            'must': [
                                {'terms': {'principals_allowed.view': ['system.Everyone']}},
                                {'terms': {'embedded.@type': []}}
                            ]
                        }
                    }
                ]
            }
        },
        'from': 0,
        'aggs': {
            'types': {
                'filter': {
                    'bool': {}
                },
                'aggs': {
                    'types': {
                        'terms': {
                            'field': 'embedded.@type',
                            'size': 10
                        },
                        'aggs': {
                            'max_score': {
                                'max': {
                                    'script': '_score'
                                }
                            },
                            'top_hits': {
                                'top_hits': {
                                    '_source': []
                                }
                            }
                        }
                    }
                }
            }
        },
        '_source': [
            'audit.*',
            'embedded.@id',
            'embedded.@type'
        ],
        'post_filter': {
            'bool': {}
        }
    }
    actual = query.to_dict()
    actual['aggs']['types']['aggs']['types']['aggs']['top_hits']['top_hits']['_source'] = []
    assert expected['aggs'] == actual['aggs']


@pytest.mark.parametrize(
    'dummy_request',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_build_query_with_filter(dummy_request):
    from snosearch.queries import TopHitsQueryFactory
    from snosearch.parsers import ParamsParser
    from pyramid.testing import DummyResource
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=ep300&type=TestingSearchSchema&status=released'
    )
    dummy_request.context = DummyResource()
    params_parser = ParamsParser(dummy_request)
    thqf = TopHitsQueryFactory(params_parser)
    query = thqf.build_query()
    actual = query.to_dict()
    actual['aggs']['types']['aggs']['types']['aggs']['top_hits']['top_hits']['_source'] = []
    expected = {
        'aggs': {
            'types': {
                'aggs': {
                    'types': {
                        'aggs': {
                            'top_hits': {
                                'top_hits': {
                                    '_source': []
                                }
                            },
                            'max_score': {
                                'max': {
                                    'script': '_score'
                                }
                            }
                        },
                        'terms': {
                            'field': 'embedded.@type',
                            'exclude': [],
                            'include': [],
                            'size': 10
                        }
                    }
                },
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}},
                            {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                        ]
                    }
                }
            }
        },
        'from': 0,
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'must': [
                                {'terms': {'principals_allowed.view': ['system.Everyone']}},
                                {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                            ]
                        }
                    }
                ],
                'must': [
                    {'query_string': {'fields': ['_all'], 'default_operator': 'AND', 'query': '(ep300)'}}
                ]
            }
        },
        '_source': ['audit.*', 'embedded.@id', 'embedded.@type', 'embedded.accession', 'embedded.status'],
        'size': 0,
        'post_filter': {
            'bool': {
                'must': [
                    {'terms': {'embedded.status': ['released']}},
                    {'terms': {'embedded.@type': ['TestingSearchSchema']}}
                ]
            }
        }
    }
    assert len(
        actual['aggs']['types']['filter']['bool']['must']
    ) == len(
        expected['aggs']['types']['filter']['bool']['must']
    )
    assert all(
        e in actual['aggs']['types']['filter']['bool']['must']
        for e in expected['aggs']['types']['filter']['bool']['must']
    )


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_make_max_aggregation(params_parser):
    from snosearch.queries import TopHitsQueryFactory
    th = TopHitsQueryFactory(params_parser)
    ma = th._make_max_aggregation()
    assert ma.to_dict() == {
        'max': {}
    }
    ma = th._make_max_aggregation(script='_source')
    assert ma.to_dict() == {
        'max': {'script': '_source'}
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_make_top_hits_aggregation(params_parser):
    from snosearch.queries import TopHitsQueryFactory
    th = TopHitsQueryFactory(params_parser)
    tha = th._make_top_hits_aggregation(
        size=3,
        source=['embedded.*']
    )
    assert tha.to_dict() == {
        'top_hits': {
            'size': 3,
            'source': ['embedded.*']
        }
    }


@pytest.mark.parametrize(
    'params_parser',
    integrations,
    indirect=True
)
def test_searches_queries_top_hits_query_factory_make_top_hits_by_type_aggregation(params_parser):
    from snosearch.queries import TopHitsQueryFactory
    th = TopHitsQueryFactory(params_parser)
    thbta = th._make_top_hits_by_type_aggregation(
    )
    actual = thbta.to_dict()
    source_actual = actual['aggs']['top_hits']['top_hits']['_source']
    source_expected = ['embedded.accession', 'embedded.@id', 'embedded.@type']
    assert all(e in source_actual for e in source_expected)
    assert len(source_actual) == len(source_expected)
    actual['aggs']['top_hits']['top_hits']['_source'] = []
    assert actual == {
        'terms': {
            'include': ['Experiment'],
            'size': 10,
            'field': 'embedded.@type'
        },
        'aggs': {
            'top_hits': {
                'top_hits': {
                    '_source': []
                }
            },
            'max_score': {
                'max': {
                    'script': '_score'
                }
            }
        }
    }


@pytest.mark.parametrize(
    'params_parser, dummy_request',
    [
        ('pyramid', 'pyramid'),
        ('flask', 'flask')
    ],
    indirect=True
)
def test_searches_queries_top_hits_query_factory_add_filtered_top_hits_aggregation(params_parser, dummy_request):
    from snosearch.queries import TopHitsQueryFactory
    dummy_request.environ['QUERY_STRING'] = (
        'searchTerm=blah&status=released'
    )
    th = TopHitsQueryFactory(params_parser)
    th.add_filtered_top_hits_aggregation()
    actual = th.search.to_dict()
    actual['aggs']['types']['aggs']['types']['aggs']['top_hits']['top_hits']['_source'] = []
    expected = {
        'query': {
            'match_all': {}
        }, 'aggs': {
            'types': {
                'filter': {
                    'bool': {
                        'must': [
                            {'terms': {'embedded.status': ['released']}}
                        ]
                    }
                },
                'aggs': {
                    'types': {
                        'terms': {
                            'field': 'embedded.@type',
                            'size': 10
                        },
                        'aggs': {
                            'max_score': {
                                'max': {
                                    'script': '_score'
                                }
                            },
                            'top_hits': {
                                'top_hits': {
                                    '_source': []
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    assert actual == expected
