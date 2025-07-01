# Setting up CELESTA conda environment

*This README focuses on the `celesta` environment only. See `README_celesta.md` for the complete guide to the CELESTA workflow.*

Make sure you clone the repo and run all scripts from `CC_codeximaging/bash_scripts`.

## Activate existing environment

```bash
source set_up_conda.sh
conda activate celesta
```

Then check that CELESTA is properly working in R:

```R
library(CELESTA)
```

## Creating new environment

If for some reason you need to recreate the `celesta` environment, you can either create it from a YAML file or from scratch.

First make sure you are directing conda to your own cache folder. Otherwise you will likely run into a bunch of permission errors. In your `~/.condarc` file, add a line like this (change to your own cache path):

```bash
pkgs_dirs:
  - /gpfs/data/proteomics/home/yb2612/conda/pkgs
```

Now you can proceed with setting up the environment.

### Create environment from YAML

```bash
source set_up_conda.sh
conda env create -f config/celesta_env.yaml --prefix=/gpfs/data/proteomics/projects/miniconda3/envs/celesta
```

If that worked, open up R and run the following:

```R
install.packages("argparse")
install.packages("rlang")
install.packages("devtools")
devtools::install_github("plevritis/CELESTA")
```

You might be asked to update packages. I usually choose to update all. 

Finally, try loading CELESTA in R:

```R
library(CELESTA)
```

### Create environment from scratch

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
conda install -c conda-forge cmake -y
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

## Issues

* I don't know what caused this issue, but my `r-base=4.4.2` broke and I had to upgrade it to `r-base=4.4.3`. This did not cause any problems with running CELESTA.

* The `CreateCelestaObj()` function, specifically `GetNeighborInfo()`, takes almost twice as long with this environment setup as in my personal R installation. I am not sure why. It probably has something to do with the `spdep` version.

## Citations

```bibtex
@article{zhang2022identification,
  title={Identification of cell types in multiplexed in situ images by combining protein expression and spatial information using CELESTA},
  author={Zhang, Weiruo and Li, Irene and Reticker-Flynn, Nathan E and Good, Zinaida and Chang, Serena and Samusik, Nikolay and Saumyaa, Saumyaa and Li, Yuanyuan and Zhou, Xin and Liang, Rachel and others},
  journal={Nature methods},
  volume={19},
  number={6},
  pages={759--769},
  year={2022},
  publisher={Nature Publishing Group US New York}
}
```