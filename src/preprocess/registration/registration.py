import json
from valis import registration #, slide_io, valtils
import pdb
import os

data_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/registration'
image_path = 'images/20231019-0413-3D_Scan1'
annotation_path = 'annotations/20231019-0413-3D_Scan1'

slide_src_dir = os.path.join(data_path, image_path)
results_dst_dir = os.path.join(slide_src_dir, 'registration')
annotation_img_f = os.path.join(slide_src_dir, '0413-3D_1018924.svs')
target_img_f = os.path.join(slide_src_dir, '20231019-0413-3D_Scan1.qptiff') 
annotation_geojson_f = os.path.join(data_path, annotation_path, 'svs_rois.geojson')
warped_geojson_annotation_f = os.path.join(data_path, annotation_path, 'qptiff_rois.geojson')

# Perform registration
registrar = registration.Valis(src_dir = slide_src_dir, dst_dir = results_dst_dir,
                                reference_img_f = target_img_f, align_to_reference=True)

rigid_registrar, non_rigid_registrar, error_df = registrar.register()


#Transfer annotation from image associated with annotation_img_f and image associated with target_img_f
annotation_source_slide = registrar.get_slide(annotation_img_f)
target_slide = registrar.get_slide(target_img_f)

warped_geojson_from_to = annotation_source_slide.warp_geojson_from_to(annotation_geojson_f, target_slide)
warped_geojson = annotation_source_slide.warp_geojson(annotation_geojson_f)

# Save annotation as warped_geojson_annotation_f, which can be dragged and dropped into QuPath
with open(warped_geojson_annotation_f, 'w') as f:
    json.dump(warped_geojson, f)

registration.kill_jvm()
 