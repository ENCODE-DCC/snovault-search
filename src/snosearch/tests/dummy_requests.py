from pyramid.request import Request
from snosearch.adapters.flask.requests import RequestAdapter
from snosearch.interfaces import JSONLD_CONTEXT
from werkzeug.datastructures import ImmutableOrderedMultiDict


class FlaskDummyRequestAdapter(RequestAdapter):

    def __setitem__(self, key, value):
        self._request.__class__.parameter_storage_class = ImmutableOrderedMultiDict
        environ = self._request.environ.copy()
        environ.update({key: value})
        self._request = self._request.__class__(environ)

    def __getitem__(self, key):
        return self._request.environ[key]

    @property
    def environ(self):
        return self

    @property
    def query_string(self):
        return self._request.query_string.decode('utf-8')

    @query_string.setter
    def query_string(self, value):
        self.__setitem__('QUERY_STRING', value)


class PyramidDummyRequest(Request):

        __parent__ = None
    
        @property
        def effective_principals(self):
            if self.environ.get('REMOTE_USER') == 'TEST_SUBMITTER':
                return ['group.submitter']
            return super().effective_principals

        def has_permission(self, action):
            principals = self.effective_principals
            acls = getattr(
                self.context,
                '__acl__',
                lambda: []
            )
            for principal in principals:
                for acl in acls():
                    if acl[1] == principal and acl[2] == action:
                        return acl[0]
            return False

        def route_path(self, context):
            if context == JSONLD_CONTEXT:
                    return '/terms/'
