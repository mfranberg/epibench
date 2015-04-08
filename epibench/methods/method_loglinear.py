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
# @param plink_file A plink file object to apply the algorithm to. This object
#                   contains a path to the plink, phenotype and covariate file.
#
# @param output_dir A directory where the method can create temporary files used
#                   during the analysis.
#
def find_significant(method_params, input_files, output_dir):
    cmd = [ "bayesic",
            "loglinear",
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )
 
    logging.info( " ".join( cmd ) )
    
    output_path = os.path.join( output_dir, "loglinear.out" )
    with open( output_path, "w" ) as output_file:
        subprocess.call( cmd, stdout = output_file )
    
    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 1 )

    return infer.num_significant_bonferroni( output_path, 2, alpha, num_tests )
