from itertools import product
import logging
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.experiment.inputfiles import InputFiles

class GLMFwerExperiment:
    def __init__(self, model, params, dispersion, effect_level, replicate, link = None):
        self.model = model
        self.params = params
        self.dispersion = dispersion
        self.effect_level = effect_level
        self.replicate = replicate
        self.link = link
 
    def generate_data(self, output_dir, input_plink = None):
        pheno_path = os.path.join( output_dir, "fwer.pheno" )

        cmd_type = "pheno-general"
        if self.link:
            cmd_type = "pheno-glm"

        cmd = [ "epigen", cmd_type,
                "--model", self.model,
                "--dispersion", str( self.dispersion ),
                "--out", pheno_path,
                input_plink ]
        
        if self.link:
            cmd.append( "--beta" )
            cmd.extend( list( map( str, self.params ) ) )
            cmd.append( "--link" )
            cmd.append( self.link )
        else:
            cmd.append( "--mu" )
            cmd.extend( list( map( str, self.params ) ) )

        logging.info( " ".join( cmd ) )

        subprocess.call( cmd )

        return InputFiles( input_plink, input_plink + ".pair", pheno_path = pheno_path )

    def write_results(self, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t{1}\t\"{2}\"\t{3}\n".format( self.replicate, self.effect_level, name, len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "replicate\teffect_level\tmethod_name\tnum_significant\n"

def param_iter(experiment):
    model = experiment.get( "model", "binomial" )
    
    params = grouper( 9, experiment.get( "param" ) )
    dispersion = experiment.get( "dispersion", [ 1.0 ] )
    effect_params = range( len( experiment.get( "param" ) ) / 9 )

    num_replicates = experiment.get( "replicates", 100 )
 
    # Experiment could either be mean value or beta
    link = [ None ]
    params = None
    if "beta" in experiment:
        link = experiment.get( "link", "default" )
        beta = grouper( 9, experiment.get( "beta" ) )
    else:
        params = grouper( 9, experiment.get( "param" ) )
    
    for e, p, d, l in product( effect_params, params, dispersion, link ):
        for replicate in range( num_replicates ):
            yield GLMFwerExperiment( model, p, d, e, replicate, l )
