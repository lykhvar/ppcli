import pytest

pytest_plugins = ["pytester"]
EXEC = "ppcli"


@pytest.fixture
def sample(pytester):
    pytester.copy_example("pyproject.toml")


@pytest.fixture
def run(testdir, sample):  # noqa: ARG001
    def do_run(*args):
        return testdir.run(EXEC, *list(args))

    return do_run
