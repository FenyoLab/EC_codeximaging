# local with mounted (for me) # can input specific files if needed, I need to include a command to delete images after run to save space

sample_names=$(find  'Downloads/ROIS_FOR_REG' -type f  -name '.*' -exec basename {} \;)
#mkdir Desktop/mount2/data_dump/rois_temp
cd Downloads/ROIS_FOR_REG
for sample in $sample_names 
do 
        echo $sample
    rm $sample
done 

mv ~/Downloads/ROIS_FOR_REG/* ~/Desktop/mount2/data_dump/rois_temp/

# in cluster mv /gpfs/data/proteomics/home/lp2700/data_dump/rois_temp/* /gpfs/data/proteomics/data/Cervical_mIF/

sample_names=$(find  /gpfs/data/proteomics/data/Cervical_mIF -type f  -name '*.csv' -exec basename {} \;)
#mkdir Desktop/mount2/data_dump/rois_temp
cd /gpfs/data/proteomics/data/Cervical_mIF/
for sample in $sample_names 
do 
        echo $sample
    mv $sample /gpfs/data/proteomics/data/Cervical_mIF/roi_annotations/
done

