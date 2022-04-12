import pytest

from . import compat


@pytest.fixture(autouse=True, scope="session")
def setup_global_pip_state():
    with compat.setup_global_pip_state():
        yield
