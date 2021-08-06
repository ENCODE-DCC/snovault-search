import pytest


@pytest.fixture
def dummy_request():
    from pyramid.request import Request
    from pyramid.registry import Registry
    dummy_request = Request({})
    dummy_request.registry = Registry()
    return dummy_request
