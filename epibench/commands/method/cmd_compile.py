import click
import json

from epibench.commands.command import CommandWithHelp
from epibench.experiment.compile import compile_experiments

def json_file(path):
    with open( path, "r" ) as jf:
        return json.load( jf )

@click.command( "compile", cls = CommandWithHelp, short_help = "Estimate FWER for the given methods." )
@click.option( "--experiment-file", type = json_file, help = "A json-file describing the experiments to run.", required = True )
@click.option( "--input-dir", type = click.Path( exists = True ), help = "The output directory of the run.", required = True )
def epibench(experiment_file, input_dir):
    compile_experiments( experiment_file, input_dir )
