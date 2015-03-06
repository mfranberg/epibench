import click

from epibench.commands.command import CommandWithHelp
from epibench.experiment.compile import compile_experiments

@click.command( "compile", cls = CommandWithHelp, short_help = "Create plots and tables for an experiment that has been run." )
@click.argument( "input_dir", type = click.Path( exists = True ), required = True )
def epibench(input_dir):
    compile_experiments( input_dir )
