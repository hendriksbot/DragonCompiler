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
        source: str,
        out: str = "./build",
    ):
        pass


# Entry Point
def main():
    cli = CompilerCLI()
    cli.run()

if __name__ == "__main__":
    main()
