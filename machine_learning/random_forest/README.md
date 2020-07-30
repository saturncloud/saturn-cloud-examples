# Random Forest

## RAPIDS vs. Spark

Code supporting article [here]()

RAPIDS example was run in [Saturn Cloud](https://www.saturncloud.io/), and Spark example was run in Amazon EMR

## Hardware and environments

Both clusters were run with 20 workers:
* RAPIDS: `g4dn.xlarge`
	* 4 CPU, 16 GB RAM
	* 1 GPU, 16 GB GPU RAM
	* On-demand price: $0.526/hour
	* See `environment.yml` for packages
* Spark: `r5.2xlarge`
    * 8 CPU, 64 GB RAM
    * On-demand price: $0.504/hour
    * Spark version 2.4.5

Saturn Cloud can also launch Dask clusters with NVIDIA Tesla V100 GPUs, but we chose `g4dn.xlarge` for this exercise to maintain a similar hourly cost profile as the Spark cluster.

Pricing as of 7/26/2020 in US East (Ohio) region.