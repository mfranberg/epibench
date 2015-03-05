from itertools import product
import subprocess
import os
import logging

from epibench.util.grouper import grouper
from epibench.util.heritability import heritability
from epibench.experiment.inputfiles import InputFiles

class GLMExperiment:
    def __init__(self, maf, sample_size, model, params, dispersion, num_pairs, link = None):
        self.maf = maf
        self.sample_size = sample_size
        self.model = model
        self.params = params
        self.dispersion = dispersion
        self.num_pairs = num_pairs
        self.link = link

    def generate_data(self, output_dir, input_plink = None):
        plink_prefix = os.path.join( output_dir, "plink" )

        cmd_type = "pair-general"
        if self.link:
            cmd_type = "pair-glm"

        cmd = [ "epigen", cmd_type,
                "--model", self.model,
                "--maf", str( self.maf[ 0 ] ), str( self.maf[ 1 ] ),
                "--sample-size", str( self.sample_size[ 0 ] ), str( self.sample_size[ 1 ] ),
                "--npairs", str( self.num_pairs ),
                "--dispersion", str( self.dispersion ),
                "--out", plink_prefix ]
        
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

        return InputFiles( plink_prefix, plink_prefix + ".pair" )

    def write_results(self, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t\"{1}\"\t{2}\t{3}\n".format( self.params_str( ), name, significant[ 1 ], len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "heritability\tmaf1\tmaf2\tncases\tncontrols\tnpairs\tmethod\tnum_missing\tnum_significant\n"

    def params_str(self):
        return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(
                heritability( self.model, self.params, self.maf, self.dispersion ),
                self.maf[ 0 ],
                self.maf[ 1 ],
                self.sample_size[ 0 ],
                self.sample_size[ 1 ],
                self.num_pairs )

def param_iter(experiment):
    model = experiment.get( "model", "binomial" )

    dispersion = experiment.get( "dispersion", [ 1.0 ] )
    maf = grouper( 2, experiment.get( "maf" ) )
    num_pairs = experiment.get( "num-pairs", 100 )

    # Binary experiments specify cases and controls
    sample_size = None
    if model == "binomial":
        sample_size = grouper( 2, experiment.get( "sample-size" ) )
    else:
        s = experiment.get( "sample-size" )
        sample_size = zip( s, [ 0 ] * len( s ) )

    # Experiment could either be mean value or beta
    link = [None]
    params = None
    if "beta" in experiment:
        link = experiment.get( "link", "default" )
        beta = grouper( 9, experiment.get( "beta" ) )
    else:
        params = grouper( 9, experiment.get( "param" ) )
    
    for m, s, p, d, l in product( maf, sample_size, params, dispersion, link ):
        yield GLMExperiment( m, s, model, p, d, num_pairs, l )

