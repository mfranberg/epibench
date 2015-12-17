library( ggplot2 )
library( gtable )
library( proto )

### GGPLOT reversed ecdf

stat_ecdf_reversed <- function (mapping = NULL, data = NULL, geom = "step", position = "identity", n = NULL, ...) {
    StatEcdfReversed$new(mapping = mapping, data = data, geom = geom, position = position, n = n, ...)
}

StatEcdfReversed <- proto(ggplot2:::Stat, {
    objname <- "ecdf"
    
    calculate <- function(., data, scales, n = NULL, ...) {
        
        # If n is NULL, use raw values; otherwise interpolate
        if (is.null(n)) {
            xvals <- unique(data$x)
        } else {
            xvals <- seq(min(data$x), max(data$x), length.out = n)
        }
        
        y <- 1 - ecdf(data$x)(xvals)
        
        # make point with y = 0, from plot.stepfun
        rx <- range(xvals)
        if (length(xvals) > 1L) {
            dr <- max(0.08 * diff(rx), median(diff(xvals)))
        } else {
            dr <- abs(xvals)/16
        }
        
        x0 <- rx[1] 
        x1 <- rx[2]
        y0 <- 1
        y1 <- 0
        
        data.frame(x = c(x0, xvals, x1), y = c(y0, y, y1))
    }
    
    default_aes <- function(.) aes(y = ..y..)
    required_aes <- c("x")
    default_geom <- function(.) ggplot2:::GeomStep
})

### End GGPLOT reversed ecdf

argv = commandArgs( trailingOnly = TRUE )
if ( length( argv ) != 2 )
{
    message( "error: Wrong number of arguments." )
    message( "Usage: plot_power_all experiment_output output_file" )
    quit( )
}

experiment_file = argv[ 1 ]
output_file = argv[ 2 ]

method_power = read.table( experiment_file, header = TRUE )
method_power$power = method_power$num_significant / ( method_power$npairs - method_power$num_missing )
method_power$power[ method_power$num_missing == method_power$npairs ] = 0.0

pdf( output_file, width = 2 * 6.7, height = 2 * 6.7 / 1.618, family = "Times" )

cbPalette = c( "#000000", "#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442" )
p = ggplot( method_power, aes( x = power, colour = method ) ) + stat_ecdf_reversed( geom = "smooth" ) + facet_grid( sample_size1 ~ maf1, scales = "free_x" ) +
    scale_x_continuous( "t" ) +
    scale_y_continuous( "Fraction of models with power >= t", limits = c( 0.0, 1.0 ) ) +
    scale_color_manual( "Method", values = cbPalette )

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
embedFonts( output_file )
