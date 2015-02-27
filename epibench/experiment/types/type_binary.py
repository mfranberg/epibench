from itertools import product
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.util.heritability import heritability
from epibench.experiment.inputfiles import InputFiles

class BinaryExperiment:
    def __init__(self, maf, sample_size, params, num_pairs):
        self.maf = maf
        self.sample_size = sample_size
        self.params = params
        self.num_pairs = num_pairs

    def generate_data(self, output_dir, input_plink = None):
        plink_prefix = os.path.join( output_dir, "plink" )
        cmd = [ "epigen", "pair-single",
                "--maf", str( self.maf[ 0 ] ), str( self.maf[ 1 ] ),
                "--sample-size", str( self.sample_size[ 0 ] ), str( self.sample_size[ 1 ] ),
                "--npairs", str( self.num_pairs ),
                "--out", plink_prefix ]
        
        cmd.append( "--penetrance" )
        cmd.extend( list( map( str, self.params ) ) )

        subprocess.call( cmd )

        return InputFiles( plink_prefix, plink_prefix + ".pair" )

    def write_results(self, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t\"{1}\"\t{2}\t{3}\n".format( self.params_str( ), name, significant[ 1 ], len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "heritability\tmaf1\tmaf2\tncases\tncontrols\tnpairs\tmethod\tnum_missing\tnum_significant\n"

    def params_str(self):
        return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(
                heritability( self.params, self.maf ),
                self.maf[ 0 ],
                self.maf[ 1 ],
                self.sample_size[ 0 ],
                self.sample_size[ 1 ],
                self.num_pairs )

def param_iter(experiment):
    maf = grouper( 2, experiment.get( "maf" ) )
    sample_size = grouper( 2, experiment.get( "sample-size" ) )
    params = grouper( 9, experiment.get( "param" ) )
    num_pairs = experiment.get( "num-pairs", 100 )

    for m, s, p in product( maf, sample_size, params ):
        yield BinaryExperiment( m, s, p, num_pairs )
        

