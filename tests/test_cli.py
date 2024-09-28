import tempfile
from pathlib import Path

import pytest
from click.core import Command, Context

from ppcli.__about__ import __version__
from ppcli.app import App


@pytest.fixture
def test_entries():
    return {
        "a": ["a1", "a2"],
        "b": "b1",
        "c": ["c1", "c2", "a"],
        "all": ["a", "b", "c"],
    }


@pytest.fixture
def app():
    config = Path(__file__).parent / "pyproject.toml"
    return App(config=config)


def test_noentry(app):
    assert not app._read_config(entry="keyerror")


def test_exit(app):
    with pytest.raises(SystemExit):
        app._abort("test")


def test_nofile():
    with pytest.raises(SystemExit):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir, "pyproject.toml")
            App(config=path)._read_config()


def test_version_print_lines(run):
    output = run("--version")
    output_text = "".join(output.outlines)
    assert f"version {__version__}" in output_text


def test_command_parsing(app, test_entries):
    entries = app._read_config()
    assert entries == test_entries


def test_command_substitution(app):
    entries = app._read_config()
    commands = app._unfold(["all"], entries)
    assert list(commands) == ["a1", "a2", "b1", "c1", "c2", "a1", "a2"]


def test_command_wraps(app):
    commands = app.commands
    for key in app._read_config().keys():
        assert isinstance(commands[key], Command)
        assert commands[key].name == key


def test_execute(app):
    cmd = "ls"
    with Context(Command(cmd)) as ctx:
        app._execute([cmd], ctx)
