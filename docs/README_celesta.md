# Guide to CELESTA

## Activating `celesta` conda environment

```bash
source bash_scripts/set_up_conda.sh
conda activate celesta
```

## Setting up `celesta` conda environment

If for some reason you need to recreate the `celesta` environment, you can either create it from a YAML file or from scratch.

First make sure you are directing conda to your own cache folder. Otherwise you will likely run into a bunch of permission errors. In your `~/.condarc` file, add a line like this (change to your own cache path):

```bash
pkgs_dirs:
  - /gpfs/data/proteomics/home/yb2612/conda/pkgs
```

Now you can proceed with setting up the environment.

### From YAML

```bash
source bash_scripts/set_up_conda.sh
conda env create -f /gpfs/data/proteomics/home/yb2612/yaml/celesta_proteomics.yaml --prefix=/gpfs/data/proteomics/projects/miniconda3/envs/celesta
```

If that worked, open up R and run the following:

```R
install.packages("rlang")
install.packages("devtools")
devtools::install_github("plevritis/CELESTA")
```

You might be asked to update packages. I usually update all. If you encounter this error with `s2`:

```txt
CMake build of Abseil failed
** Abseil can be installed with:
** - apt-get install libabsl-dev
** - dnf install abseil-cpp-devel
** - brew install abseil
** If a system install of Abseil is not possible, cmake is required to build
** the internal vendored copy.
ERROR: configuration failed for package ‘s2’
* removing ‘/gpfs/data/proteomics/projects/miniconda3/envs/celesta/lib/R/library/s2’
* restoring previous ‘/gpfs/data/proteomics/projects/miniconda3/envs/celesta/lib/R/library/s2’

The downloaded source packages are in
	‘/tmp/RtmpKHftcQ/downloaded_packages’
Updating HTML index of packages in '.Library'
Making 'packages.html' ... done
Warning message:
In install.packages("s2") :
  installation of package ‘s2’ had non-zero exit status
```

You can solve this by doing:

```bash
conda install -c conda-forge cmake
```

Then in R, try installing `s2`:

```R
install.packages("s2")
```

Finally, try loading CELESTA in R:

```R
library(CELESTA)
```

### From scratch

```bash
conda create -n celesta -c conda-forge r-base=4.4.2 -y
conda activate celesta
```

Now there are a couple of tricky things about installing CELESTA from scratch.

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
install.packages("argparse")
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

See https://github.com/plevritis-lab/CELESTA for more details.

## Running CELESTA

Clone the `CC_codeximaging` repo and navigate to `bash_scripts`. 

Open `run_celesta.sh`, edit arguments as needed, and run.

The actual R script is in `celesta_phenotyping.R`.

## Inspecting CELESTA results

Results will be saved to the `output_dir/project_title` folder specified in `run_celesta.sh`. This will include the following:
* Final Celesta object (RDS)
* Final cell assignments (CSV)
* Cell assignment plot
* Expression probability plots

## Evaluating CELESTA performance

This will work if you have ground truth labels.