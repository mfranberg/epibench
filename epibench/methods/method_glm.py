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
    scale = method_params.get( "scale", "logistic" )
    factor = method_params.get( "factor", "factor" )

    cmd = [ "besiq",
            "glm",
            "-l", scale,
            "-f", factor,
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.cov_path:
        cmd.extend( [ "-c", input_files.cov_path ] )

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )
    
    logging.info( " ".join( cmd ) )
    
    output_path = os.path.join( output_dir, "besiq.out" )
    with open( output_path, "w" ) as output_file:
        subprocess.call( cmd, stdout = output_file )
    
    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 1 )

    return infer.num_significant_bonferroni( output_path, 3, alpha, num_tests )
