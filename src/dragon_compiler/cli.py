"""This module implements the command line interface of the dragon compiler"""
import typer
import logging
from pathlib import Path
from dragon_compiler import builder

class CompilerCLI:
    """this is the command line interface class for the compiler"""
    def __init__(self):
        self._app = typer.Typer(help="Awesome dragon compiler " \
            "for your spells and monster database")
        self._app.command("build")(self._make_build_command())
        self._app.command("release")(self._make_release_command())
        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s] %(message)s")

    def run(self):
        self._app()

    def _make_build_command(self):
        def build_command(
            source: str = typer.Option(
                ...,"--source", "-s",
                help ="source folder that contains the database that needs " \
                "to be compiled"),
            out: str = typer.Option(
                "./build","--out", "-o",
                help = "optional output folder where the database will be"
                " created"),
            do_clean: bool = typer.Option(
                False, "--clean", "-c", is_flag=True,
                help = "removes old build from output folder")
        ):
            return self.build(source, out, do_clean)
        return build_command

    def _make_release_command(self):
        def release_command(
                source: str = typer.Option(...,"--source", "-s")
        ):
            return self.release(source)
        return release_command

    def _create_builder(self) -> builder.Builder:
        return builder.Builder(logger = logging.getLogger("dragon"))

    def build(self, source: str, out: str, do_clean: bool): #pylint: disable=unused-argument
        db_builder= self._create_builder()
        db_builder.set_config(builder.BuilderConfig(
            Path(source), Path(out), "spells.sqlite"
        ))
        if do_clean:
            db_builder.clean_up_out_folder()

        db_builder.build()

    def release(self, source: str):
        out = "release"
        db_builder= self._create_builder()
        db_builder.set_config(builder.BuilderConfig(
            Path(source), Path(out), "spells.sqlite"
        ))
        db_builder.clean_up_out_folder()
        db_builder.build()
        db_builder.package_release()

# Entry Point
def main():
    cli = CompilerCLI()
    cli.run()

if __name__ == "__main__":
    main()
