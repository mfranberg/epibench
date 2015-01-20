
##
# Any method to be evaluated should define the following methods.
#

##
# Given a plink file this function should apply
# the algorithm a return a list of the significant
# pairs.
#
# @param experiment_params A list of parameters used in the experiment,
#                          a ExperimentParams object. This can for example
#                          include the number of tests to correct for
#                          (if applicable).
#
# @param method_params This contains parameters for the method passed by the
#                      method json file, and is supplied as a dict directly.
#
# @param plink_file A plink file object to apply the algorithm to. This object
#                   contains a path to the plink, phenotype and covariate file.
#
# @param output_dir A directory where the method can create temporary files used
#                   during the analysis.
#
def find_significant(experiment_params, method_params, plink_file, output_dir):
    return [ ]
