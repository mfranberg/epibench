from epibench.util.dirhandle import setup_file, setup_dir
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

##
#  
#
def run_experiments(experiment_json, method_list, output_dir):
    data_prefix = setup_file( output_dir, "data", "plink" )
    started_experiments = set( )
    result_file = None

    for experiment_id, experiment in walk_experiments( experiment_json ):
        if not experiment_id in started_experiments:
            result_path = setup_file( output_dir, "result", "experiment{0}.out".format( experiment_id ) )
            result_file = open( result_path, "w" )
            result_file.write( experiment.header( ) )

        input_files = experiment.generate_data( data_prefix )
        method_results = run_methods( method_list, input_files, output_dir )
        experiment.write_results( method_results, result_file )
