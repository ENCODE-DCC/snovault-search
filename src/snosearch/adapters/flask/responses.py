class ResponseAdapter:

    def __init__(self, response):
        # Avoid calling setattr.
        self.__dict__['_response'] = response

    # Emulates inheritance without requiring
    # concrete base class.
    def __getattr__(self, attr):
        return getattr(self._response, attr)

    def __setattr__(self, attr, value):
        # Use local properties if exist.
        if attr in ResponseAdapter.__dict__:
            return super().__setattr__(attr, value)
        else:
            # Delegate to response object.
            return setattr(self._response, attr, value)

    @property
    def status_code(self):
        return self._response.status_code

    @status_code.setter
    def status_code(self, code):
        self.status = code

    @property
    def app_iter(self):
        return None

    @app_iter.setter
    def app_iter(self, generator):
        self.response = generator
