import cPickle
import os
from functools import partial

from epibench.util.dirhandle import setup_file, setup_dir
from epibench.util.grouper import grouper
from epibench.experiment.method import find_param_iter

def find_sub_experiments(experiment):
    param_iter = find_param_iter( experiment.get( "type" ) )
    return param_iter( experiment )

def walk_experiments(experiment_json):
    for i, experiment in enumerate( experiment_json[ "models" ] ):
        for sub_experiment in find_sub_experiments( experiment ):
            yield ( i, sub_experiment )

def run_methods(method_list, input_files, output_dir):
    method_id = 0
    for method, find_significant in method_list:
        method_output_dir = setup_dir( output_dir, "method", "method{0}".format( method_id ) )
        method_id += 1

        yield ( method[ "name" ], find_significant( method, input_files, method_output_dir ) )

def run_experiment_list(experiment_list, method_list, output_dir, plink_path = None):
    data_dir = setup_dir( output_dir, "data", "" )

    started_experiments = set( )
    result_file = None

    for experiment_id, experiment in experiment_list:
        if not experiment_id in started_experiments:
            result_path = setup_file( output_dir, "result", "experiment{0}.out".format( experiment_id ) )
            result_file = open( result_path, "w" )
            result_file.write( experiment.header( ) )
            started_experiments.add( experiment_id )

        input_files = experiment.generate_data( data_dir, plink_path )
        method_results = run_methods( method_list, input_files, output_dir )
        experiment.write_results( method_results, result_file )

def run_experiments(experiment_json, method_list, output_dir, plink_path = None, cluster = None):
    experiment_list = list( walk_experiments( experiment_json ) )
    if not cluster:
        run_experiment_list( experiment_list, method_list, output_dir, plink_path )
    else:
        per_core_experiment = grouper( cluster.num_cores( ), experiment_list )

        for core_id, core_experiment_list in enumerate( per_core_experiment ):
            core_output_dir = os.path.join( output_dir, "batch{0}".format( core_id ) )

            func = partial( run_experiment_list, core_experiment_list, method_list, core_output_dir, plink_path )
            func_path = setup_file( output_dir, "batch{0}".format( core_id ), "func.obj" )

            with open( func_path, "w" ) as func_file:
                cPickle.dump( func, func_file )

            cmd = [ "epibench", "method-run", func_path ]
            cluster.submit( cmd )
