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


def test_searches_adapters_requests_request_adapter_init():
    from snosearch.adapters.flask.requests import RequestAdapter
    from flask import Request
    request = Request({})
    ra = RequestAdapter(request)
    assert isinstance(ra, RequestAdapter)


def test_searches_adapters_requests_request_has_properties():
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
