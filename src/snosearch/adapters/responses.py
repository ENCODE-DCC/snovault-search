class ResponseFactory():
    def __init__(self, name=None):
        self.name = name

    def _get_response_from_pyramid(self):
        from pyramid.response import Response
        return Response()

    def _get_response_from_flask(self):
        from flask import Response
        from snosearch.adapters.flask.responses import ResponseAdapter
        return ResponseAdapter()

    def _maybe_get_response_from_pyramid(self):
        try:
            return self._get_response_from_pyramid()
        except ModuleNotFoundError:
            return None

    def _maybe_get_response_from_flask(self):
        try:
            return self._get_response_from_flask()
        except ModuleNotFoundError:
            return None

    def _get_response_by_name(self):
        if not self.name:
            return None
        if self.name == 'flask':
            return self._get_response_from_flask()
        return self._get_response_from_pyramid()

    def _get_response(self):
        return (
            self._get_response_by_name()
            or self._maybe_get_response_from_pyramid()
            or self._maybe_get_response_from_flask()
        )


def get_response():
    rf = ResponseFactory()
    return rf._get_response()
