import logging
import subprocess
import os

from epibench.report import infer

def num_significant(output_path, alpha, num_tests):
    significant = set( )

    threshold1 = 1.0
    if num_tests != 0:
        threshold1 = alpha / ( 4.0 * num_tests )

    with open( output_path ) as output_file:
        next( output_file ) # Skip header

        for line in output_file:
            column = line.strip( ).split( )
            snp1_info = column[ 0 ].split( "," )
            snp2_info = column[ 1 ].split( "," )

            if len( snp1_info ) != 6  or len( snp2_info ) != 6:
                continue
            
            snp1 = snp1_info[ 3 ]
            snp2 = snp2_info[ 3 ]

            try:
                pvalue1 = float( column[ 4 ] )
                pvalue2 = float( column[ 7 ] )

                if pvalue1 <= threshold1 and pvalue2 <= threshold1:
                    significant.add( ( snp1, snp2 ) )
            except ValueError:
                continue

    return list( significant ), 0

def convert_to_plink(bayesic_pheno, output_pheno):
    output_file = open( output_pheno, "w" )
    with open( bayesic_pheno, "r" ) as pheno_file:
        for line in pheno_file:
            column = line.strip( ).split( )
            if line.startswith( "FID" ):
                output_file.write( "\t".join( column ) + "\n" )
            else:
                if column[ 2 ] != "NA":
                    column[ 2 ] = str( int( float( column[ 2 ] ) ) + 1 )
                else:
                    column[ 2 ] = "0"
                output_file.write( "\t".join( column ) + "\n" )

    output_file.close( )

def create_pair_file(pair_path, sixpac_pair_path):
    sixpac_pair = open( sixpac_pair_path, "w" )
    with open( pair_path, "r" ) as pair_file:
        for line in pair_file:
            snp1, snp2 = line.strip( ).split( )
            
            sixpac_pair.write( "{0}\t{1}\t{2}\t{3}\n".format( "d", snp1, "d", snp2 ) )
            sixpac_pair.write( "{0}\t{1}\t{2}\t{3}\n".format( "r", snp1, "d", snp2 ) )
            sixpac_pair.write( "{0}\t{1}\t{2}\t{3}\n".format( "d", snp1, "r", snp2 ) )
            sixpac_pair.write( "{0}\t{1}\t{2}\t{3}\n".format( "r", snp1, "r", snp2 ) )

    sixpac_pair.close( )

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
    # Prepare input format
    plink_prefix = os.path.join( output_dir, "sixpac" )
    cmd = [ "plink2",
            "--bfile", input_files.plink_prefix,
            "--recodeA",
            "--out", plink_prefix ]
    if input_files.pheno_path:
        convert_to_plink( input_files.pheno_path, plink_prefix + ".pheno" )
        cmd.extend( [ "--pheno", plink_prefix + ".pheno" ] )

    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )
    cmd = [ "plink2",
            "--bfile", input_files.plink_prefix,
            "--recode",
            "--out", plink_prefix ]
    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )


    # Run sixpac
    output_path = os.path.join( output_dir, "sixpac.out" )
    cmd = [ "sixpac",
            "--maxheap", "8",
            "--threads", "1",
            "--useblocks-bp", "0",
            "--raw", plink_prefix + ".raw",
            "--map", plink_prefix + ".map",
            "--out", output_path ]

    num_tests = method_params.get( "num-tests", 1 )
    if num_tests == 0:
        cmd.extend( [ "--mode", "approx" ] )
    else:
        pair_path = os.path.join( output_dir, "sicpac.pair" )
        create_pair_file( input_files.pair_path, pair_path )
        cmd.extend( [ "--mode", "test" ] )
        cmd.extend( [ "--testfile", pair_path ] )

    logging.info( " ".join( cmd ) )
    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )

    alpha = method_params.get( "alpha", 0.05 )

    return num_significant( output_path + ".sxp", alpha, num_tests )
