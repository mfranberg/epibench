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
    stage1_path = os.path.join( output_dir, "caseonly.res" )
    cmd = [ "besiq",
            "caseonly",
            "--method", "css",
            "-o", stage1_path,
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )
 
    logging.info( " ".join( cmd ) )
    
    subprocess.check_call( cmd )

    css_threshold = method_params.get( "css-threshold", 3.0 )
    css_threshold_cdf = method_params.get( "css-threshold-cdf", 0.3916252 )

    output_path = os.path.join( output_dir, "caseonly.out" )
    with open( output_path, "w" ) as output_file:
        cmd = [ "besiq",
                "view",
                "-p", "gt",
                "-f", "0",
                "-t", str( css_threshold ),
                stage1_path ]
        subprocess.check_call( cmd, stdout = output_file )
    
    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 1 )

    return infer.num_significant_bonferroni( output_path, 5, alpha, int( num_tests * css_threshold_cdf ) )
