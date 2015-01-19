# Introduction

This benchmark evaluates statistical models for inferring epistasis, or
interaction, between geneotypes or genotype and an environmental factor.
Currently it only evaluates two-locus models. Both synthetic genotypes
and real genotypes can be used. A method is evaluated by writing a
Python-wrapper script for it. The framework supports and advocates
that these analyses are computed on a cluster, since they often are
computationally intense.

This benchmark is by no means complete, and serves only to understand
the general behavior of the methods that are evaluated. One important
scenario is to find circumstances when a method produces results that may be
difficult to interpret.

The key questions addressed are:

* False positive rate of the test/method
* Family-wise error rate
* Distribution of the power of the method
* Power for discovering a single pair (simulate one pair at a time)
* Power for discovering a pair on a simulated chromosome

Data is generated using generalized linear models to accomodate the
wide range of different phenotype distributions. This framework
primarily focuses on phenotypes that are generated from a normal
or bernoulli distribution, in which the mean parameter is described by a
regression model.

The class of null models that we consider are:

* No variant is associated with the phenotype
* A single variant is associated with the phenotype
* Two or more variants are associated with the phenotype by an additive model (using an arbitrary link function).

The task of defining alternative models is not always
clear cut because of the link function. Here we use
the following models:

* Continuous analogous of simple and commonly used genetics models like double dominant.
* Continuous variants of Li and Reich catalogue of epistatic models.
* Random models where the interaction effects in a generalized linear model are taken from a given distribution.

Future directions of this benchmark would be to include models for:
* Relatedness
* Genotyping errors
* Population stratification
* Covariates

# Running

## False positive rate

epibench method-fpr --cluster "sbatch" --maf 0.1-0.5 --sample-size 2000/2000 --method my.py --out fpr_dir
epibench method-fpr --compile --in fpr_dir

## Family-wise error rate

epibench method-fwer --cluster "sbatch" --maf 0.3 --sample-size 2000 --method my.py --out fwer_dir
