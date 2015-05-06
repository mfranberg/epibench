##
# Computes the heritability V(P|G) / V(P).
#
# @param model The type of model used (normal, binomial, poisson etc)
# @param mu The mean value for each genotype.
# @param maf The minor allele frequency for both locus.
# @param dispersion The dispersion parameter if applicable.
#
# @return The heritability.
#
def heritability(model, mu, maf, dispersion):
    p = [ ( 1 - maf[ 0 ] )**2, 2 * maf[ 0 ] * ( 1 - maf[ 0 ] ), ( maf[ 0 ] )**2 ]
    q = [ ( 1 - maf[ 1 ] )**2, 2 * maf[ 1 ] * ( 1 - maf[ 1 ] ), ( maf[ 1 ] )**2 ]

    joint_maf =  [ p[ 0 ] * q[ 0 ], p[ 0 ] * q[ 1 ], p[ 0 ] * q[ 2 ],
                   p[ 1 ] * q[ 0 ], p[ 1 ] * q[ 1 ], p[ 1 ] * q[ 2 ],
                   p[ 2 ] * q[ 0 ], p[ 2 ] * q[ 1 ], p[ 2 ] * q[ 2 ] ]

    pop_mu = sum( m * f for m, f in zip( mu, joint_maf ) )
    h_numerator = sum( f * m**2 for m, f in zip( mu, joint_maf ) ) - pop_mu**2

    h_denominator = h_numerator
    if model == "binomial":
        h_denominator += sum( m*(1-m) * f for m, f in zip( mu, joint_maf ) )
    elif model == "poisson":
        h_denominator += pop_mu
    else:
        h_denominator += sum( d**2 * f for d, f in zip( [ dispersion ] * 9, joint_maf ) )

    return h_numerator / h_denominator

##
# Computes the disease prevalence.
#
def prevalence(mu, maf):
    p = [ ( 1 - maf[ 0 ] )**2, 2 * maf[ 0 ] * ( 1 - maf[ 0 ] ), ( maf[ 0 ] )**2 ]
    q = [ ( 1 - maf[ 1 ] )**2, 2 * maf[ 1 ] * ( 1 - maf[ 1 ] ), ( maf[ 1 ] )**2 ]

    joint_maf =  [ p[ 0 ] * q[ 0 ], p[ 0 ] * q[ 1 ], p[ 0 ] * q[ 2 ],
                   p[ 1 ] * q[ 0 ], p[ 1 ] * q[ 1 ], p[ 1 ] * q[ 2 ],
                   p[ 2 ] * q[ 0 ], p[ 2 ] * q[ 1 ], p[ 2 ] * q[ 2 ] ]

    return sum( m * f for m, f in zip( mu, joint_maf ) )
