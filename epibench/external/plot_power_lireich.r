library( ggplot2 )
library( gtable )
library( proto )
library( plyr )

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

method_power = read.table( experiment_file, header = TRUE, stringsAsFactors = FALSE )
method_power$power = method_power$num_significant / method_power$npairs
method_power$power = method_power$num_significant / (method_power$npairs - method_power$num_missing)
method_power$power[ method_power$npairs - method_power$num_missing <= 10 ] = 0.0

tiff( output_file, width = 7.5, height = 7.5 / 1.618, family = "Times", units = "in", res = 300, compression = "lzw", pointsize = 10 )

cbPalette = c( "#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7" )
p = ggplot( method_power, aes( x = power, colour = method ) ) + stat_ecdf_reversed( geom = "smooth" ) + facet_grid( sample_size1 ~ desired_h2, scales = "free_x" ) +
    scale_x_continuous( "t" ) +
    scale_y_continuous( "Fraction of models with power >= t", limits = c( 0.0, 1.0 ) ) +
    scale_color_manual( "Method", values = cbPalette ) + theme(plot.margin=unit(c(2,2,2,2),"points"), axis.text.x = element_text(size=6), axis.text.y = element_text(size=6))

z <- ggplot_gtable(ggplot_build(p))

# add label for right strip
z <- gtable_add_cols(z, z$widths[[9]], 9)
z <- gtable_add_grob(z, 
                     list(rectGrob(gp = gpar(col = NA, fill = gray(0.5))),
                          textGrob("Sample size", rot = -90, gp = gpar(col = gray(1), fontsize=10))),
                     4, 10, 8, name = paste(runif(2)))

# add label for top strip
z <- gtable_add_rows(z, z$heights[[3]], 2)
z <- gtable_add_grob(z, 
                     list(rectGrob(gp = gpar(col = NA, fill = gray(0.5))),
                          textGrob("Heritability", gp = gpar(col = gray(1), fontsize=10))),
                     3, 4, 3, 8, name = paste(runif(2)))

# add margins
z <- gtable_add_cols(z, unit(1/8, "line"), 9)
z <- gtable_add_rows(z, unit(1/8, "line"), 3)

# draw it
# grid.newpage()
grid.draw(z)

dev.off( )

library( reshape )
penetrance = sapply( method_power$params, function(params){ as.numeric(unlist(strsplit(params, ","))) } )
P = matrix(
    c( 1, 0, 0, 0, 0, 0, 0, 0, 0,
       1, 1, 0, 0, 0, 0, 0, 0, 0,
       1, 0, 1, 0, 0, 0, 0, 0, 0,
       1, 0, 0, 1, 0, 0, 0, 0, 0,
       1, 1, 0, 1, 0, 1, 0, 0, 0,
       1, 0, 1, 1, 0, 0, 1, 0, 0,
       1, 0, 0, 0, 1, 0, 0, 0, 0,
       1, 1, 0, 0, 1, 0, 0, 1, 0,
       1, 0, 1, 0, 1, 0, 0, 0, 1), ncol = 9, byrow = TRUE )
Pinv = solve( P )

param.names = c( "a", "b1", "b2", "c1", "c2", "d11", "d12", "d21", "d22" )

B = t( Pinv %*% log( penetrance / ( 1 - penetrance ) ) )
colnames( B ) = param.names
logit_beta = melt( cbind( method_power, B ), measure.vars = param.names )

B = t( Pinv %*% penetrance )
colnames( B ) = param.names
pen_beta = melt( cbind( method_power, B ), measure.vars = param.names )

write.table( logit_beta, "test.out", col.names = TRUE, row.names = FALSE, quote = TRUE )

tiff( paste0( output_file, ".logit.tif" ), width = 7.5, height = 7.5 / 1.618, units = "in", res = 300, compression = "lzw" )

