class ArgsAdapter:

    def __init__(self, args):
        self.args = args

    def __iter__(self):
        return self.args.__iter__()

    def items(self):
        return self.args.items(multi=True)

    def getall(self, key):
        return self.args.getlist(key)


class RequestAdapter:

    __parent__ = None

    def __init__(self, request):
        self._request = request

    @property
    def params(self):
        return ArgsAdapter(
            self._request.args
        )

    def copy(self, environ=None):
        return RequestAdapter(
            self._request.__class__(
                environ or self._request.environ.copy()
            )
        )

    @property
    def effective_principals(self):
        return ['system.Everyone']

    def has_permission(self, action):
        return True

    def route_path(self, context):
        raise NotImplementedError

    @property
    def path_qs(self):
        return self._request.full_path

    @property
    def path(self):
        return self._request.path

    @property
    def query_string(self):
        return self._request.query_string.decode('utf-8')

    @query_string.setter
    def query_string(self, query_string):
        environ = self._request.environ.copy()
        environ.update(
            {
                'QUERY_STRING': query_string,
            }
        )
        self._request = self.copy(
            environ=environ
        )._request
