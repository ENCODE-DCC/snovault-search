def flask_exception_adapter(error):
    def wrapper(explanation):
        return error(explanation)
    return wrapper


class BadRequestFactory():

    def __init__(self, name=None):
        self.name = name

    def _get_exception_from_pyramid(self):
        from pyramid.httpexceptions import HTTPBadRequest
        return HTTPBadRequest

    def _maybe_get_exception_from_pyramid(self):
        try:
            return self._get_exception_from_pyramid()
        except ModuleNotFoundError:
            return None

    def _get_exception_from_flask(self):
        from werkzeug.exceptions import BadRequest
        return flask_exception_adapter(BadRequest)

    def _maybe_get_exception_from_flask(self):
        try:
            return self._get_exception_from_flask()
        except ModuleNotFoundError:
            return None

    def _get_exception_by_name(self):
        if not self.name:
            return None
        if self.name == 'flask':
            return self._get_exception_from_flask()
        return self._get_exception_from_pyramid()

    def _get_bad_request(self):
        return (
            self._get_exception_by_name()
            or self._maybe_get_exception_from_pyramid()
            or self._maybe_get_exception_from_flask()
        )


def get_default_exception(name=None):
    br = BadRequestFactory(name)
    return br._get_bad_request()
