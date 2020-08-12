import tensorflow as tf
import cv2
import time
import argparse
import pandas as pd

import posenet
from jakobsfuncs import table_transforms
from jakobsfuncs import pose_checks
from jakobsfuncs import util_functions

def analyzeVideo(filepath):
        
    with tf.Session() as sess:
            model_cfg, model_outputs = posenet.load_model(101, sess)
            output_stride = model_cfg['output_stride']

            try:
                cap = cv2.VideoCapture(filepath)
            except:
                print("File not found or none entered!")
                
            cap.set(3, 1280)
            cap.set(4, 720)

            start = time.time() 
            #vid_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            dfs=[]
        
            #fixed_pose_id limits the readout of coords to one person
            fixed_pose_id=0
            
            
            print('Keypoint analysis in progress')
            while True:
                # try/except hier weil tf.session abstürzt wenn video zuende
                try:
                    input_image, display_image, output_scale = posenet.read_cap(
                        cap, scale_factor=0.7125, output_stride=output_stride)

                    heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
                        model_outputs,
                        feed_dict={'image:0': input_image}
                    )

                    pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
                        heatmaps_result.squeeze(axis=0),
                        offsets_result.squeeze(axis=0),
                        displacement_fwd_result.squeeze(axis=0),
                        displacement_bwd_result.squeeze(axis=0),
                        output_stride=output_stride,
                        max_pose_detections=10,
                        min_pose_score=0.15)

                    keypoint_coords *= output_scale

                    _df = pd.DataFrame(keypoint_scores[fixed_pose_id], columns=['keypoint_score'])
                    _df['y'] = keypoint_coords[fixed_pose_id, :, 0]
                    _df['x'] = keypoint_coords[fixed_pose_id, :, 1]
                    _df['pose_score'] = pose_scores[fixed_pose_id]
                    _df['frame_count']=frame_count
                    _df['timestamp']=int(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
                    _df['part_names'] = posenet.PART_NAMES
                    _df = _df[['frame_count','pose_score', 'part_names', 'keypoint_score', 'x', 'y','timestamp']]
                    
                    frame_count += 1
                    dfs.append(_df)
                    
                except:
                    data = pd.concat(dfs)
                    #data.to_csv('kp_coords/{}.csv'.format(filepath),index=False)
                    break
            
            print('Keypoints identified for each frame')
            
            # create special dataframe containing information on movement
            data=table_transforms.nose_as_origin(data)
            df_prev=data.copy()
            df_prev['frame_count']=df_prev['frame_count']+1
            df_prev=df_prev.drop(['pose_score','keypoint_score'],axis=1)
            df_prev.rename(columns={"x": "x_dist_to_nose_in_prev_frame", "y": "y_dist_to_nose_in_prev_frame"},inplace=True)
            df_prev=data.merge(df_prev, on=['frame_count','part_names'])
            df_prev['x_movement']=df_prev['x']-df_prev['x_dist_to_nose_in_prev_frame']
            df_prev['y_movement']=df_prev['y']-df_prev['y_dist_to_nose_in_prev_frame']
            df_prev['movement_vector_length']=((df_prev['x_movement']**2)+(df_prev['y_movement']**2))**(1/2)
            
            
            
            #analysefunktionen für verschiedene posen
            #new_coords=table_transforms.nose_as_origin(data)
            arme_angewinkelt=pose_checks.check_angewinkelt(data)
            arme_verschränkt=pose_checks.check_verschränkt(data)
            handgelenke_umfasst=pose_checks.check_handgelenkgriff(data)
            ein_arm_haengt=pose_checks.check_einarmhaengt(data)
            arm_gestreckt=pose_checks.check_armgestreckt(data)
            gesicht_verdeckt=pose_checks.check_gesichtverdeckt(data)

            # diese arrays enthalten informationen, die in den plot funktionen der gui weiter verwendet werden
            bool_array_for_plot = pd.concat(
                [arme_angewinkelt, arme_verschränkt, handgelenke_umfasst, ein_arm_haengt, arm_gestreckt,
                 gesicht_verdeckt], axis=1).to_numpy().transpose()
            labels_for_plot = ["Arme \nangew.", "Arme \nversch.", "Handg. \numf.", "Arm \nhängt",
                               "Arm \nausge.", "Ges. \nverd."]

    return (bool_array_for_plot, labels_for_plot, df_prev)
       
