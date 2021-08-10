from pyramid.httpexceptions import HTTPBadRequest


def get_default_exception():
    return HTTPBadRequest
