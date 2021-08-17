import pytest


def test_searches_adapters_flask_requests_args_adapters_init():
    from snosearch.adapters.flask.requests import ArgsAdapter
    from werkzeug.datastructures import MultiDict
    aa = ArgsAdapter(MultiDict())
    assert isinstance(aa, ArgsAdapter)


def test_searches_adapters_flask_requests_args_adapters_items():
    from snosearch.adapters.flask.requests import ArgsAdapter
    from werkzeug.datastructures import MultiDict
    aa = ArgsAdapter(MultiDict([('a', 'b'), ('a', 'c')]))
    assert list(aa.items()) == [('a', 'b'), ('a', 'c')]


def test_searches_adapters_flask_requests_request_adapter_init():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    request = Request({})
    ra = RequestAdapter(request)
    assert isinstance(ra, RequestAdapter)


def test_searches_adapters_flask_requests_request_has_properties():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    request = Request({'PATH_INFO': '/xyz/', 'QUERY_STRING': 'abc=123'})
    ra = RequestAdapter(request)
    assert ra.has_permission('xyz')
    with pytest.raises(NotImplementedError):
        ra.route_path({})
    assert ra.path_qs == '/xyz/?abc=123'
    assert ra.path == '/xyz/'
    assert ra.effective_principals == ['system.Everyone']



def test_searches_adapters_flask_requests_request_adapter_params():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    request = Request(
        {
            'QUERY_STRING':
            'type=Experiment&type=RNAExpression&field=status&files.file_type=bed+bed3%2B'
            '&accession!=ABC'
        }
    )
    ra = RequestAdapter(request)
    assert list(ra.params.items()) == [
        ('type', 'Experiment'),
        ('type', 'RNAExpression'),
        ('field', 'status'),
        ('files.file_type', 'bed bed3+'),
        ('accession!', 'ABC')
    ]


def test_searches_adapters_flask_request_works_with_params_parsers():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    from snosearch.parsers import ParamsParser
    request = Request(
        {
            'QUERY_STRING': 'type!=Experiment'
        }
    )
    pp = ParamsParser(RequestAdapter(request))
    assert 'type!' in pp._request.params
    assert pp.is_param('type!', 'Experiment')
    assert not pp.is_param('type', 'RNAExpression')
    assert pp.get_filters_by_condition() == [
        ('type!', 'Experiment')
    ]


def test_searches_adapters_flask_request_works_with_params_parser_get_filters_by_condition():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    from snosearch.parsers import ParamsParser
    request = Request(
        {
            'QUERY_STRING': 'type=Experiment&type=File&field=status'
        }
    )
    pp = ParamsParser(RequestAdapter(request))
    assert pp.get_filters_by_condition(
        key_and_value_condition=lambda k, _: k == 'field'
    ) == [
        ('field', 'status')
    ]
    assert pp.get_filters_by_condition(
        key_and_value_condition=lambda k, _: k == 'type'
    ) == [
        ('type', 'Experiment'),
        ('type', 'File')
    ]
    assert pp.get_search_term_filters() == []
    assert pp.get_must_match_filters() == [
        ('type', 'Experiment'),
        ('type', 'File'),
        ('field', 'status')
    ]
