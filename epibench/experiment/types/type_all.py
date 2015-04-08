from itertools import product
import logging
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.experiment.inputfiles import InputFiles
from epibench.experiment.types.type_geno import GenoExperiment

def bio_to_mu(ap, dp, ip, maf):
    mu = [ -ap[ 0 ] - ap[ 1 ] + ip[ 0 ], dp[ 0 ] + ap[ 1 ] - ip[ 1 ], ap[ 0 ] - ap[ 1 ] - ip[ 0 ],
           -ap[ 0 ] + dp[ 1 ] - ip[ 2 ], dp[ 0 ] + dp[ 1 ] + ip[ 3 ], ap[ 0 ] + dp[ 1 ] + ip[ 2 ],
           -ap[ 0 ] + ap[ 1 ] - ip[ 0 ], dp[ 0 ] + ap[ 1 ] + ip[ 1 ], ap[ 0 ] + ap[ 1 ] + ip[ 0 ] ]

    p = [ (1 - maf[ 0 ])**2, 2*maf[ 0 ]*(1-maf[ 0 ]), maf[ 0 ]**2 ]
    q = [ (1 - maf[ 1 ])**2, 2*maf[ 1 ]*(1-maf[ 1 ]), maf[ 1 ]**2 ]

    maf = [ p[ 0 ] * q[ 0 ], p[ 1 ] * q[ 0 ], p[ 2 ] * q[ 0 ],
          p[ 0 ] * q[ 1 ], p[ 1 ] * q[ 1 ], p[ 2 ] * q[ 1 ],
          p[ 0 ] * q[ 2 ], p[ 1 ] * q[ 2 ], p[ 2 ] * q[ 2 ] ]

    b0 = -sum( m * pq for m, pq in zip( mu, maf ) )

    return list( map( lambda x: x - b0, mu ) )

def all_interactions(ip_list):
    for ip in ip_list:
        for pattern in product( [-1, 0, 1], repeat = 4 ):
            if all( p == 0 for p in pattern ):
                continue

            total = float( sum( abs( p ) for p in pattern ) )

            yield list( (p * ip) / total for p in pattern )

def param_iter(experiment):
    model = experiment.get( "model", "normal" )
    
    add_size = experiment.get( "aparam", [ 0.2, 0.2 ] )
    dom_size = experiment.get( "dparam", [ 0.2, 0.2 ] )
    interaction_size = all_interactions( experiment.get( "iparam", [ 0.6 ] ) )

    num_pairs = experiment.get( "num-pairs", 200 )
    sample_size = grouper( 2, experiment.get( "sample-size" ) )
    maf = grouper( 2, experiment.get( "maf" ) )
    
    for ip, s, m in product( interaction_size, sample_size, maf ):
        mu = bio_to_mu( add_size, dom_size, ip, m )
        yield GenoExperiment( m, s, model, mu, 1.0, num_pairs, None )
