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
    num_tests = method_params.get( "num-tests", [ 0, 0, 0, 0 ] )
    alpha = method_params.get( "alpha", 0.05 )
    weight = method_params.get( "weight", [ 0.25, 0.25, 0.25, 0.25 ] )
    model = method_params.get( "model", "binomial" )
    
    step1_path = os.path.join( output_dir, "besiq.out" )
    step1_file = open( step1_path, "w" )
    
    cmd = [ "besiq",
            "stagewise",
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )

    logging.info( " ".join( cmd ) )
    subprocess.call( cmd, stdout = step1_file )
    step1_file.close( )
 
    method = "adaptive"
    if any( map( lambda x: x != 0, num_tests ) ):
        method = "static"

    output_path = os.path.join( output_dir, "besiq.out.final" )
    cmd =[ "besiq-correct",
           "--method", method,
           "--model", model,
           "--alpha", str( alpha ),
           "--bfile", input_files.plink_prefix,
           "--output-prefix", output_path,
           step1_path
           ]

    cmd.append( "--weight" )
    cmd.append( ",".join( map( str, weight ) ) )

    cmd.append( "--num-tests" )
    cmd.append( ",".join( map( str, num_tests ) ) )

    logging.info( " ".join( cmd ) )
    output_file = open( output_path, "w" )
    subprocess.call( cmd, stdout = output_file )
    output_file.close( )
    
    if model == "binomial":
        missing_step1 = infer.num_missing_multiple( step1_path, [2,3,4] )
        significant, missing = infer.num_significant_multiple( output_path, [2,3,4,5,6], alpha, 3 )
        
        return ( significant, missing_step1 + missing )
    else:
        missing_step1 = infer.num_missing_multiple( step1_path, [2,3,4] )
        significant, missing = infer.num_significant_multiple( output_path, [2], alpha, 1 )
        
        return ( significant, missing_step1 + missing )

