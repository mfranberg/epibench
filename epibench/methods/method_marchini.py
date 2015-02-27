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
    step1_path = os.path.join( output_dir, "step1.out" )
    cmd = [ "plink2",
            "--bfile", input_files.plink_prefix,
            "--silent",
            "--model", "--out", step1_path ]

    if input_files.pheno_path:
        cmd.extend( [ "--pheno", input_files.pheno_path ] )

    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )

    step1_alpha = method_params.get( "step1-alpha", 0.10 )
    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 0 )

    # Find the signifcant single snps
    significant = set( )
    with open( step1_path + ".model", "r" ) as assoc_file:
        next( assoc_file ) # Skip header

        for line in assoc_file:
            column = line.strip( ).split( )
            if column[ 4 ] != "GENO":
                continue

            try:
                pvalue = float( column[ 9 ] )
                if pvalue < step1_alpha:
                    significant.add( column[ 1 ] )
            except:
                continue

    # Write the pairs to run
    new_pairs = os.path.join( output_dir, "significant_pairs.out" )
    with open( new_pairs, "w" ) as new_pairs_file:
        for line in open( input_files.pair_path ):
            snp1, snp2 = line.strip( ).split( )
            if snp1 in significant or snp2 in significant:
                new_pairs_file.write( line )

    # Perform logistic regression on the remaining pairs
    cmd = [ "bayesic",
            "-m", "wald",
            new_pairs,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )

    logging.info( " ".join( cmd ) )

    output_path = os.path.join( output_dir, "marchini.out" )
    with open( output_path, "w" ) as output_file:
        subprocess.check_call( cmd, stdout = output_file )
 
    expected_num_tests = int( step1_alpha * num_tests + 1 ) * ( int( step1_alpha * num_tests + 1 ) - 1 ) / 2
    return infer.num_significant_bonferroni( output_path, 3, alpha, expected_num_tests )
