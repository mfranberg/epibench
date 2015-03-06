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

# Defining experiments

## The actual experiment

The first step is to define an experiment. Here is an example where we want to look at the power for a specific model.

    {
      "experiments" : [
        {
          "type" : "geno",
          "model" : "binomial",
          "maf" : [ 0.2, 0.2, 0.3, 0.3, 0.4, 0.4 ],
          "sample-size" : [ 2000, 2000, 3000, 3000, 4000, 4000 ],
          "num-pairs" : 200,
          "param" : [
            0.5, 0.5, 0.5,
            0.5, 0.55, 0.55,
            0.5, 0.55, 0.55,

            0.5, 0.5, 0.5,
            0.5, 0.6, 0.6,
            0.5, 0.6, 0.6,

            0.5, 0.5, 0.5,
            0.5, 0.65, 0.65,
            0.5, 0.65, 0.65,

            0.5, 0.5, 0.5,
            0.5, 0.7, 0.7,
            0.5, 0.7, 0.7
          ]
        }
      ]
    }

Here the type geno indicates that we will simulate genotypes conditional on the phenotype, model is the distribution around the mean parameter here binomial (i.e. case/control), maf describes the minor allele frequency for both variants, here we will vary this over 0.2, 0.3 and 0.4 for both variants, sample-size is the sample size in each group, here varied over 2000, 3000 and 4000 in each group, then we have the number of pairs that will be generated for each parameter combination, here 2000, finally we have the model parameters, here a double dominant model, in this case the penetrance for each genotype is given, we have 4 sets.

## The methods to evaluate

The second step is to define which methods to run and with what parameters. A method is defined by two things, a Python file that describes how to execute the method, and a .json-file that defines parameters for that and other methods, that may be changed over the course of an experiment.

The Python file should return a list of the number of significant pairs, and the number of pairs for which no significance value computed, i.e. missing values. Here the *num_significant_bonferroni* function does this for a given output file.

  def find_significant(method_params, input_files, output_dir):
    cmd = [ "bayesic",
            "-m", "loglinear",
            input_files.pair_path,
            input_files.plink_prefix ]

    if input_files.pheno_path:
        cmd.extend( [ "-p", input_files.pheno_path ] )

    output_path = os.path.join( output_dir, "loglinear.out" )
    with open( output_path, "w" ) as output_file:
        subprocess.call( cmd, stdout = output_file )

    alpha = method_params.get( "alpha", 0.05 )
    num_tests = method_params.get( "num-tests", 1 )

    return infer.num_significant_bonferroni( output_path, 2, alpha, num_tests )

The next step is to define the .json-file that describes which methods and with what parameters to run in the experiment. In this case it defines the number of tests to correct for and the significance level.

    {
      "methods" : [
        {
          "name" : "Log-linear",
          "method" : "loglinear",
          "num-tests" : 1000,
          "alpha" : 0.05
        }
      ]
    }

## Running

The experiment is run by the following command

    > epibench run --method-file method.json --experiment-file experiment.json --out output/

This will run all methods defined in method.json, for all experiments defined in experiment.json. The output directory will then contain the results, typically it looks something like this:

    > ls output/
    data  experiment.log  experiments.json  method  result

The data directory contains temporary data files, experiment.log is a log file of the run, experiments.json is a copy of the input experiment.json, method contains temporary results for each method, and result contains final results for each method. This data can then be compiled into plots and tables by:

    > epibench compile output/

This creates the *final* directory that contains the compiled results for each experiment.

    > ls output/final/
    experiment0.pdf

This plot will then show the power for each parameter combination, and *output/result/experiment0.out* contains the raw files for which plot is based, if you want to plot it in another way.
