
def read_significance_value_from_file(csv_file, column):
    csv_file.seek( 0 )
    value_list = list( )
    for line in csv_file:
        column_list = line.strip( ).split( )

        value = 0.0
        try:
            value =  float( column_list[ column ] )
        except:
            continue

        if value >= 0.0 and value <= 1.0:
            value_list.append( ( column_list[ 0 ], column_list[ 1 ], value ) )

    return value_list

def num_significant_bonferroni(output_path, column, alpha, num_tests):
    with open( output_path, "r" ) as output_file:
        values = read_significance_value_from_file( output_file, column )

        threshold = alpha
        if num_tests == 0:
            if len( values ) <= 0:
                return [ ]
            threshold = alpha / len( values )
        else:
            threshold = alpha / num_tests

        return filter( lambda x: x[ 2 ] <= threshold, values )

def num_significant_threshold(output_path, column, threshold):
    with open( output_path, "r" ) as output_file:
        values = read_significance_value_from_file( output_file, column )

        return filter( lambda x: x[ 2 ] <= threshold, values )
