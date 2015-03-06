import glob
import json
import os
import subprocess
from collections import defaultdict
from pkg_resources import resource_filename

from epibench.util.dirhandle import mkdir_p

def group_result(batch_dirs):
    base_path_map = defaultdict( list )
    for experiment_path in batch_dirs:
        base_path_map[ os.path.basename( experiment_path ) ].append( experiment_path )

    return base_path_map.iteritems( )

def write_results(experiment_path, output_file, with_header = True):
    with open( experiment_path, "r" ) as experiment_file:
        if not with_header:
            next( experiment_file )
        
        for line in experiment_file:
            output_file.write( line )

def merge_results(grouped_results, output_dir):
    for experiment_base, experiment_paths in grouped_results:
        output_path = os.path.join( output_dir, experiment_base )
        with open( output_path, "w" ) as output_file:
            write_results( experiment_paths[ 0 ], output_file )

            for experiment_path in experiment_paths[ 1: ]:
                write_results( experiment_path, output_file, with_header = False )

def plot(result_path, plot_path):
    cmd = [ "Rscript",
            resource_filename( "epibench.external", "plot_power_joint.r" ),
            result_path,
            plot_path
    ]
    
    subprocess.check_call( cmd )

def tabulate(result_path, table_path):
    cmd = [ "Rscript",
            resource_filename( "epibench.external", "table_fwer.r" ),
            result_path,
            table_path
            ]

    subprocess.check_call( cmd )

def compile_results(experiments, result_dir, final_dir):
    for i, e in enumerate( experiments ):
        result_path = os.path.join( result_dir, "experiment{0}.out".format( i ) )

        if e[ "type" ] == "geno":
            plot_path = os.path.join( final_dir, "experiment{0}.pdf".format( i ) )
            plot( result_path, plot_path )
        elif e[ "type" ] == "pheno":
            table_path = os.path.join( final_dir, "experiment{0}.csv".format( i ) )
            tabulate( result_path, table_path )

def compile_experiments(input_dir):
    experiments = [ ]
    with open( os.path.join( input_dir, "experiments.json" ), "r" ) as experiment_file:
        experiments = json.load( experiment_file )

    result_dir = os.path.join( input_dir, "result" )
    batch_dirs = glob.glob( os.path.join( input_dir, "batch*", "result", "*.out" ) )
    if len( batch_dirs ) > 0:
        grouped_results = group_result( batch_dirs )
        mkdir_p( result_dir )
        merge_results( grouped_results, result_dir )

    final_dir = os.path.join( input_dir, "final" )
    mkdir_p( final_dir )

    compile_results( experiments[ "experiments" ], result_dir, final_dir )
