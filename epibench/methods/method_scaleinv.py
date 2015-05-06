import logging
import subprocess
import os

from epibench.report import infer

##
# Given a plink file this function should apply
# the algorithm a return a list of the significant
# pairs.
#
# @param method_params This contains parameters for the method passed by the
#                      method json file, and is supplied as a dict directly.
#
# @param experiment_params Contains some parameters relevant for the specific experiment.
#
# @param plink_file A plink file object to apply the algorithm to. This object
#                   contains a path to the plink, phenotype and covariate file.
#
# @param output_dir A directory where the method can create temporary files used
#                   during the analysis.
#
def find_significant(method_params, experiment_params, input_files, output_dir):
    num_tests = method_params.get( "num-tests", 0 )
    alpha = method_params.get( "alpha", 0.05 )
        
    cmd =[ "bayesic",
           "scaleinv",
           "--model", "binomial",
           input_files.pair_path,
           input_files.plink_prefix
           ]

    logging.info( " ".join( cmd ) )
    output_path = os.path.join( output_dir, "bayesic.out" )
    output_file = open( output_path, "w" )
    subprocess.call( cmd, stdout = output_file )
     
    return infer.num_significant_multiple( output_path, [2,3,4,5,6], alpha / num_tests, 3 )
