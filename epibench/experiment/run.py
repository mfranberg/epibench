import cPickle
import os
import logging
import json
from functools import partial

from epibench.util.dirhandle import setup_file, setup_dir
from epibench.util.grouper import grouper
from epibench.experiment.method import find_param_iter

def get_info(info_path):
    if not info_path:
        return dict( )

    try:
        return json.load( open( info_path, "r" ) )
    except IOError:
        return dict( )

def find_sub_experiments(experiment):
    param_iter = find_param_iter( experiment.get( "type" ) )
    return param_iter( experiment )

def walk_experiments(experiment_json):
    for i, experiment in enumerate( experiment_json[ "experiments" ] ):
        for sub_experiment in find_sub_experiments( experiment ):
            yield ( i, sub_experiment )

def run_methods(method_list, experiment_params, input_files, output_dir):
    method_id = 0
    for method, find_significant in method_list:
        method_output_dir = setup_dir( output_dir, "method", "method{0}".format( method_id ) )
        method_id += 1

        yield ( method[ "name" ], find_significant( method, experiment_params, input_files, method_output_dir ) )

def run_experiment_list(experiment_list, method_list, output_dir, plink_path = None):
    data_dir = setup_dir( output_dir, "data", "" )

    log_path = os.path.join( output_dir, "experiment.log" )
    logging.basicConfig( filename=log_path, format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG )

    started_experiments = set( )
    result_file = None

    for experiment_id, experiment in experiment_list:
        if not experiment_id in started_experiments:
            result_path = setup_file( output_dir, "result", "experiment{0}.out".format( experiment_id ) )
            result_file = open( result_path, "w" )
            result_file.write( experiment.header( ) )
            started_experiments.add( experiment_id )

        input_files = experiment.generate_data( data_dir, plink_path )
        info = get_info( input_files.info_path )
        method_results = run_methods( method_list, info, input_files, output_dir )
        experiment.write_results( info, method_results, result_file )

def run_experiments(experiment_json, method_list, output_dir, plink_path = None, cluster = None):
    json_path = setup_file( output_dir, "", "experiments.json" )
    with open( json_path, "w" ) as json_file:
        json.dump( experiment_json, json_file )

    experiment_list = list( walk_experiments( experiment_json ) )
    if not cluster:
        run_experiment_list( experiment_list, method_list, output_dir, plink_path )
    else:
        experiments_per_block = ( len( experiment_list ) + cluster.num_cores( ) - 1 ) / cluster.num_cores( )
        per_core_experiment = grouper( experiments_per_block, experiment_list )

        for core_id, core_experiment_list in enumerate( per_core_experiment ):
            core_output_dir = os.path.join( output_dir, "batch{0}".format( core_id ) )

            func = partial( run_experiment_list, core_experiment_list, method_list, core_output_dir, plink_path )
            func_path = setup_file( output_dir, "batch{0}".format( core_id ), "func.obj" )

            with open( func_path, "w" ) as func_file:
                cPickle.dump( func, func_file )

            cmd = [ "epibench", "resume", func_path ]
            cluster.submit( cmd )
