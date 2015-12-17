from itertools import product
import subprocess
import os
import logging

from epibench.util.grouper import grouper
from epibench.util.heritability import heritability, prevalence
from epibench.experiment.inputfiles import InputFiles

class GenoExperiment:
    def __init__(self, maf, sample_size, model, params, dispersion, num_pairs, link = None, desired_h2 = 0.0, ld = None, name = "NA"):
        self.maf = maf
        self.sample_size = sample_size
        self.model = model
        self.params = params
        self.dispersion = dispersion
        self.num_pairs = num_pairs
        self.link = link
        self.ld = ld
        self.desired_h2 = desired_h2
        self.name = name

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

        if self.ld:
            cmd.append( "--ld" )
            cmd.append( str( self.ld ) )

        logging.info( " ".join( cmd ) )
        subprocess.call( cmd )

        return InputFiles( plink_prefix, plink_prefix + ".pair", info_path = plink_prefix + ".info" )

    def write_results(self, info, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t\"{1}\"\t{2}\t{3}\n".format( self.params_str( info ), name, significant[ 1 ], len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "name\theritability\tdesired_h2\tmaf1\tmaf2\tsample_size1\tsample_size2\tld\tparams\tnpairs\tmethod\tnum_missing\tnum_significant\n"

    def params_str(self, info):
        ld = 0.0
        if self.ld:
            ld = self.ld

        return "\"{0}\"\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}".format(
                self.name,
                info[ "heritability" ],
                self.desired_h2,
                self.maf[ 0 ],
                self.maf[ 1 ],
                self.sample_size[ 0 ],
                self.sample_size[ 1 ],
                ld,
                ",".join( map( str, self.params ) ),
                self.num_pairs )

def param_iter(experiment):
    name = experiment.get( "name", "NA" )
    model = experiment.get( "model", "binomial" )

    dispersion = experiment.get( "dispersion", [ 1.0 ] )
    maf = grouper( 2, experiment.get( "maf" ) )
    num_pairs = experiment.get( "num-pairs", 100 )
    ld = experiment.get( "ld", [ None ] )

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
        link = [ experiment.get( "link", "default" ) ]
        params = grouper( 9, experiment.get( "beta" ) )
    else:
        params = grouper( 9, experiment.get( "param" ) )
    
    for m, s, p, d, l, lewd in product( maf, sample_size, params, dispersion, link, ld ):
        yield GenoExperiment( m, s, model, p, d, num_pairs, l, ld = lewd, name = name )