ggplot( logit_beta, aes( x = value, color = variable, group = variable ) ) + geom_density( ) + facet_grid( sample_size1 ~ desired_h2, scales = "free_x" ) +
    scale_x_continuous( "Size of effect" ) +
    scale_y_continuous( "Density" ) +
    scale_color_discrete( "Parameter" ) +
    theme( plot.margin = unit( c( 2,2,2,2 ), "points" ),
           text = element_text( size = 8 ) )

dev.off( )

tiff( paste0( output_file, ".penetrance.tif" ), width = 7.5, height = 7.5 / 1.618, units = "in", res = 300, compression = "lzw" )

ggplot( pen_beta, aes( x = value, color = variable, group = variable ) ) + geom_density( ) + facet_grid( sample_size1 ~ desired_h2, scales = "free_x" ) +
    scale_x_continuous( "Size of effect" ) +
    scale_y_continuous( "Density" ) +
    scale_color_discrete( "Parameter" ) +
    theme( plot.margin = unit( c( 2,2,2,2 ), "points" ),
           text = element_text( size = 8 ) )

dev.off( )

ih_power = subset( method_power, method == "Static" )
ih_power$ih = 0.0
ih_power$m1 = 0.0
ih_power$m2 = 0.0
ih_power$h2 = 0.0
ih_power$prev = 0.0

for(i in 1:nrow(ih_power))
{
    p = as.numeric(unlist(strsplit(ih_power$params[ i ], ",")))
    m = ih_power$maf1[ i ]
    maf = c( (1-m)**2, 2*m*(1-m), m**2 )

    prev = 0.0
    m1 = c( 0, 0, 0 )
    m2 = c( 0, 0, 0 )    

    for(j in 1:3)
    {
        for(k in 1:3)
        {
            m1[ j ] = m1[ j ] + p[ 3 * (j - 1) + k ] * maf[ k ]
            m2[ k ] = m2[ k ] + p[ 3 * (j - 1) + k ] * maf[ j ]
            prev = prev + p[ 3 * (j - 1) + k ] * maf[ j ] * maf[ k ]
        }
    }

    denom = prev * ( 1 - prev )
    h2 = 0.0
    mh1 = 0.0
    mh2 = 0.0
    for(j in 1:3)
    {
        mh1 = mh1 + (prev - m1[ j ])**2 * maf[ j ]
        mh2 = mh2 + (prev - m2[ j ])**2 * maf[ j ]
        for(k in 1:3)
        {
            h2 = h2 + (prev - p[ 3 * (j - 1) + k ])**2 * maf[ j ] * maf[ k ]
        }
    }

    ih_power$ih[ i ] = (h2 - mh1 - mh2) / (h2)
    ih_power$m1[ i ] = mh1
    ih_power$m2[ i ] = mh2
    ih_power$h2[ i ] = h2
    ih_power$prev[ i ] = prev
}

pdf( paste0( output_file, ".prev.pdf" ), width = 2 * 6.7, height = 2 * 6.7 / 1.618 )

ggplot( ih_power, aes( x = prev ) ) + stat_ecdf( geom = "smooth" ) + facet_grid( sample_size1 ~ desired_h2, scales = "free_x" ) +
    scale_x_continuous( "Prevalence" ) +
    scale_y_continuous( "Cumulative distribution" )

dev.off( )

tiff( paste0( output_file, ".h2.tif" ), width=6.15, height=4.07, units = "in", res = 300, compression = "lzw" )

ggplot( ih_power, aes( x = 1-ih ) ) + stat_ecdf( geom = "smooth" ) +
    scale_x_continuous( "Marginal heritability fraction" ) +
    geom_abline( intercept = 0, slope = 1 ) +
    scale_y_continuous( "Cumulative distribution" ) +
    theme( plot.margin = unit( c( 2,2,2,2 ), "points" ),
           text = element_text( size = 8 ) )

dev.off( )

cat( sum( ih_power$ih <= 0.5 ) / length( ih_power$ih ) )

write.table( ih_power, paste0( output_file, ".h2.out" ), col.names = TRUE, row.names = FALSE, quote = FALSE )
