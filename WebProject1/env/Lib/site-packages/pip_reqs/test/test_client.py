# fmt: off
from pip_reqs import client  # isort:skip
# fmt: on

import sys

import mock
import pytest
from pip._vendor.requests.exceptions import HTTPError
from pip._vendor.requests.models import Response


PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
else:
    text_type = unicode  # NOQA


POST_DEF = "pip._vendor.requests.Session.post"


def patch_post(status_code, content):
    response = Response()
    response._content = content
    response.status_code = status_code
    return mock.patch(POST_DEF, return_value=response)


@pytest.mark.parametrize(
    "code",
    [500, 502],
)
def test_compile_response_server_fail(code):
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=code, content=b"bytes") as post:
        with pytest.raises(HTTPError) as exc_info:
            wheelsproxy_client.compile("")

        assert isinstance(exc_info.value.args[0], text_type)
        assert post.call_count == 1


@pytest.mark.parametrize(
    "code",
    [400, 404],
)
def test_compile_response_client_fail(code):
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=code, content=b"bytes") as post:
        with pytest.raises(client.CompilationError) as exc_info:
            wheelsproxy_client.compile("")

        assert isinstance(exc_info.value.args[0], text_type)
        assert post.call_count == 1


def test_compile_response_success():
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=200, content=b"bytes") as post:
        response = wheelsproxy_client.compile("")
        assert isinstance(response, text_type)
        assert post.call_count == 1


@pytest.mark.parametrize(
    "code",
    [400, 404],
)
def test_resolve_response_client_fail(code):
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=code, content=b"bytes") as post:
        with pytest.raises(client.ResolutionError) as exc_info:
            wheelsproxy_client.resolve("")

        assert isinstance(exc_info.value.args[0], text_type)
        assert post.call_count == 1


@pytest.mark.parametrize(
    "code",
    [500, 502],
)
def test_resolve_response_server_fail(code):
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=code, content=b"bytes") as post:
        with pytest.raises(HTTPError) as exc_info:
            wheelsproxy_client.resolve("")

        assert isinstance(exc_info.value.args[0], text_type)
        assert post.call_count == 1


def test_resolve_response_success():
    wheelsproxy_client = client.WheelsproxyClient("")

    with patch_post(status_code=200, content=b"bytes") as post:
        response = wheelsproxy_client.resolve("")
        assert isinstance(response, text_type)
        assert post.call_count == 1
