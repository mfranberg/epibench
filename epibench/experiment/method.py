import sys

##
# Iterates through the method directory and imports the methods'
# execute function.
#
# @param method_json A json object describing the methods.
# @param include_methods A list of names of methods to include.
#
# @return A list of tuples containing the method params and
#         the imported method function.
#
def find_methods(method_json, include_methods = None):
    method_funcs = [ ]
    for params in method_json.itervalues( ):
        name = params[ "method" ]
        if include_methods and not name in include_methods:
            continue

        try:
            if sys.version_info[ 0 ] == 2:
                name = name.encode( "ascii", "replace" )

            mod_name = "epibench.methods.method_{0}".format( name )
            mod = __import__( mod_name, None, None, [ "epibench" ] )
            method_funcs.append( ( params, mod.find_significant ) )
        except ValueError:
            print "Warning: method {0} not found.".format( name )
            continue

    return method_funcs

##
# Iterates through the types directory and import param_iter
# for the given type.
#
# @param experiment_type Type of experiment, e.g. 'binary'.
#
# @return The param_iter function of the experiment type.
#
def find_param_iter(experiment_type):
    try:
        if sys.version_info[ 0 ] == 2:
            experiment_type = experiment_type.encode( "ascii", "replace" )

        mod_name = "epibench.experiment.types.type_{0}".format( experiment_type )
        mod = __import__( mod_name, None, None, [ "epibench" ] )

        return mod.param_iter
    except ValueError:
        print "Warning: experiment {0} not found".format( experiment_type )
        return None

