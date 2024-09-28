# SPDX-License-Identifier: 2023-present Artem Lykhvar <me@a10r.com>
#
# SPDX-License-Identifier: MIT
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

from click import Context, Group, pass_context, secho, version_option

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        secho(
            "You need to install 'tomllib' or 'tomli' to run this application",
            err=True,
            fg="red",
        )
        sys.exit(1)


context_settings: Dict[str, Any] = {
    "help_option_names": ["--help"],
    "ignore_unknown_options": True,
}


class App(Group):
    def __init__(self, config: Union[Path, None] = None) -> None:
        help_text = """
        \b
                       _ _
         _ __ _ __  __| (_)
        | '_ \\ '_ \\/ _| | |
        | .__/ .__/\\__|_|_|
        |_|  |_|
        """
        super().__init__(
            help=help_text,
            context_settings=context_settings,
        )
        self.config = config or Path(os.getcwd(), "pyproject.toml")
        self.commands = self._commands()
        self.invoke_without_command = True
        self.no_args_is_help = (True,)
        self.chain = True

    @staticmethod
    def _execute(
        cmd: Generator[str, None, None], ctx: Context  # noqa: ARG004
    ) -> None:
        for entry in cmd:
            secho(f"\n => {entry}")
            args = shlex.split(entry)

            if not args:
                raise ValueError("Empty command not allowed.")

            subprocess.call(entry, shell=True)  # noqa: S602

    @classmethod
    def _unfold(
        cls,
        cmd: Union[str, List[str]],
        entries: Dict[str, Union[str, List[str]]],
    ) -> Generator[str, None, None]:
        for sub in cmd:
            if sub in entries:
                sub_cmd = entries.get(sub)

                if isinstance(sub_cmd, list):
                    yield from cls._unfold(sub_cmd, entries)
                else:
                    yield cls._substitute_env_vars(sub_cmd)
            else:
                yield cls._substitute_env_vars(sub)

    @staticmethod
    def _abort(message: str) -> None:
        secho(message, err=True, fg="red")
        sys.exit(0)

    def _read_config(
        self, entry: str = "ppcli"
    ) -> Dict[str, Union[str, List[str]]]:
        if not self.config.exists():
            self._abort("No pyproject.toml file found")
        try:
            with open(self.config, encoding="utf-8") as f:
                config = tomllib.loads(f.read())
                return config["tool"].get(entry, {})
        except KeyError:
            self._abort("No configuration found at pyproject.toml")
        except OSError as err:
            self._abort(f"Error loading configuration: {err}")

    @staticmethod
    def _substitute_env_vars(command: str) -> str:
        def replace_var(match):
            var_name = match.group(1)
            if var_name in os.environ:
                return os.environ[var_name]
            else:
                message = f"Missing environment variable: {var_name}"
                secho(message, err=True, fg="red")
                raise ValueError(message)

        try:
            return re.sub(r"\$(\w+)", replace_var, command)
        except ValueError:
            sys.exit(1)

    def _commands(self) -> Dict[str, Any]:
        commands: Dict[str, Any] = {}
        entries: Dict[str, Union[str, List[str]]] = self._read_config()

        for name, entry in entries.items():
            cmd = [entry] if isinstance(entry, str) else entry
            if name in cmd:
                self._abort("Command error. Command can't rely on itself.")

            help_text = " && ".join(cmd) if isinstance(cmd, list) else str(cmd)

            def make_command(unfolded):
                @pass_context
                def command(ctx):
                    self._execute(unfolded, ctx)

                return command

            commands[name] = self.command(
                name=name,
                short_help=help_text,
                help=help_text,
                context_settings=context_settings,
            )(make_command(self._unfold(cmd, entries)))

        return commands


cli = version_option()(App())
