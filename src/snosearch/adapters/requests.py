from pyramid.request import Request
from snosearch.interfaces import JSONLD_CONTEXT


class DummyRequest(Request):

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
            return super().route_path(context)
