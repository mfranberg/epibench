import os
import sys
import click

from epibench.commands.command import ComplexCLI

@click.command(no_args_is_help = True, cmd_subdirs = ["method"], cls = ComplexCLI)
def epibench():
    """Evaluate statistical methods for epistasis."""

if __name__ == "__main__":
    epibench( )
