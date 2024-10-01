import json
from valis import registration
import pdb
import os

data_path = '/home/fenyopc002/as18894/dat/registration'
image_path = 'images/20231019-0413-3D_Scan1'
annotation_path = 'annotations/20231019-0413-3D_Scan1'

slide_src_dir = os.path.join(data_path, image_path)
results_dst_dir = os.path.join(slide_src_dir, 'slide_registration')
annotation_img_f = os.path.join(slide_src_dir, '0413-3D_1018924.svs')
target_img_f = os.path.join(slide_src_dir, '0413-3D_1018924.svs') 
annotation_geojson_f = os.path.join(data_path, annotation_path, 'svs_rois.geojson')
warped_geojson_annotation_f = os.path.join(data_path, annotation_path, 'qptiff_rois.geojson')
registered_slide_dst_dir = "/home/fenyopc002/as18894/dat/registration/images/20231019-0413-3D_Scan1/slide_registration"

# Perform registration
registrar = registration.Valis(src_dir = slide_src_dir, dst_dir = results_dst_dir,
                                reference_img_f = target_img_f, align_to_reference=True)

rigid_registrar, non_rigid_registrar, error_df = registrar.register()

# Save all registered slides as ome.tiff
registrar.warp_and_save_slides(registered_slide_dst_dir, crop="overlap", compression = 'jp2k', Q = 100)

registration.kill_jvm()
