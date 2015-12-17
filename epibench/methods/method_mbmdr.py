import logging
import subprocess
import os

from epibench.report import infer

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

def fix_map_file(map_path):
    map_file = open( map_path, "r" )
    lines = map_file.readlines( )
    map_file.close( )

    lines.insert( 0, "chr\tsnp\tPOS\tBP\n" )
    map_file = open( map_path, "w" )
    for line in lines:
        map_file.write( line )
    map_file.close( )

def num_significant(output_path, threshold):
    value_list = list( )
    with open( output_path ) as output_file:
        next( output_file )
        next( output_file )
        next( output_file ) # skip header

        for line in output_file:
            column = line.strip( ).split( )
            try:
                snp1 = column[ 0 ]
                snp2 = column[ 1 ]

                pvalue = float( column[ 3 ] )

                if pvalue <= threshold:
                    value_list.append( ( snp1, snp2, pvalue ) )
            except ValueError:
                continue

    return value_list, 0

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
    pedmap_path = os.path.join( output_dir, "pedmap" )
    cmd = [ "plink2",
            "--bfile", input_files.plink_prefix,
            "--recode",
            "--out", pedmap_path ]
    if input_files.pheno_path:
        convert_to_plink( input_files.pheno_path, pedmap_path + ".pheno" )
        cmd.extend( [ "--pheno", pedmap_path + ".pheno" ] )
    
    logging.info( " ".join( cmd ) )
    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )
    fix_map_file( pedmap_path + ".map" )

    mbmdr_path = os.path.join( output_dir, "mbmdr" )
    mbmdr_tr_path = os.path.join( output_dir, "mbmdrtr" )
    cmd = [ "mbmdr",
            "--plink2mbmdr",
            "--binary",
            "-ped", pedmap_path + ".ped",
            "-map", pedmap_path + ".map",
            "-o", mbmdr_path,
            "-tr", mbmdr_tr_path ]
    logging.info( " ".join( cmd ) )
    subprocess.check_call( cmd, stdout = open( os.devnull, "w" ) )
    print( " ".join( cmd ) )

    alpha = method_params.get( "alpha", 0.05 )
    num_top = method_params.get( "num_top", 10 )
    num_perm = int( num_top / alpha ) + 10

    output_path = os.path.join( output_dir, "mbmdr.out" )
    cmd = [ "mbmdr", "--binary",
            "-n", str( num_top ),
            "-p", str( num_perm ),
            "-o", output_path,
            "-pb", "NONE",
            mbmdr_path ]
 
    logging.info( " ".join( cmd ) )
    subprocess.check_call( cmd )

    return num_significant( output_path, alpha )
