from itertools import product
import logging
import subprocess
import os
import json

from epibench.util.heritability import prevalence
from epibench.util.grouper import grouper
from epibench.experiment.inputfiles import InputFiles

class CaseControlExperiment:
    def __init__(self, model, params, effect_level, replicate, sample_size, maf, nvariants, link = None, beta0 = None):
        self.model = model
        self.params = params
        self.effect_level = effect_level
        self.replicate = replicate
        self.sample_size = sample_size
        self.maf = maf
        self.num_true = nvariants[ 0 ]
        self.num_false = nvariants[ 1 ]
        self.link = link
        self.beta0 = beta0

    def generate_data(self, output_dir, input_plink = None):
        input_plink = os.path.join( output_dir, "plink" )
        pheno_path = input_plink + ".pheno"
        cmd = [ "epigen", "plink-casecontrol",
                "--maf", str( self.maf[ 0 ] ), str( self.maf[ 1 ] ),
                "--num-false", str( self.num_false ),
                "--num-true", str( self.num_true ),
                "--sample-size", str( self.sample_size[ 0 ] ), str( self.sample_size[ 1 ] ),
                "--out", input_plink ]

        if self.model == "glm":
            cmd.append( "--link" )
            cmd.append( self.link )
            cmd.append( "--beta" )
            cmd.extend( list( map( str, self.params ) ) )
        elif self.model == "additive":
            cmd.append( "--beta-sim" )
            cmd.extend( list( map( str, self.params ) ) )
            if self.beta0:
                cmd.append( "--beta0" )
                cmd.append( str( self.beta0 ) )
        elif self.model == "general":
            cmd.append( "--mu" )
            cmd.extend( list( map( str, self.params ) ) )

        logging.info( " ".join( cmd ) )

        subprocess.check_call( cmd )

        return InputFiles( input_plink, input_plink + ".pair", pheno_path = pheno_path, info_path = input_plink + ".info" )

    def write_results(self, info, method_results, result_file):
        for name, significant in method_results:
            result_file.write( "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t\"{9}\"\t{10}\n".format( self.replicate, self.effect_level, self.sample_size[ 0 ], self.sample_size[ 1 ], self.maf[ 0 ], self.maf[ 1 ], self.num_true, self.num_false, ",".join( map( str, self.params ) ), name, len( significant[ 0 ] ) ) )

        return method_results
        
    def header(self):
        return "replicate\teffect_level\tncases\tncontrols\tmaf1\tmaf2\tnum_true\tnum_false\tparams\tmethod_name\tnum_significant\n"

def param_iter(experiment):
    model = experiment.get( "model" )
    
    params = None
    effect_params = None
    if model == "glm" or model == "general":
        params = grouper( 9, experiment.get( "param" ) )
        effect_params = zip( range( len( experiment.get( "param" ) ) / 9 ), params )
    else:
        params = grouper( 2, experiment.get( "param" ) )
        effect_params = zip( range( len( experiment.get( "param" ) ) / 2 ), params )

    num_replicates = experiment.get( "replicates", 100 )

    sample_size = grouper( 2, experiment.get( "sample-size", [ 2000, 2000 ] ) )
    maf = grouper( 2, experiment.get( "maf", [ 0.4, 0.4 ] ) )
    nvariants = grouper( 2, experiment.get( "nvariants", [2, 100] ) )
 
    # Experiment could either be mean value or beta
    beta0 = experiment.get( "beta0", None )
    link = experiment.get( "link", "default" )
    
    for s, m, n, e in product( sample_size, maf, nvariants, effect_params ):
        for replicate in range( num_replicates ):
            yield CaseControlExperiment( model, e[ 1 ], e[ 0 ], replicate, s, m, n, link, beta0 )
