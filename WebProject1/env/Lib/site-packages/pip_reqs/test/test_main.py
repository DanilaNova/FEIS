from __future__ import unicode_literals

import pytest
from pip_reqs.__main__ import compile, main, resolve
from pip_reqs.client import CompilationError, ResolutionError


def test_main_no_args():
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 2


class DummyClient:
    def compile(self, text):
        assert text == "django==2.0"
        return "dummy==1.1"

    def resolve(self, text):
        assert text == "django==2.0"
        return "https://dummy.com/package.tar.gz"


class BogusClient:
    def compile(self, text):
        raise CompilationError("A compile error occurred")

    def resolve(self, text):
        raise ResolutionError("A resolve error occurred")


class DummyArgs:
    def __init__(self, reqs_in, reqs_out):
        self.reqs_in = reqs_in
        self.reqs_out = reqs_out
        self.infile = str(reqs_in)
        self.outfile = str(reqs_out)

    def write(self, text):
        self.reqs_in.write_text(text)

    def read(self):
        return self.reqs_out.read_text()


@pytest.fixture
def dummy_client():
    return DummyClient()


@pytest.fixture
def bogus_client():
    return BogusClient()


@pytest.fixture
def dummy_args(tmp_path):
    return DummyArgs(tmp_path / "infile", tmp_path / "outfile")


def test_compile(tmp_path, dummy_client, dummy_args):
    dummy_args.write("django==2.0")
    compile(dummy_client, dummy_args)
    assert dummy_args.read() == "dummy==1.1\n"


def test_compile_failure(tmp_path, bogus_client, dummy_args, capsys):
    dummy_args.write("django==2.0")
    with pytest.raises(SystemExit) as excinfo:
        compile(bogus_client, dummy_args)
    assert excinfo.value.code == 1
    assert capsys.readouterr().err == "A compile error occurred\n"


def test_resolve(tmp_path, dummy_client, dummy_args):
    dummy_args.write("django==2.0")
    resolve(dummy_client, dummy_args)
    assert dummy_args.read() == "https://dummy.com/package.tar.gz"


def test_resolve_failure(tmp_path, bogus_client, dummy_args, capsys):
    dummy_args.write("django==2.0")
    with pytest.raises(SystemExit) as excinfo:
        resolve(bogus_client, dummy_args)
    assert excinfo.value.code == 1
    assert capsys.readouterr().err == "A resolve error occurred\n"
