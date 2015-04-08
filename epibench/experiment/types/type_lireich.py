from itertools import product
from functools import partial
import logging
import subprocess
import os

from epibench.util.grouper import grouper
from epibench.util.heritability import heritability
from epibench.experiment.inputfiles import InputFiles
from epibench.experiment.types.type_geno import GenoExperiment

##
# Converts a marginal null vector to a
# complete penetrance matrix for two loci.
#
# e.g.
#
# (p1, p2, p3) -> ( p1, p2, p3, p1, p2, p3, p1, p2, p3 )
#
# or
#
# (p1, p2, p3) -> ( p1, p1, p1, p2, p2, p2, p3, p3, p3 )
#
# @param a The marginal vector. 
# @param other If false each row has the same penetrance,
#              otherwise each column.
#
# @return The penetrance matrix as a vector.
#
def to_mat(a, other = False):
    l = list( )
    for i in range(3):
        for j in range(3):
            index = i
            if other:
                index = j

            l.append( a[ index ] )

    return tuple( l )

##
# The OR null model, if either locus is one the disease
# develops.
#
def mat_or(a, b):
    return tuple( map( lambda x: x[ 0 ] | x[ 1 ], zip(a, b) ) )

##
# Generate all possible interaction and null models by
# generating all possible marginal vectors and combining
# them with the given null function, to see which null 
# models can be reached. The interactions are then defined
# as all models minus these null models.
#
def generate():
    all_mats = set( a for a in product( (0,1), repeat = 9 ) )
    null_mats = set( )
    for a in product( (0,1), repeat = 3 ):
        for b in product( (0,1), repeat = 3 ):
            a_mat = to_mat( a, True )
            b_mat = to_mat( b, True )
            null_mats.add( mat_or( a_mat, b_mat ) )

            a_mat = to_mat( a, True )
            b_mat = to_mat( b, False )
            null_mats.add( mat_or( a_mat, b_mat ) )
            
            a_mat = to_mat( a, False )
            b_mat = to_mat( b, True )
            null_mats.add( mat_or( a_mat, b_mat ) )

            a_mat = to_mat( a, False )
            b_mat = to_mat( b, False )
            null_mats.add( mat_or( a_mat, b_mat ) )

    int_mats = all_mats.difference( null_mats )

    return ( int_mats, null_mats )

##
# Given a desired heritability, a fully penetrant disease model
# (penetrance is either 1 or 0), this function tries to find a
# non-fully penetrant disease model that has the desired
# heritability.
#
# @param desired_heritability The desired heritability
# @param base_risk The population risk.
# @param maf Minor allele frequency.
# @param model The fully penetrance disease model.
# 
# @return A non-fully penetrant disease model with as close
#         heritability to the desired as possible.
#
def find_penetrance(desired_heritability, base_risk, maf, model):
    if sum( model ) == 0 or sum( model ) == 9:
        return [ 0.5 ] * 9

    step = 0.01
    disease_p = base_risk + step
    disease_map = dict( { 0 : base_risk, 1 : 1.0 } )
    penetrance = list( map( lambda x: disease_map[ x ], model ) )
    if heritability( "binomial", penetrance, maf, 1.0 ) < desired_heritability:
        print( "Warning: impossible to find penetrance with desired heritability under (will use maximum): " + str( model ) )

    while disease_p <= 1.0:
        disease_map = dict( { 0 : base_risk, 1 : disease_p } )
        penetrance = list( map( lambda x: disease_map[ x ], model ) )
        if heritability( "binomial", penetrance, maf, 1.0 ) >= desired_heritability:
            return penetrance

        disease_p += step

    return penetrance

def all_interactions(h2, base_risk, maf):
    interactions, nulls = generate( )
    partial_find_penetrance = partial( find_penetrance, h2, base_risk, maf )
    return map( partial_find_penetrance, interactions )

def param_iter(experiment):
    heritabilities = experiment.get( "heritability", [ 0.2 ] )
    base_risks = experiment.get( "base-risk", [ 0.5 ] )
    num_pairs = experiment.get( "num-pairs", 200 )
    sample_size = grouper( 2, experiment.get( "sample-size" ) )
    maf = grouper( 2, experiment.get( "maf" ) )
    
    for h, b, s, m in product( heritabilities, base_risks, sample_size, maf ):
        for mu in all_interactions( h, b, m ):
            yield GenoExperiment( m, s, "binomial", mu, 1.0, num_pairs, None )
