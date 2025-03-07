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
for variable in 701231 701509 692524 692536 #698744 698885 699026 699167 692515 692533 692518 692539
do 
        echo $variable
	/gpfs/data/proteomics/home/lp2700/data_gen/EC_mIF/OMERO.downloader-0.3.3/download.sh -b $data_dir'downloads' -s omero.nyumc.org -u $USER -w $PASSWORD -f binary Image:$variable
done 

target_qptiff=$(find $data_dir'downloads' -type f -name "*.qptiff" ! -name "._*")
target_svs=$(find $data_dir'downloads' -type f -name "*.svs" ! -name "._*")
#num_savory=$(target_svs | wc -l)
# Alternative methods to find basename
# target_qptiff=$(find $data_dir -type f -name "*.qptiff" ! -name '._*' -exec basename {} \;)
# target_svs=$(find $data_dir -type f -name "*.svs" ! -name '._*' -exec basename {} \;) 
# this code will move files both to epoch (rsync) and move  them to appropriate folders for preprocessing
mkdir -p $data_dir'qptiff_dat'
mkdir -p $data_dir'svs_dat'
for qptiffany in $target_qptiff 
do
        echo $qptiffany
        rsync -avzP $qptiffany epoch:/media/ssd02/lp2700/landing_pad/
        mv $qptiffany $data_dir'qptiff_dat/'
done
# same as above, but will remove " " characters from svs file names, copy yo epoch, and move
echo -e "$target_svs" | while IFS= read -r savory; do
    echo "$savory"
    more_savory="${savory// /_}"
    echo "$more_savory"
    mv "$savory" "$more_savory"
    rsync -avzP "$more_savory" epoch:/media/ssd02/lp2700/landing_pad/
    mv "$more_savory" $data_dir'svs_dat/'
done

rm -r $data_dir'downloads/'  # rm download folder recursive       
