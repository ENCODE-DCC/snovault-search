import pytest


integrations = [
    'pyramid',
    'flask',
]


@pytest.fixture()
def dummy_parent(request, pyramid_dummy_request, flask_dummy_request):
    if hasattr(request, 'param') and request.param == 'flask':
        dummy_request = flask_dummy_request
    else:
        dummy_request = pyramid_dummy_request
    from pyramid.testing import DummyResource
    from pyramid.security import Allow
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
    from snosearch.interfaces import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch()
    dummy_request.context = DummyResource()
    dummy_request.context.__acl__ = lambda: [(Allow, 'group.submitter', 'search_audit')]
    class DummyParent():
        def __init__(self):
            self._meta = {}
            self.response = {}
    dp = DummyParent()
    pp = ParamsParser(dummy_request)
    dp._meta = {
        'params_parser': pp,
        'query_builder': AbstractQueryFactory(pp)
    }
    return dp


def test_searches_fields_response_field_init():
    from snosearch.fields import ResponseField
    rf = ResponseField()
    assert isinstance(rf, ResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_response_field_get_params_parser(dummy_parent):
    from snosearch.fields import ResponseField
    from snosearch.parsers import ParamsParser
    rf = ResponseField()
    rf.parent = dummy_parent
    assert isinstance(rf.get_params_parser(), ParamsParser)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_response_field_get_request(dummy_parent):
    from snosearch.fields import ResponseField
    from pyramid.request import Request as PyramidRequest
    from .dummy_requests import FlaskDummyRequestAdapter as FlaskRequest
    rf = ResponseField()
    rf.parent = dummy_parent
    assert (
        isinstance(rf.get_request(), PyramidRequest)
        or isinstance(rf.get_request(), FlaskRequest)
    )


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_response_field_render(dummy_parent):
    from snosearch.fields import ResponseField
    rf = ResponseField()
    with pytest.raises(NotImplementedError):
        rf.render()


def test_searches_fields_basic_search_response_field_init():
    from snosearch.fields import BasicSearchResponseField
    brf = BasicSearchResponseField()
    assert isinstance(brf, BasicSearchResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_response_build_query(dummy_parent):
    from snosearch.fields import BasicSearchResponseField
    from elasticsearch_dsl import Search
    brf = BasicSearchResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query, Search)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_response_register_query(dummy_parent):
    from snosearch.fields import BasicSearchResponseField
    from snosearch.queries import BasicSearchQueryFactory
    brf = BasicSearchResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query_builder, BasicSearchQueryFactory)
    brf._register_query()
    assert isinstance(brf.get_query_builder(), BasicSearchQueryFactory)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_response_execute_query(dummy_parent, mocker):
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from snosearch.fields import BasicSearchResponseField
    brf = BasicSearchResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    brf._execute_query()
    assert Search.execute.call_count == 1


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_response_format_results(dummy_parent, mocker):
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from snosearch.fields import BasicSearchResponseField
    brf = BasicSearchResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    brf._execute_query()
    assert Search.execute.call_count == 1
    assert '@graph' not in brf.response
    brf._format_results()
    assert '@graph' in brf.response
    assert list(brf.response['@graph']) == []


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_response_render(dummy_parent, mocker):
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from snosearch.fields import BasicSearchResponseField
    brf = BasicSearchResponseField()
    brf.parent = dummy_parent
    assert '@graph' not in brf.response
    brf.render(parent=dummy_parent)
    assert Search.execute.call_count == 1
    assert '@graph' in brf.response
    assert list(brf.response['@graph']) == []


