library( plyr )
library( reshape2 )

argv = commandArgs( trailingOnly = TRUE )
if ( length( argv ) != 3 )
{
    message( "error: Wrong number of arguments." )
    message( "Usage: plot_power_joint name model_input output_file" )
    quit( )
}

name = argv[ 1 ]
power_file = argv[ 2 ]
output_file = argv[ 3 ]

fwer_data = read.table( power_file, header = TRUE )

fwer_tbl = ddply( fwer_data, .(effect_level, ncases, ncontrols, maf1, maf2, num_true, num_false, params, method_name), summarize, fwer = mean( num_significant > 0 ) )
write.table( fwer_tbl, output_file, row.names = FALSE, col.names = TRUE )

small_tbl = dcast( fwer_tbl, effect_level + ncases + ncontrols + maf1 + maf2 + num_true + num_false + params ~ method_name, value.var = "fwer" )
small_tbl$name = name
write.table( small_tbl, paste0( output_file, ".2d" ), row.names = FALSE, col.names = TRUE )
