import pytest


def test_adapters_responses_get_response_get_response():
    from snosearch.adapters.responses import ResponseFactory
    from snosearch.adapters.responses import get_response
    from pyramid.response import Response as PyramidResponse
    from flask import Response as FlaskResponse
    from snosearch.adapters.flask.responses import ResponseAdapter as FlaskResponseAdapter
    rf = ResponseFactory('pyramid')
    assert isinstance(
        rf._get_response_by_name(),
        PyramidResponse
    )
    rf = ResponseFactory('flask')
    assert isinstance(
        rf._get_response_by_name(),
        FlaskResponse
    )
    rf = ResponseFactory()
    assert rf._get_response_by_name() is None
    assert isinstance(
        rf._get_response(),
        PyramidResponse
    )
    def raise_error():
        raise ModuleNotFoundError
    rf._get_response_from_pyramid = lambda: raise_error()
    assert isinstance(
        rf._get_response(),
        FlaskResponseAdapter
    )
    rf = ResponseFactory()
    rf._get_response_from_flask = lambda: raise_error()
    assert isinstance(
        rf._get_response(),
        PyramidResponse
    )
    assert rf._maybe_get_response_from_flask() is None
    assert isinstance(
        get_response(),
        PyramidResponse
    )


def test_adapters_responses_flask_response_adapter_methods():
    from flask import Response
    from snosearch.adapters.flask.responses import ResponseAdapter
    r = ResponseAdapter()
    assert r.status_code == 200
    r.status_code = 404
    assert r.status_code == 404
    r.status_code = 200
    assert r.status == '200 OK'
    r.registry = {'a': 'b'}
    assert r.registry == {'a': 'b'}
    assert r.app_iter is None
    r.app_iter = (x for x in ['a', 'b', 'c'])
    assert r.content_type == 'text/html; charset=utf-8'
    assert r.data == b'abc'
    assert isinstance(r, Response)