def test_searches_fields_basic_search_with_facets_response_field_init():
    from snosearch.fields import BasicSearchWithFacetsResponseField
    brf = BasicSearchWithFacetsResponseField()
    assert isinstance(brf, BasicSearchWithFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_with_facets_response_build_query(dummy_parent):
    from snosearch.fields import BasicSearchWithFacetsResponseField
    from elasticsearch_dsl import Search
    brf = BasicSearchWithFacetsResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query, Search)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_with_facets_response_register_query(dummy_parent):
    from snosearch.fields import BasicSearchWithFacetsResponseField
    from snosearch.queries import BasicSearchQueryFactoryWithFacets
    brf = BasicSearchWithFacetsResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query_builder, BasicSearchQueryFactoryWithFacets)
    brf._register_query()
    assert isinstance(brf.get_query_builder(), BasicSearchQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_with_facets_response_execute_query(dummy_parent, mocker):
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from snosearch.fields import BasicSearchWithFacetsResponseField
    brf = BasicSearchWithFacetsResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    brf._execute_query()
    assert Search.execute.call_count == 1


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_with_facets_response_format_results(dummy_parent, mocker):
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = mocker.MagicMock()
    from snosearch.fields import BasicSearchWithFacetsResponseField
    brf = BasicSearchWithFacetsResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    brf._execute_query()
    assert Search.execute.call_count == 1
    assert '@graph' not in brf.response
    assert 'facets' not in brf.response
    assert 'total' not in brf.response
    brf._format_results()
    assert '@graph' in brf.response
    assert 'facets' in brf.response
    assert 'total' in brf.response


def test_searches_fields_basic_search_without_facets_response_field_init():
    from snosearch.fields import BasicSearchWithoutFacetsResponseField
    brf = BasicSearchWithoutFacetsResponseField()
    assert isinstance(brf, BasicSearchWithoutFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_search_without_facets_response_build_query(dummy_parent):
    from snosearch.fields import BasicSearchWithoutFacetsResponseField
    from elasticsearch_dsl import Search
    brf = BasicSearchWithoutFacetsResponseField()
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query, Search)


def test_searches_fields_cached_facets_response_field_init():
    from snosearch.fields import CachedFacetsResponseField
    cfrf = CachedFacetsResponseField()
    assert isinstance(cfrf, CachedFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_cached_facets_response_field_build_query(dummy_parent):
    from snosearch.fields import CachedFacetsResponseField
    from elasticsearch_dsl import Search
    cfrf = CachedFacetsResponseField()
    cfrf.parent = dummy_parent
    cfrf._build_query()
    assert isinstance(cfrf.query, Search)


def test_searches_fields_collection_search_with_facets_response_field_init():
    from snosearch.fields import CollectionSearchWithFacetsResponseField
    crf = CollectionSearchWithFacetsResponseField()
    assert isinstance(crf, CollectionSearchWithFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_collection_search_with_facets_response_build_query(dummy_parent):
    from snosearch.fields import CollectionSearchWithFacetsResponseField
    from snosearch.fields import CollectionSearchQueryFactoryWithFacets
    context = dummy_parent._meta['params_parser']._request.registry['types']['TestingSearchSchema']
    dummy_parent._meta['params_parser']._request.context = context
    from elasticsearch_dsl import Search
    crf = CollectionSearchWithFacetsResponseField()
    crf.parent = dummy_parent
    crf._build_query()
    assert isinstance(crf.query, Search)
    assert isinstance(crf.query_builder, CollectionSearchQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_report_with_facets_response_build_query(dummy_parent):
    from snosearch.fields import BasicReportWithFacetsResponseField
    from snosearch.queries import BasicReportQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    brf = BasicReportWithFacetsResponseField()
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query, Search)
    assert isinstance(brf.query_builder, BasicReportQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_report_without_facets_response_build_query(dummy_parent):
    from snosearch.fields import BasicReportWithoutFacetsResponseField
    from snosearch.queries import BasicReportQueryFactoryWithoutFacets
    from elasticsearch_dsl import Search
    brf = BasicReportWithoutFacetsResponseField()
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    brf.parent = dummy_parent
    brf._build_query()
    assert isinstance(brf.query, Search)
    assert isinstance(brf.query_builder, BasicReportQueryFactoryWithoutFacets)


def test_searches_fields_raw_search_with_aggs_response_field_init():
    from snosearch.fields import RawSearchWithAggsResponseField
    rs = RawSearchWithAggsResponseField()
    assert isinstance(rs, RawSearchWithAggsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_raw_search_with_aggs_response_field_maybe_scan_over_results(dummy_parent, mocker):
    from snosearch.fields import BasicSearchQueryFactoryWithFacets
    from snosearch.fields import RawSearchWithAggsResponseField
    from snosearch.mixins import RawHitsToGraphMixin
    from snosearch.responses import RawQueryResponseWithAggs
    rs = RawSearchWithAggsResponseField()
    rs.parent = dummy_parent
    rs._build_query()
    rs.results = RawQueryResponseWithAggs(
        results={},
        query_builder={}
    )
    rs.response = {'hits': {'hits': []}}
    mocker.patch.object(RawHitsToGraphMixin, 'to_graph')
    mocker.patch.object(BasicSearchQueryFactoryWithFacets, '_should_scan_over_results')
    BasicSearchQueryFactoryWithFacets._should_scan_over_results.return_value = False
    rs._maybe_scan_over_results()
    assert RawHitsToGraphMixin.to_graph.call_count == 0
    BasicSearchQueryFactoryWithFacets._should_scan_over_results.return_value = True
    rs._maybe_scan_over_results()
    assert RawHitsToGraphMixin.to_graph.call_count == 1


def test_searches_fields_title_response_field_init():
    from snosearch.fields import TitleResponseField
    tf = TitleResponseField()
    assert isinstance(tf, TitleResponseField)


def test_searches_fields_title_field_title_value():
    from snosearch.fields import TitleResponseField
    tf = TitleResponseField(title='Search')
    rtf = tf.render()
    assert rtf == {'title': 'Search'}


def test_searches_fields_type_response_field():
    from snosearch.fields import TypeResponseField
    tr = TypeResponseField(at_type=['Snowflake'])
    assert isinstance(tr, TypeResponseField)
    assert tr.render() == {'@type': ['Snowflake']}


def test_searches_fields_context_response_field(dummy_parent):
    from snosearch.fields import ContextResponseField
    cr = ContextResponseField()
    assert isinstance(cr, ContextResponseField)
    assert cr.render(parent=dummy_parent) == {'@context': '/terms/'}


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_id_response_field(dummy_parent):
    from snosearch.fields import IDResponseField
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
    )
    ir = IDResponseField()
    assert isinstance(ir, IDResponseField)
    assert ir.render(parent=dummy_parent) == {
        '@id': '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
    }


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_all_response_field_init(dummy_parent):
    from snosearch.fields import AllResponseField
    ar = AllResponseField()
    assert isinstance(ar, AllResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_all_response_field_get_limit(dummy_parent):
    from snosearch.fields import AllResponseField
    ar = AllResponseField()
    ar.parent = dummy_parent
    assert ar._get_limit() == [('limit', 25)]
    ar.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=99'
    )
    assert ar._get_limit() == [('limit', '99')]


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_all_response_field_get_qs_with_limit_all(dummy_parent):
    from snosearch.fields import AllResponseField
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=99'
    )
    assert ar._get_qs_with_limit_all() == (
        'type=Experiment&assay_title=Histone+ChIP-seq'
        '&award.project=Roadmap&limit=all'
    )


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_all_response_field_maybe_add_all(dummy_parent):
    from snosearch.fields import AllResponseField
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar._maybe_add_all()
    assert 'all' not in ar.response
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar.parent.response.update({'total': 150})
    ar._maybe_add_all()
    assert 'all' in ar.response
    assert ar.response['all'] == '/dummy?limit=all'
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar.parent.response.update({'total': 150})
    ar.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=99'
    )
    ar._maybe_add_all()
    assert ar.response['all'] == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq'
        '&award.project=Roadmap&limit=all'
    )
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar.parent.response.update({'total': 150})
    ar.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all'
    )
    ar._maybe_add_all()
    assert 'all' not in ar.response
    ar = AllResponseField()
    ar.parent = dummy_parent
    ar.parent.response.update({'total': 150})
    ar.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=200'
    )
    ar._maybe_add_all()
    assert 'all' not in ar.response


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_notification_response_field_init(dummy_parent):
    from snosearch.fields import NotificationResponseField
    nr = NotificationResponseField()
    assert isinstance(nr, NotificationResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_notification_response_field_results_found(dummy_parent):
    from snosearch.fields import NotificationResponseField
    nr = NotificationResponseField()
    nr.parent = dummy_parent
    assert not nr._results_found()
    nr.parent.response.update({'total': 0})
    assert not nr._results_found()
    nr.parent.response.update({'total': 150})
    assert nr._results_found()


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_notification_response_field_set_notification(dummy_parent):
    from snosearch.fields import NotificationResponseField
    nr = NotificationResponseField()
    nr.parent = dummy_parent
    assert 'notification' not in nr.response
    nr._set_notification('lots of results')
    assert nr.response['notification'] == 'lots of results'


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_notification_response_field_set_status_code(dummy_parent):
    from snosearch.fields import NotificationResponseField
    nr = NotificationResponseField()
    nr.parent = dummy_parent
    assert nr.parent._meta['params_parser']._request.response.status_code == 200
    nr._set_status_code(404)
    assert nr.parent._meta['params_parser']._request.response.status_code == 404


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_notification_response_field_render(dummy_parent):
    from snosearch.fields import NotificationResponseField
    nr = NotificationResponseField()
    dummy_parent.response['total'] = 123
    nr.render(parent=dummy_parent)
    assert nr.parent._meta['params_parser']._request.response.status_code == 200
    del dummy_parent.response['total']
    nr.render(parent=dummy_parent)
    assert nr.parent._meta['params_parser']._request.response.status_code == 404
    assert dummy_parent.response == {}


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_init(dummy_parent):
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    assert isinstance(frf, FiltersResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_get_filters_and_search_terms_from_query_string(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    frf.parent = dummy_parent
    expected = [
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('restricted!', '*'),
        ('type', 'Experiment'),
        ('searchTerm', 'ctcf')
    ]
    actual = frf._get_filters_and_search_terms_from_query_string()
    assert len(actual) == len(expected)
    assert all([e in actual for e in expected])


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_get_path_qs_without_filter(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    frf.parent = dummy_parent
    assert frf._get_path_qs_without_filter('type', 'Experiment') == (
        '/dummy?assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all'
        '&frame=embedded&restricted%21=%2A&searchTerm=ctcf'
    )
    assert frf._get_path_qs_without_filter('searchTerm', 'ctcf') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all'
        '&frame=embedded&restricted%21=%2A'
    )
    assert frf._get_path_qs_without_filter('searchTerm', 'ctcaf') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all'
        '&frame=embedded&restricted%21=%2A&searchTerm=ctcf'
    )
    assert frf._get_path_qs_without_filter('restricted!', '*') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all'
        '&frame=embedded&searchTerm=ctcf'
    )


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_get_path_qs_without_filter_malformed_query(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    frf.parent = dummy_parent
    assert frf._get_path_qs_without_filter('files.file_type', '') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf'
    )
    assert frf._get_path_qs_without_filter('', '') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf'
    )
    assert frf._get_path_qs_without_filter('', '*') == (
        '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf'
    )


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_make_filter(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    frf.parent = dummy_parent
    frf._make_filter('type', 'Experiment')
    assert frf.filters[0] == {
        'field': 'type',
        'remove': '/dummy?assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf',
        'term': 'Experiment'
    }


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_filters_response_field_make_filters(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import FiltersResponseField
    frf = FiltersResponseField()
    frf.parent = dummy_parent
    frf._make_filters()
    expected = [
        {
            'remove': '/dummy?type=Experiment&award.project=Roadmap&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf',
            'field': 'assay_title',
            'term': 'Histone ChIP-seq'
        },
        {
            'remove': '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf',
            'field': 'award.project',
            'term': 'Roadmap'
        },
        {
            'remove': '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all&frame=embedded&searchTerm=ctcf',
            'field': 'restricted!',
            'term': '*'
        },
        {
            'remove': '/dummy?assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all&frame=embedded&restricted%21=%2A&searchTerm=ctcf',
            'field': 'type',
            'term': 'Experiment'
        },
        {
            'remove': '/dummy?type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap&limit=all&frame=embedded&restricted%21=%2A',
            'field': 'searchTerm',
            'term': 'ctcf'
        }
    ]
    actual = frf.filters
    assert len(actual) == len(expected)
    assert all([e in actual for e in expected])


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_clear_filter_response_field_get_search_term_or_types_from_query_string(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import ClearFiltersResponseField
    cfr = ClearFiltersResponseField()
    cfr.parent = dummy_parent
    search_term_or_types = cfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('searchTerm', 'ctcf')]
    cfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    search_term_or_types = cfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('type', 'Experiment')]


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_type_only_clear_filter_response_field_get_search_term_or_types_from_query_string(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import TypeOnlyClearFiltersResponseField
    tcfr = TypeOnlyClearFiltersResponseField()
    tcfr.parent = dummy_parent
    search_term_or_types = tcfr._get_search_term_or_types_from_query_string()
    # Matrix/report clear filters should always always returns types.
    assert search_term_or_types == [('type', 'Experiment')]
    tcfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    search_term_or_types = tcfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('type', 'Experiment')]


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_clear_filter_response_field_get_path_qs_with_no_filters(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from snosearch.fields import ClearFiltersResponseField
    cfr = ClearFiltersResponseField()
    cfr.parent = dummy_parent
    path = cfr._get_path_qs_with_no_filters()
    assert path == '/dummy?searchTerm=ctcf'


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_clear_filter_response_field_add_clear_filters(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    from snosearch.fields import ClearFiltersResponseField
    cfr = ClearFiltersResponseField()
    cfr.parent = dummy_parent
    cfr._add_clear_filters()
    assert cfr.response['clear_filters'] == '/dummy?type=Experiment'


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_collection_clear_filter_response_field_get_search_term_or_types_from_query_string(dummy_parent):
    from snosearch.queries import CollectionSearchQueryFactoryWithFacets
    from snosearch.fields import CollectionClearFiltersResponseField
    context = dummy_parent._meta['params_parser']._request.registry['types']['TestingSearchSchema']
    dummy_parent._meta['params_parser']._request.context = context
    dummy_parent._meta['query_builder'] = CollectionSearchQueryFactoryWithFacets(dummy_parent._meta['params_parser'])
    ccfr = CollectionClearFiltersResponseField()
    ccfr.parent = dummy_parent
    assert ccfr._get_search_term_or_types_from_query_string() == [
        ('type', 'TestingSearchSchema')
    ]


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_collection_clear_filter_response_field_get_path_qs_with_no_filters(dummy_parent):
    from snosearch.queries import CollectionSearchQueryFactoryWithFacets
    from snosearch.fields import CollectionClearFiltersResponseField
    context = dummy_parent._meta['params_parser']._request.registry['types']['TestingSearchSchema']
    dummy_parent._meta['params_parser']._request.context = context
    dummy_parent._meta['query_builder'] = CollectionSearchQueryFactoryWithFacets(dummy_parent._meta['params_parser'])
    ccfr = CollectionClearFiltersResponseField()
    ccfr.parent = dummy_parent
    assert ccfr._get_path_qs_with_no_filters() == '/search/?type=TestingSearchSchema'


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_debug_query_response_field(dummy_parent, mocker):
    from snosearch.queries import AbstractQueryFactory
    mocker.patch.object(AbstractQueryFactory, '_get_index')
    AbstractQueryFactory._get_index.return_value = 'snovault-resources'
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&debug=true'
    )
    dummy_parent._meta['query_builder'].add_post_filters()
    from snosearch.fields import DebugQueryResponseField
    dbr = DebugQueryResponseField()
    r = dbr.render(parent=dummy_parent)
    assert 'query' in r['debug']['raw_query']
    assert 'post_filter' in r['debug']['raw_query']


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_column_response_field(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema'
    )
    from snosearch.fields import ColumnsResponseField
    crf = ColumnsResponseField()
    r = crf.render(parent=dummy_parent)
    assert r['columns'] == {
        '@id': {'title': 'ID'},
        'accession': {'title': 'Accession'},
        'status': {'title': 'Status'}
    }


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_sort_response_field_remove_prefix(dummy_parent):
    from snosearch.fields import SortResponseField
    srf = SortResponseField()
    rp = srf._remove_prefix([{'embedded.x': {'order': 'desc'}}, {'embedded.y': {'order': 'asc'}}])
    assert rp == {'x': {'order': 'desc'}, 'y': {'order': 'asc'}}


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_sort_response_field_maybe_add_sort(dummy_parent):
    from snosearch.fields import SortResponseField
    from elasticsearch_dsl import Search
    s = Search().from_dict(
        {'query': {'match_all': {}}, 'sort': [{'embedded.y': {'order': 'desc'}}]}
    )
    dummy_parent._meta['query_builder'].search = s
    srf = SortResponseField()
    srf.parent = dummy_parent
    srf._maybe_add_sort()
    assert dict(srf.response['sort']) == {'y': {'order': 'desc'}}


def test_searches_fields_raw_matrix_with_aggs_response_field_init():
    from snosearch.fields import RawMatrixWithAggsResponseField
    rm = RawMatrixWithAggsResponseField()
    assert isinstance(rm, RawMatrixWithAggsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_raw_matrix_with_aggs_response_field_build_query(dummy_parent):
    from snosearch.fields import RawMatrixWithAggsResponseField
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    rmf = RawMatrixWithAggsResponseField()
    rmf.parent = dummy_parent
    rmf._build_query()
    assert isinstance(rmf.query, Search)
    assert isinstance(rmf.query_builder, BasicMatrixQueryFactoryWithFacets)


def test_searches_fields_raw_top_hits_response_field_init():
    from snosearch.fields import RawTopHitsResponseField
    rth = RawTopHitsResponseField()
    assert isinstance(rth, RawTopHitsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_raw_top_hits_response_field_build_query(dummy_parent):
    from snosearch.fields import RawTopHitsResponseField
    from snosearch.queries import TopHitsQueryFactory
    from elasticsearch_dsl import Search
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    rth = RawTopHitsResponseField()
    rth.parent = dummy_parent
    rth._build_query()
    assert isinstance(rth.query, Search)
    assert isinstance(rth.query_builder, TopHitsQueryFactory)


def test_searches_fields_basic_matrix_with_facets_response_field_init():
    from snosearch.fields import BasicMatrixWithFacetsResponseField
    bmwf = BasicMatrixWithFacetsResponseField()
    assert isinstance(bmwf, BasicMatrixWithFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_matrix_with_facets_response_field_build_query(dummy_parent):
    from snosearch.fields import BasicMatrixWithFacetsResponseField
    from snosearch.queries import BasicMatrixQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    bmwf = BasicMatrixWithFacetsResponseField()
    bmwf.parent = dummy_parent
    bmwf._build_query()
    assert isinstance(bmwf.query, Search)
    assert isinstance(bmwf.query_builder, BasicMatrixQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_basic_matrix_with_facets_response_field_execute_query(dummy_parent, mocker):
    from snosearch.fields import BasicMatrixWithFacetsResponseField
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    bmwf = BasicMatrixWithFacetsResponseField()
    bmwf.parent = dummy_parent
    bmwf._build_query()
    bmwf._execute_query()
    assert Search.execute.call_count == 1


def test_searches_fields_missing_matrix_with_facets_response_field_init():
    from snosearch.fields import MissingMatrixWithFacetsResponseField
    mmwf = MissingMatrixWithFacetsResponseField()
    assert isinstance(mmwf, MissingMatrixWithFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_missing_matrix_with_facets_response_field_build_query(dummy_parent):
    from snosearch.fields import MissingMatrixWithFacetsResponseField
    from snosearch.queries import MissingMatrixQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    mmwf = MissingMatrixWithFacetsResponseField()
    mmwf.parent = dummy_parent
    mmwf._build_query()
    assert isinstance(mmwf.query, Search)
    assert isinstance(mmwf.query_builder, MissingMatrixQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_search_base_get_search_base(dummy_parent):
    from snosearch.fields import SearchBaseResponseField
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    sb = SearchBaseResponseField()
    sb.parent = dummy_parent
    assert sb._get_search_base() == '/search/?type=TestingSearchSchema&status=released'
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        ''
    )
    sb = SearchBaseResponseField()
    sb.parent = dummy_parent
    assert sb._get_search_base() == '/search/'
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        ''
    )
    sb = SearchBaseResponseField(search_base='/different-search/')
    sb.parent = dummy_parent
    assert sb._get_search_base() == '/different-search/'


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_search_base_render(dummy_parent):
    from snosearch.fields import SearchBaseResponseField
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    sb = SearchBaseResponseField()
    assert sb.render(
        parent=dummy_parent
    ) == {'search_base': '/search/?type=TestingSearchSchema&status=released'}


def test_searches_fields_audit_matrix_with_facets_response_field_init():
    from snosearch.fields import AuditMatrixWithFacetsResponseField
    amwf = AuditMatrixWithFacetsResponseField()
    assert isinstance(amwf, AuditMatrixWithFacetsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_audit_matrix_with_facets_response_field_build_query(dummy_parent):
    from snosearch.fields import AuditMatrixWithFacetsResponseField
    from snosearch.queries import AuditMatrixQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    amwf = AuditMatrixWithFacetsResponseField()
    amwf.parent = dummy_parent
    amwf._build_query()
    assert isinstance(amwf.query, Search)
    assert isinstance(amwf.query_builder, AuditMatrixQueryFactoryWithFacets)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_audit_matrix_with_facets_response_field_execute_query(dummy_parent, mocker):
    from snosearch.fields import AuditMatrixWithFacetsResponseField
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    amwf = AuditMatrixWithFacetsResponseField()
    amwf.parent = dummy_parent
    amwf._build_query()
    amwf._execute_query()
    assert Search.execute.call_count == 1


def test_searches_fields_facet_groups_response_field_init():
    from snosearch.fields import FacetGroupsResponseField
    fg = FacetGroupsResponseField()
    assert isinstance(fg, FacetGroupsResponseField)


@pytest.mark.parametrize(
    'dummy_parent',
    integrations,
    indirect=True
)
def test_searches_fields_facet_groups_get_facet_groups(dummy_parent):
    from snosearch.fields import FacetGroupsResponseField
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=TestingSearchSchema&status=released'
    )
    fg = FacetGroupsResponseField()
    fg.parent = dummy_parent
    assert fg._get_facet_groups() == [
        {
            'title': 'Test group',
            'name': 'TestingSearchSchema',
            'facet_fields': [
                'status',
                'name'
            ]
        }
    ]
