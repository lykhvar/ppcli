# ppcli

[![PyPI - Version](https://img.shields.io/pypi/v/ppcli.svg)](https://pypi.org/project/ppcli)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ppcli.svg)](https://pypi.org/project/ppcli)

-----
`ppcli` stands for **pyproject CLI**. It is a Python package designed to provide an easy way to specify and manage auxiliary commands within a `pyproject.toml` file for any Python project.

## Purpose

The primary purpose of `ppcli` is to allow developers to define and manage common project tasks, such as test, lint, and migration commands, directly within the `pyproject.toml` file. This ensures that all project-specific commands are centralized and easily accessible.

## Installation

You can install `ppcli` via pip:

```console
pip install ppcli
```

## Usage
After installing ppcli, you can define your project-specific commands within your pyproject.toml file under the `[tool.ppcli]` section.

### Example pyproject.toml Configuration
```toml
[tool.ppcli]
lint="black --check --diff ."
fmt="black ."
clean = [
    "find . -type d -name __pycache__ -empty -print0 | xargs --null --no-run-if-empty rmdir",
    "coverage erase",
]
test = [
    "clean",
    "pytest --cov --blockage -x -s --no-header -ra",
]
```
### Defining and Combining Commands
* **Single Command**: Each key under [tool.ppcli] represents a command that can be executed. The value can be a single command string or a list of commands.
* **Combined Commands**: Use the keys of other commands to create combined tasks. In the example above, the test command executes the clean command followed by pytest.

### Running Commands

To execute the defined commands, simply run the ppcli tool followed by the command name:

```console
ppcli <command>
```
For example:

```console
ppcli lint
ppcli fmt
ppcli test
```

## Contributing

Contributions are welcome! Please open an issue or a pull request to contribute.

## License
This project is licensed under the [MIT](https://spdx.org/licenses/MIT.html) License. See the [LICENSE](/LICENSE) file for more details.

