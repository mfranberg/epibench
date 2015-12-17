library( ggplot2 )
library( gtable )

argv = commandArgs( trailingOnly = TRUE )
if ( length( argv ) != 2 )
{
    message( "error: Wrong number of arguments." )
    message( "Usage: plot_power_joint model_input output_file" )
    quit( )
}

power_file = argv[ 1 ]
output_file = argv[ 2 ]

method_power = read.table( power_file, header = TRUE )
method_power$power = method_power$num_significant / method_power$npairs
method_power$power = method_power$num_significant / (method_power$npairs - method_power$num_missing)
method_power$power[ method_power$npairs - method_power$num_missing <= 10 ] = 0.0

pdf( output_file, width = 2 * 6.7, height = 2 * 6.7 / 1.618 )

cbPalette = c( "#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7" )
p = ggplot( method_power, aes( x = heritability, y = power, color = method ) ) + geom_line( ) + facet_grid( sample_size1 ~ maf1, scales = "free_x" ) +
    scale_x_continuous( "Heritability" ) +
    scale_y_continuous( "Power", limits = c( 0.0, 1.0 ) ) + 
    #scale_color_discrete( "Method" ) +
    scale_color_manual( "Method", values = cbPalette ) +
    geom_point( )

z <- ggplot_gtable(ggplot_build(p))

# add label for right strip
z <- gtable_add_cols(z, z$widths[[9]], 9)
z <- gtable_add_grob(z, 
                     list(rectGrob(gp = gpar(col = NA, fill = gray(0.5))),
                          textGrob("Sample size", rot = -90, gp = gpar(col = gray(1)))),
                     4, 10, 8, name = paste(runif(2)))

# add label for top strip
z <- gtable_add_rows(z, z$heights[[3]], 2)
z <- gtable_add_grob(z, 
                     list(rectGrob(gp = gpar(col = NA, fill = gray(0.5))),
                          textGrob("Minor allele frequency", gp = gpar(col = gray(1)))),
                     3, 4, 3, 8, name = paste(runif(2)))

# add margins
z <- gtable_add_cols(z, unit(1/8, "line"), 9)
z <- gtable_add_rows(z, unit(1/8, "line"), 3)

# draw it
# grid.newpage()
grid.draw(z)

dev.off( )
