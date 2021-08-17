import pytest


def test_adapters_responses_get_response_get_response():
    from snosearch.adapters.responses import ResponseFactory
    from snosearch.adapters.responses import get_response
    from pyramid.response import Response as PyramidResponse
    from flask import Response as FlaskResponse
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
        FlaskResponse
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
