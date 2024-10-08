import json
from valis import registration #, slide_io, valtils
import pdb
import os

def convert_rois_with_registration(sample, sample_svs_name, sample_qptiff_name):

    #define paths 
    data_path = '../data'
    image_path = 'images'
    annotation_path = 'annotations'
    slide_path = sample 
    out_path = 'registration_results'
    
    slide_src_dir = os.path.join(data_path, image_path, slide_path)
    results_dst_dir = os.path.join(data_path, out_path)
    annotation_img = os.path.join(slide_src_dir, f'{sample_svs_name}.svs')
    target_img = os.path.join(slide_src_dir, f'{sample_qptiff_name}.qptiff')

    
    annotation_geojson = os.path.join(data_path, annotation_path, slide_path, f'{sample_svs_name}_rois.geojson')
    warped_geojson_annotation = os.path.join(data_path, annotation_path, slide_path, f'{sample_qptiff_name}_rois.geojson')
    
    
    #perform registration
    registrar = registration.Valis(src_dir = slide_src_dir, dst_dir = results_dst_dir, reference_img_f = target_img, align_to_reference=True)
    rigid_registrar, non_rigid_registrar, error_df = registrar.register()


    #Transfer annotation from image associated with annotation_img_f and image associated with target_img_f
    annotation_source_slide = registrar.get_slide(annotation_img)
    target_slide = registrar.get_slide(target_img)

    warped_geojson_from_to = annotation_source_slide.warp_geojson_from_to(annotation_geojson, target_slide)
    warped_geojson = annotation_source_slide.warp_geojson(annotation_geojson)

    # Save annotation as warped_geojson_annotation_f, which can be dragged and dropped into QuPath
    with open(warped_geojson_annotation, 'w') as f:
        json.dump(warped_geojson, f)
    
    registration.kill_jvm()