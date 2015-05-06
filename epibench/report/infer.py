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

def num_missing_multiple(output_path, valid_columns, missing = "NA"):
    value_list = list( )
    num_missing = 0
    with open( output_path, "r" ) as output_file:
        for line in output_file:
            column_list = line.strip( ).split( )
            
            row = [ ]
            for column in valid_columns:
                if column_list[ column ] == "NA":
                    num_missing += 1
                    break

    return num_missing

def num_significant_multiple(output_path, valid_columns, threshold, min_valid, missing = "NA"):
    value_list = list( )
    num_missing = 0
    with open( output_path, "r" ) as output_file:
        for line in output_file:
            column_list = line.strip( ).split( )
            
            row = [ ]
            num_missing_in_row = 0
            for column in valid_columns:
                if column_list[ column ] == missing:
                    num_missing_in_row += 1

                value = 0.0
                try:
                    value =  float( column_list[ column ] )
                except:
                    continue

                row.append( value )

            if len( row ) >= min_valid:
                value_list.append( ( column_list[ 0 ], column_list[ 1 ], max( row ) ) )
            elif num_missing_in_row > 0:
                num_missing += 1

    return filter( lambda x: x[ 2 ] <= threshold, value_list ), num_missing


def num_significant_peer(output_path, stage1_columns, stage1_threshold, stage2_columns, stage2_threshold, missing = "NA"):
    value_list = list( )
    num_missing = 0
    with open( output_path, "r" ) as output_file:
        for line in output_file:
            column_list = line.strip( ).split( )
            
            stage1 = [ ]
            stage2 = [ ]
            for column1, column2 in zip( stage1_columns, stage2_columns ):
                if column_list[ column1 ] == missing or column_list[ column2 ] == missing:
                    continue

                value1 = 0.0
                value2 = 0.0
                try:
                    value1 =  float( column_list[ column1 ] )
                    value2 =  float( column_list[ column2 ] )
                except:
                    continue

                stage1.append( value1 )
                stage2.append( value2 )

            if len( stage1 ) <= 0 or len( stage2 ) <= 0 or len( stage1 ) != len( stage2 ):
                num_missing += 1
                continue

            best_index, best_value = max( enumerate( stage1 ), key = lambda x: x[ 1 ] )
            if best_value >= stage1_threshold and stage2[ best_index ] <= stage2_threshold:
                value_list.append( ( column_list[ 0 ], column_list[ 1 ], stage2[ best_index ] ) )

    return value_list, num_missing


