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
    num_tests = method_params.get( "num-tests", [ 0, 0, 0, 0 ] )
    alpha = method_params.get( "alpha", 0.05 )
    weight = method_params.get( "weight", [ 0.25, 0.25, 0.25, 0.25 ] )
    
    step1_path = os.path.join( output_dir, "bayesiclm.out" )
    step1_file = open( step1_path, "w" )
    
    cmd = [ "bayesic",
            "stagewise",
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )

    logging.info( " ".join( cmd ) )
    subprocess.call( cmd, stdout = step1_file )
    step1_file.close( )
 
    cmd =[ "bayesic-correct",
           "--use-lm",
           "--alpha", str( alpha ),
           step1_path,
           input_files.plink_prefix
           ]

    cmd.append( "--weight" )
    cmd.append( ",".join( str, weight ) )

    cmd.append( "--num-tests" )
    cmd.append( ",".join( str, num_tests ) )

    logging.info( " ".join( cmd ) )
    output_path = os.path.join( output_dir, "bayesiclm.out.final" )
    output_file = open( output_path, "w" )
    subprocess.call( cmd, stdout = output_file )

    missing_step1 = infer.num_missing_multiple( step1_path, [2,3,4] )
    significant, missing = infer.num_significant_multiple( output_path, [2], alpha, 1 )

    return ( significant, missing + missing_step1 )
