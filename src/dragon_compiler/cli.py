"""This module implements the command line interface of the dragon compiler"""
import typer
from pathlib import Path
from dragon_compiler import builder

class CompilerCLI:
    """this is the command line interface class for the compiler"""
    def __init__(self):
        self._app = typer.Typer()
        self._app.command()(self._make_build_command())

    def run(self):
        self._app()

    def _make_build_command(self):
        def build_command(
            source: str = typer.Option(...,"--source", "-s"),
            out: str = typer.Option("./build","--out", "-o")
        ):
            return self.build(source, out)
        return build_command

    def build(self, source: str, out: str):
        print("ready to build")
        print("source: " + source)
        print("out: " + out)
        db_builder= builder.Builder()
        db_builder.set_config(builder.BuilderConfig(
            Path(source), Path(out), "spells.sqlite"
        ))
        db_builder.build()


# Entry Point
def main():
    cli = CompilerCLI()
    cli.run()

if __name__ == "__main__":
    main()
