#!/bin/bash
#SBATCH --job-name=omero_download
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1
#SBATCH --output=download4_%A_%a.out
#SBATCH --error=download4_%A_%a.err
#SBATCH --mem=32G
#SBATCH --time=10:00:00
#SBATCH -p fn_short

source /gpfs/data/proteomics/home/lp2700/python_scripts/github_testing/CC_codeximaging/bash_scripts/.env

data_dir='/gpfs/data/proteomics/data/Cervical_mIF/'
mkdir $data_dir'downloads' # does this overwrite the folder 
for variable in 698744 698885 699026 699167 692515 692533 692518 692539
do 
        echo $variable
	/gpfs/data/proteomics/home/lp2700/data_gen/EC_mIF/OMERO.downloader-0.3.3/download.sh -b $data_dir'downloads' -s omero.nyumc.org -u $USER -w $PASSWORD -f binary Image:$variable
done 

target_qptiff=$(find $data_dir'downloads' -type f -name "*.qptiff" ! -name "._*")
target_svs=$(find $data_dir'downloads' -type f -name "*.svs" ! -name "._*")
#num_savory=$(target_svs | wc -l)
# Alternative methods to find basename
#target_qptiff=$(find $data_dir -type f -name "*.qptiff" ! -name '._*' -exec basename {} \;)
#target_svs=$(find $data_dir -type f -name "*.svs" ! -name '._*' -exec basename {} \;) 
mkdir -p $data_dir'qptiff_dat'
mkdir -p $data_dir'svs_dat'
for qptiffany in $target_qptiff 
do
        echo $qptiffany
        mv $qptiffany $data_dir'qptiff_dat/'
done

echo -e "$target_svs" | while IFS= read -r savory; do
    echo "$savory"
    more_savory="${savory// /_}"
    echo "$more_savory"
    mv "$savory" "$more_savory"
    mv "$more_savory" $data_dir'svs_dat/'
done

rm -r $data_dir'downloads/'  # rm download folder recursive       
