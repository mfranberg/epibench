import logging
import subprocess
import os
import math
from math import sqrt


from epibench.report import infer

def qnorm(p, mean = 0.0, sd = 1.0):
    """
    Modified from the author's original perl code (original comments follow below)
    by dfield@yahoo-inc.com.  May 3, 2004.
 
    Lower tail quantile for standard normal distribution function.
 
    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.
 
    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.
 
    Author:      Peter John Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """
 
    if p <= 0 or p >= 1:
        # The original perl code exits here, we'll throw an exception instead
        raise ValueError( "Argument to ltqnorm %f must be in open interval (0,1)" % p )
 
    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01,  2.209460984245205e+02, \
         -2.759285104469687e+02,  1.383577518672690e+02, \
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02, \
         -1.556989798598866e+02,  6.680131188771972e+01, \
         -1.328068155288572e+01 )
    c = (-7.784894002430293e-03, -3.223964580411365e-01, \
         -2.400758277161838e+00, -2.549732539343734e+00, \
          4.374664141464968e+00,  2.938163982698783e+00)
    d = ( 7.784695709041462e-03,  3.224671290700398e-01, \
          2.445134137142996e+00,  3.754408661907416e+00)
 
    # Define break-points.
    plow  = 0.02425
    phigh = 1 - plow
 
    # Rational approximation for lower region:
    if p < plow:
       q = math.sqrt(-2*math.log(p))
       z = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
 
    # Rational approximation for upper region:
    elif phigh < p:
       q  = math.sqrt(-2*math.log(1-p))
       z = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
 
    # Rational approximation for central region:
    else:
       q = p - 0.5
       r = q*q
       z = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    # transform to non-standard:
    return mean + z * sd

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
    cmd = [ "bayesic",
            "caseonly",
            "--method", "peer",
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )
 
    logging.info( " ".join( cmd ) )
    
    output_path = os.path.join( output_dir, "peer.out" )
    with open( output_path, "w" ) as output_file:
        subprocess.call( cmd, stdout = output_file )
    
    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 1 )
    pd = experiment_params.get( "prevalence" )
    ccr = experiment_params.get( "case-control-ratio" )

    if num_tests == 0:
        with open( input_files.pair_path, "r" ) as pair_file:
            for line in pair_file:
                num_tests += 1

    zb = qnorm( 1 - ( alpha / ( num_tests * 4 ) ) )
    zbprim = ( 1 - pd ) * sqrt( 1 / ccr ) * zb

    return infer.num_significant_peer( output_path, [ 2, 4, 6, 8 ], zbprim, [ 3, 5, 7, 9 ], alpha )
