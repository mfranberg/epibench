library( plyr )

argv = commandArgs( trailingOnly = TRUE )
if ( length( argv ) != 2 )
{
    message( "error: Wrong number of arguments." )
    message( "Usage: plot_power_joint model_input output_file" )
    quit( )
}

power_file = argv[ 1 ]
output_file = argv[ 2 ]

fwer_data = read.table( power_file, header = TRUE )

fwer_tbl = ddply( fwer_data, .(effect_level, method_name), summarize, fwer = mean( num_significant ) )
write.table( fwer_tbl, output_file, row.names = FALSE, col.names = TRUE )
