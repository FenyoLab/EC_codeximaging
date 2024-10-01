import json
from valis import registration, slide_io, valtils
import pdb
import os
from types import SimpleNamespace
#from utils import helper

#https://valis.readthedocs.io/en/latest/examples.html


data_path = '/gpfs/data/proteomics/projects/Endometrial_mIF/EC_codeximaging_results/registration_test'
image_path = 'images/20231012-9784-6H_Scan1'
annotation_path = 'annotations/20231012-9784-6H_Scan1'

slide_src_dir = os.path.join(data_path, image_path)
results_dst_dir = os.path.join(slide_src_dir, 'slide_registration')
annotation_img_f = os.path.join(slide_src_dir, '9784-6H_1018921.svs')
target_img_f = os.path.join(slide_src_dir, '20231012-9784-6H_Scan1.qptiff') 
annotation_geojson_f = os.path.join(data_path, annotation_path, 'svs_rois.geojson')
warped_geojson_annotation_f = os.path.join(data_path, annotation_path, 'qptiff_rois.geojson')
pdb.set_trace()
reader_cls = slide_io.get_slide_reader(image_path, series=0) #Get appropriate slide reader class
img_reader = reader_cls(image_path, series=0)

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



# def run_registration(config_yaml):
#     # Load the configuration
#     run_config = helper.load_yaml_file(config_yaml)
#     config = SimpleNamespace(**run_config)

#     register_ROIs(data_path = config.data_path)

# def register_ROIs(data_path):
#     pdb.set_trace()
#     image_path = f'images/20231012-9784-6H_Scan1'
#     annotation_path = f'annotations/20231012-9784-6H_Scan1'

#     slide_src_dir = os.path.join(data_path, image_path)
#     results_dst_dir = os.path.join(slide_src_dir, 'slide_registration')
#     #os.makedirs(results_dst_dir, exist_ok=True)
        
#     #svs_file = [img for img in os.listdir(slide_src_dir) if ".svs" in img][0]
#     annotation_img_f = os.path.join(slide_src_dir, '20231012-9784-6H_Scan1_v2.qptiff')
#     target_img_f = os.path.join(slide_src_dir, '20231012-9784-6H_Scan1.qptiff') 
        
#     #os.makedirs(os.path.join(data_path, annotation_path), exist_ok=True)
#     annotation_geojson_f = os.path.join(data_path, annotation_path, 'svs_rois.geojson')
#     warped_geojson_annotation_f = os.path.join(data_path, annotation_path, 'qptiff_rois.geojson')

#     # Perform registration
#     registrar = registration.Valis(src_dir = slide_src_dir, dst_dir = results_dst_dir,
#                                         reference_img_f = target_img_f, align_to_reference=True)

#     rigid_registrar, non_rigid_registrar, error_df = registrar.register()

#     pdb.set_trace()

#     # Transfer annotation from image associated with annotation_img_f and image associated with target_img_f
#     annotation_source_slide = registrar.get_slide(annotation_img_f)
#     target_slide = registrar.get_slide(target_img_f)

#     warped_geojson_from_to = annotation_source_slide.warp_geojson_from_to(annotation_geojson_f, target_slide)
#     warped_geojson = annotation_source_slide.warp_geojson(annotation_geojson_f)

#     # Save annotation as warped_geojson_annotation_f, which can be dragged and dropped into QuPath
#     with open(warped_geojson_annotation_f, 'w') as f:
#         json.dump(warped_geojson, f)

#     registration.kill_jvm()



    # slides = os.listdir(os.path.join(data_path,"images"))
    # for slide in slides:
    #     print(slide)
    #     image_path = f'images/{slide}'
    #     annotation_path = f'annotations/{slide}'

    #     slide_src_dir = os.path.join(data_path, image_path)
    #     results_dst_dir = os.path.join(slide_src_dir, 'slide_registration')
    #     #os.makedirs(results_dst_dir, exist_ok=True)
        
    #     svs_file = [img for img in os.listdir(slide_src_dir) if ".svs" in img][0]
    #     annotation_img_f = os.path.join(slide_src_dir, svs_file)
    #     target_img_f = os.path.join(slide_src_dir, f'{slide}.qptiff') 
        
    #     #os.makedirs(os.path.join(data_path, annotation_path), exist_ok=True)
    #     annotation_geojson_f = os.path.join(data_path, annotation_path, 'svs_rois.geojson')
    #     warped_geojson_annotation_f = os.path.join(data_path, annotation_path, 'qptiff_rois.geojson')

    #     # Perform registration
    #     registrar = registration.Valis(src_dir = slide_src_dir, dst_dir = results_dst_dir,
    #                                     reference_img_f = target_img_f, align_to_reference=True)

    #     rigid_registrar, non_rigid_registrar, error_df = registrar.register()

    #     # Transfer annotation from image associated with annotation_img_f and image associated with target_img_f
    #     annotation_source_slide = registrar.get_slide(annotation_img_f)
    #     target_slide = registrar.get_slide(target_img_f)

    #     warped_geojson_from_to = annotation_source_slide.warp_geojson_from_to(annotation_geojson_f, target_slide)
    #     warped_geojson = annotation_source_slide.warp_geojson(annotation_geojson_f)

    #     # Save annotation as warped_geojson_annotation_f, which can be dragged and dropped into QuPath
    #     with open(warped_geojson_annotation_f, 'w') as f:
    #         json.dump(warped_geojson, f)

    #     registration.kill_jvm()