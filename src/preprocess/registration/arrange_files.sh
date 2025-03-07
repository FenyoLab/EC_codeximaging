#!/bin/bash

# set -e

data_dir='/media/ssd02/lp2700/landing_pad/'

move_data() {
    registration_dir='/media/ssd02/lp2700/registration/data/'
    data_dir=$2

    qptiff_name="$(basename "$1" .qptiff)"
    new_img_dir=$registration_dir'images/'$qptiff_name
    new_ann_dir=$registration_dir'annotations/'$qptiff_name

    mkdir -p $new_img_dir
    mkdir -p $new_ann_dir

    IFS='-' read -ra parts <<< "$qptiff_name"
    svs_file=$(find "$data_dir" -type f -name "${parts[2]}*.svs")
    roi_name="$(basename "$svs_file" .svs)_rois.csv"

    cp $1 $new_img_dir
    cp $svs_file $new_img_dir
    cp $data_dir$roi_name $new_ann_dir
}

export -f move_data

find "$data_dir" -type f -name "*.qptiff" -exec echo {} \; \
-exec bash -c 'move_data "$0" "$1"' {} $data_dir \; 

