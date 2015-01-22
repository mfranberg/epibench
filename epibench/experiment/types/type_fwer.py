from itertools import product
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.experiment.inputfiles import InputFiles

class BinaryFwerExperiment:
    def __init__(self, params, effect_level, replicate):
        self.params = params
        self.effect_level = effect_level
        self.replicate = replicate

    def generate_data(self, output_dir, input_plink):
        pheno_path = os.path.join( output_dir, "fwer.pheno" )
        cmd = [ "epigen", "pheno-binary",
                "--out", pheno_path,
                input_plink ]
        
        cmd.append( "--model" )
        cmd.extend( list( map( str, self.params ) ) )

        subprocess.call( cmd )

        return InputFiles( input_plink, input_plink + ".pair", pheno_path = pheno_path )

    def write_results(self, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t{1}\t\"{2}\"\t{3}\n".format( self.replicate, self.effect_level, name, len( significant ) ) )

        return method_results
        
    def header(self):
        return "replicate\teffect_level\tmethod_name\tnum_significant\n"

def param_iter(experiment):
    params = grouper( 9, experiment.get( "param" ) )
    effect_params = zip( params, range( len( experiment.get( "param" ) ) / 9 ) )

    num_replicates = experiment.get( "replicates", 100 )

    for ep, replicate in product( effect_params, range( num_replicates ) ):
        yield BinaryFwerExperiment( ep[ 0 ], ep[ 1 ], replicate )
        

