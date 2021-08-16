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

    def copy(self):
        return RequestAdapter(
            self._request.__class__(
                self._request.environ.copy()
            )
        )

    @property
    def effective_principals(self):
        return ['system.Everyone']

    def has_permission(self, action):
        return True

    def route_path(self, context):
        raise NotImplementedError
