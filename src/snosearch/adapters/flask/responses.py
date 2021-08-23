from flask import Response


class ResponseAdapter(Response):

    @property
    def status_code(self):
        return super().status_code

    @status_code.setter
    def status_code(self, code):
        self.status = code

    @property
    def app_iter(self):
        return None

    @app_iter.setter
    def app_iter(self, generator):
        self.response = generator
