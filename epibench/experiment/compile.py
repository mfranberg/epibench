import glob
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
    
    print " ".join( cmd )
    subprocess.check_call( cmd )

def plot_results(result_dir, plot_dir):
    result_files = glob.glob( os.path.join( result_dir, "*.out" ) )
    for r in result_files:
        basename = os.path.basename( r )
        prefix = os.path.splitext( basename )[ 0 ]
        plot_path = os.path.join( plot_dir, prefix + ".pdf" )
        plot( r, plot_path )

def compile_experiments(experiments, input_dir):
    result_dir = os.path.join( input_dir, "result" )
    batch_dirs = glob.glob( os.path.join( input_dir, "batch*/result/*.out" ) )
    if len( batch_dirs ) > 0:
        grouped_results = group_result( batch_dirs )
        mkdir_p( result_dir )
        merge_results( grouped_results, result_dir )

    plot_dir = os.path.join( input_dir, "plot" )
    mkdir_p( plot_dir ) 
    plot_results( result_dir, plot_dir )

