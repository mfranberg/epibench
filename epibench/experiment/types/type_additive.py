from itertools import product
import logging
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.experiment.inputfiles import InputFiles

class AdditiveExperiment:
    def __init__(self, model, params, dispersion, effect_level, replicate, link = None, nassociated = None, beta0 = None, plink_config = None):
        self.model = model
        self.params = params
        self.dispersion = dispersion
        self.effect_level = effect_level
        self.replicate = replicate
        self.link = link
        self.nassociated = nassociated
        self.beta0 = beta0
        self.plink_config = plink_config

    def get_params(self):
        return dict( )

    def generate_plink(self, output_dir):
        input_plink = os.path.join( output_dir, "plink" )
        cmd = [ "epigen",
                "plink-data",
                "--nsamples", str( self.plink_config[ "nsamples" ] ),
                "--nvariants", str( self.plink_config[ "nvariants" ] ),
                "--create-pair",
                "--out", input_plink ]

        maf = self.plink_config.get( "maf" )
        if maf:
            cmd.extend( [ "--maf", str( maf[ 0 ] ), str( maf[ 1 ] ) ] ) 

        subprocess.check_call( cmd )

        return input_plink
 
    def generate_data(self, output_dir, input_plink = None):
        pheno_path = os.path.join( output_dir, "additive.pheno" )

        if not input_plink:
            input_plink = self.generate_plink( output_dir )

        cmd = [ "epigen", "pheno-additive",
                "--model", self.model,
                "--dispersion", str( self.dispersion ),
                "--num-loci", str( self.nassociated ),
                "--out", pheno_path,
                input_plink ]
        
        if self.link:
            cmd.append( "--link" )
            cmd.append( self.link )

        if self.beta0:
            cmd.append( "--beta0" )
            cmd.append( str( self.beta0 ) )
        
        cmd.append( "--beta" )
        cmd.extend( list( map( str, self.params ) ) )

        logging.info( " ".join( cmd ) )

        subprocess.check_call( cmd )

        return InputFiles( input_plink, input_plink + ".pair", pheno_path = pheno_path )

    def write_results(self, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t{1}\t\"{2}\"\t{3}\n".format( self.replicate, self.effect_level, name, len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "replicate\teffect_level\tmethod_name\tnum_significant\n"

def param_iter(experiment):
    model = experiment.get( "model", "binomial" )
    
    params = grouper( 2, experiment.get( "param" ) )
    dispersion = experiment.get( "dispersion", [ 1.0 ] )
    effect_params = zip( range( len( experiment.get( "param" ) ) / 2 ), params )

    num_replicates = experiment.get( "replicates", 100 )

    plink_config = dict( )
    plink_config[ "nvariants" ] = experiment.get( "nvariants", 100 )
    plink_config[ "nsamples" ] = experiment.get( "nsamples", 2000 )
    plink_config[ "maf" ] = experiment.get( "maf", None )
 
    # Experiment could either be mean value or beta
    beta0 = experiment.get( "beta0", None )
    link = experiment.get( "link", [ "default" ] )
    nassociated = experiment.get( "nassociated", [ 5 ] )
    
    for e, d, l, n in product( effect_params, dispersion, link, nassociated ):
        for replicate in range( num_replicates ):
            yield AdditiveExperiment( model, e[ 1 ], d, e[ 0 ], replicate, l, n, beta0, plink_config )
