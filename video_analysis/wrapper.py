import tensorflow as tf
import cv2
import time
import argparse
import pandas as pd

import posenet
from jakobsfuncs import table_transforms
from jakobsfuncs import pose_checks
from jakobsfuncs import util_functions

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, default=None, help="Optionally use a video file instead of a live camera")
args = parser.parse_args()

with tf.Session() as sess:
        model_cfg, model_outputs = posenet.load_model(101, sess)
        output_stride = model_cfg['output_stride']

        try:
            cap = cv2.VideoCapture(args.file)
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
                data.to_csv('kp_coords/{}.csv'.format(args.file),index=False)
                break
        
        print('Keypoints identified for each frame')
                
        #new_coords=table_transforms.nose_as_origin(data)
        arme_angewinkelt=pose_checks.check_angewinkelt(data)
        arme_verschränkt=pose_checks.check_verschränkt(data)
        handgelenke_umfasst=pose_checks.check_handgelenkgriff(data)
        
        
        bool_array_for_plot=pd.concat([arme_angewinkelt,arme_verschränkt,handgelenke_umfasst],axis=1).to_numpy().transpose()
        labels_for_plot=["Arme angewinkelt", "Arme verschränkt", "Handgelenke umfasst"]
    
    
        blocks=util_functions.get_blocks(arme_angewinkelt)
        
        frame_to_second=data[['frame_count','timestamp']]
        avg_fps=frame_to_second.iloc[-1][0]/frame_to_second.iloc[-1][1]
        prev=-1
        for element in blocks:
            second=frame_to_second[frame_to_second['frame_count']== element[2]].iloc[0][1]
            if (prev!=second):
                print("Beidseitig in die Hüften gestützte Arme ab Sekunde ", second, ". Dauer: Etwa", int(element[1]/avg_fps)+1, "Sekunden.")
            prev=second        
        
        
