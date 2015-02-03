import click
import json

from epibench.commands.command import CommandWithHelp
from epibench.experiment.run import run_experiments
from epibench.experiment.method import find_methods
from epibench.cluster.load import load_cluster

def json_file(path):
    with open( path, "r" ) as jf:
        return json.load( jf )

@click.command( "power", cls = CommandWithHelp, short_help = "Compute power for the given methods." )
@click.option( "--methods", type = str, help = "A comma-separated list of methods to run (default is to run all).", default = None )
@click.option( "--method-file", type = json_file, help = "A json-file describing which and how to run the methods.", default = None )
@click.option( "--experiment-file", type = json_file, help = "A json-file describing the experiments to run.", required = True )
@click.option( "--cluster", nargs=2, type = str, help = "A python file that contains a function submit that describes how to submit jobs to a cluster.", default = None  )
@click.option( "--out", type = click.Path( writable = True ), help = "The output directory.", required = True )
def epibench(methods, method_file, experiment_file, cluster, out):
    method_list = find_methods( method_file )
    if methods:
        method_list = find_methods( method_file, methods )

    run_experiments( experiment_file, method_list, out, cluster = load_cluster( cluster ) )
