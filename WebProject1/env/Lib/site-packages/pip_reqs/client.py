from pip import _internal  # NOQA: Needed to make the _vendor import works.
from pip._vendor.requests import Session


class CompilationError(Exception):
    pass


class ResolutionError(Exception):
    pass


class WheelsproxyClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = Session()

    def compile(self, requirements_in):
        r = self.session.post(
            self.base_url + "+compile/", data=requirements_in
        )
        if r.status_code >= 400 and r.status_code < 500:
            raise CompilationError(r.text)
        r.raise_for_status()
        return r.text

    def resolve(self, compiled_reqs):
        r = self.session.post(self.base_url + "+resolve/", data=compiled_reqs)
        if r.status_code >= 400 and r.status_code < 500:
            raise ResolutionError(r.text)
        r.raise_for_status()
        return r.text
