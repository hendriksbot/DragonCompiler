"""This module implements the command line interface of the dragon compiler"""
import typer

class CompilerCLI:
    """this is the command line interface class for the compiler"""
    def __init__(self):
        self.app = typer.Typer()
        self.app.command()(self.build)

    def run(self):
        self.app()

    def build(
        self,
        source: str = typer.Option(...,"--source", "-s"),
        out: str = typer.Option("./build","--out", "-o")
    ):
        print("ready to build")
        print("source: " + source)
        print("out: " + out)


# Entry Point
def main():
    cli = CompilerCLI()
    cli.run()

if __name__ == "__main__":
    main()
