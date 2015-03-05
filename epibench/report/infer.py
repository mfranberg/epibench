from collections import defaultdict

def read_significance_value_from_file(csv_file, column, missing = "NA"):
    num_missing = 0
    value_list = list( )
    for line in csv_file:
        column_list = line.strip( ).split( )

        if column_list[ column ] != missing:
            value = 0.0
            try:
                value =  float( column_list[ column ] )
            except:
                continue

            value_list.append( ( column_list[ 0 ], column_list[ 1 ], value ) )
        else:
            num_missing += 1

    return value_list, num_missing

def num_significant_bonferroni(output_path, column, alpha, num_tests, missing = "NA"):
    with open( output_path, "r" ) as output_file:
        values, num_missing = read_significance_value_from_file( output_file, column )

        threshold = alpha
        if num_tests == 0:
            if len( values ) <= 0:
                return [ ]
            threshold = alpha / len( values )
        else:
            threshold = alpha / num_tests

        return filter( lambda x: x[ 2 ] <= threshold, values ), num_missing

def num_significant_threshold(output_path, column, threshold, missing = "NA"):
    with open( output_path, "r" ) as output_file:
        values, num_missing = read_significance_value_from_file( output_file, column )

        return filter( lambda x: x[ 2 ] <= threshold, values ), num_missing

def num_significant_multiple(pair_path, output_path, valid_columns, threshold, min_valid, missing = "NA"):
    pairs_left = set( )
    with open( pair_path, "r" ) as pair_file:
        for line in pair_file:
            column = line.strip( ).split( )
            pairs_left.add( ( column[ 0 ], column[ 1 ] ) )

    value_list = list( )
    with open( output_path, "r" ) as output_file:
        for line in output_file:
            column_list = line.strip( ).split( )
            
            row = [ ]
            for column in valid_columns:
                value = 0.0
                try:
                    value =  float( column_list[ column ] )
                except:
                    continue

                row.append( value )

            if len( row ) >= min_valid:
                value_list.append( ( column_list[ 0 ], column_list[ 1 ], max( row ) ) )
                pairs_left.remove( ( column_list[ 0 ], column_list[ 1 ] ) )

    return filter( lambda x: x[ 2 ] <= threshold, value_list ), len( pairs_left )

