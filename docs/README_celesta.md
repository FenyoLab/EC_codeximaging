# Guide to CELESTA

## Setting up a `celesta` conda environment

There are a couple of tricky things about installing CELESTA. 

First is that it relies on `devtools`, which can be a pain to install properly. Thanks to Amit Kohli and Matthew J. Oldach for their instructions in https://stackoverflow.com/questions/20923209/problems-installing-the-devtools-package. Below is what worked for me:

```bash
conda create -n celesta -c conda-forge r-base=4.4.2 -y
conda activate celesta
conda install -c conda-forge libcurl openssl fontconfig libxml2 harfbuzz fribidi freetype libpng libtiff libjpeg-turbo -y
conda install -c r r-devtools -y
```

Now install CELESTA's dependencies:
```
conda install -c conda-forge gdal liblzma zlib mysql-libs -y
conda install -c conda-forge r-sf r-spdep -y
```

If that worked, open up R and run the following:

```R
install.packages("rlang")
install.packages("devtools")
devtools::install_github("plevritis/CELESTA")
````

Finally, try loading CELESTA in R:

```R
library(CELESTA)
```

## Preparing CELESTA inputs

CELESTA requires the following:

1. Prior marker info (CSV)
2. Imaging data (CSV)

## Running CELESTA

Open `bash_scripts/run_celesta.sh`, enter arguments as needed, and run. 

The actual R script is in `celesta_phenotyping.R`.

## Inspecting CELESTA results

Results will be saved to the `output_dir/project_title` folder as you specified in `run_celesta.sh`. This will include the following:
* Final Celesta object (RDS)
* Final cell assignments (CSV)
* Cell assignment plot
* Expression probability plots

## Evaluating CELESTA performance

This will work if you have ground truth labels.