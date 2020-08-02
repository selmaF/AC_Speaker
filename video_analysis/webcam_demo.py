import tensorflow as tf
import cv2
import time
import argparse
import pandas as pd
import math
import posenet

from jakobsfuncs import table_transforms
from jakobsfuncs import pose_checks
from jakobsfuncs import util_functions

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=int, default=101)
parser.add_argument('--cam_id', type=int, default=0)
parser.add_argument('--cam_width', type=int, default=1280)
parser.add_argument('--cam_height', type=int, default=720)
parser.add_argument('--scale_factor', type=float, default=0.7125)
parser.add_argument('--file', type=str, default=None, help="Optionally use a video file instead of a live camera")
args = parser.parse_args()


def main():
    with tf.Session() as sess:
        model_cfg, model_outputs = posenet.load_model(args.model, sess)
        output_stride = model_cfg['output_stride']

        if args.file is not None:
            cap = cv2.VideoCapture(args.file)
        else:
            cap = cv2.VideoCapture(args.cam_id)
        cap.set(3, args.cam_width)
        cap.set(4, args.cam_height)

        start = time.time()
        frame_count = 0
        dfs=[]
        txt1="thisisaplaceholder"
        txt2=""
        txt3=""
        ileft=0
        iright=0
        
        #fixed_pose_id limits the readout of coords to one person
        fixed_pose_id=0
        
        while True:
            input_image, display_image, output_scale = posenet.read_cap(
                cap, scale_factor=args.scale_factor, output_stride=output_stride)

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
            
            
            
            
            #dataFrame creat
            _df = pd.DataFrame(keypoint_scores[fixed_pose_id], columns=['keypoint_score'])
            _df['y'] = keypoint_coords[fixed_pose_id, :, 0]
            _df['x'] = keypoint_coords[fixed_pose_id, :, 1]
            _df['pose_score'] = pose_scores[fixed_pose_id]
            _df['frame_count']=frame_count
            _df['part_names'] = posenet.PART_NAMES
            _df = _df[['frame_count','pose_score', 'part_names', 'keypoint_score', 'x', 'y']]
            dfs.append(_df)
            
            
            #rename coords
            #add [0] for y coord and [1] for x coord
            left_wrist_coords=keypoint_coords[0][9]
            right_wrist_coords=keypoint_coords[0][10]
            left_hip_coords=keypoint_coords[0][11]
            right_hip_coords=keypoint_coords[0][12]
            left_shoulder_coords=keypoint_coords[0][5]
            right_shoulder_coords=keypoint_coords[0][6]
            left_elbow_coords=keypoint_coords[0][7]
            right_elbow_coords=keypoint_coords[0][8]
            
            #elbow angle
            e2wx=left_wrist_coords[1]-left_elbow_coords[1]
            e2wy=left_wrist_coords[0]-left_elbow_coords[0]
            e2sx=left_shoulder_coords[1]-left_elbow_coords[1]
            e2sy=left_shoulder_coords[0]-left_elbow_coords[0]
            skalarprod=e2wx*e2sx+e2wy*e2sy
            e2w_len=math.sqrt(e2wx**2+e2wy**2)
            e2s_len=math.sqrt(e2sx**2+e2sy**2)
            
            #shoulder
            #e2wx=left_elbow_coords[1]-left_shoulder_coords[1]
            #e2wy=left_elbow_coords[0]-left_shoulder_coords[0]
            #e2sx=left_hip_coords[1]-left_shoulder_coords[1]
            #e2sy=left_hip_coords[0]-left_shoulder_coords[0]
            #skalarprod=e2wx*e2sx+e2wy*e2sy
            #e2w_len=math.sqrt(e2wx**2+e2wy**2)
            #e2s_len=math.sqrt(e2sx**2+e2sy**2)
            
            try:
                winkel=math.degrees(math.acos(skalarprod/abs(e2w_len*e2s_len)))
            except:
                winkel=0
                
            
            
            # TODO this isn't particularly fast, use GL for drawing and display someday...
            overlay_image = posenet.draw_skel_and_kp(
                display_image, pose_scores, keypoint_scores, keypoint_coords,
                min_pose_score=0.15, min_part_score=0.1)
            
            #left or right
            leftEarDist=abs(keypoint_coords[0][0][1]-keypoint_coords[0][4][1])
            rightEarDist=abs(keypoint_coords[0][0][1]-keypoint_coords[0][5][1])
            if (rightEarDist>leftEarDist or (keypoint_scores[0][4]<0.5 and keypoint_scores[0][5]>0.5)):
                txt1="You are looking right."
            elif(rightEarDist<leftEarDist or (keypoint_scores[0][5]<0.5 and keypoint_scores[0][4]>0.5)):
                txt1="You are looking left."
                
            #is the wrist hanging limply under the elbow (lässt die person ihre arme hängen?)
            if ((left_elbow_coords[1]+20)>left_wrist_coords[1]>(left_elbow_coords[1]-20)):
                ileft += 1
            else:
                ileft = 0
                txt2 = ""
                
            if ((right_elbow_coords[1]+20)>right_wrist_coords[1]>(right_elbow_coords[1]-20)):
                iright += 1
            else:
                iright = 0
                txt3 = ""
            

            # if 5 frames have elapsed with the person not moving their wrists out from underneath their elbows, these two texts are displayed.
            # for higher frame rates, the number 5 has to be increased, otherwise the texts will be displayed even if the person is moving their
            # arms
            if (ileft == 5):
                txt2=" Move your left arm."
            if (iright == 5):
                txt3=" Move your right arm."
                                            
            # text overlay
            font                   = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (10,500)
            fontScale              = 1
            fontColor              = (0,255,255)
            lineType               = 2    
            cv2.putText(overlay_image,txt1+txt2+txt3+str(winkel), 
                bottomLeftCornerOfText, 
                font, 
                fontScale,
                fontColor,
                lineType)
            
            #line overlay for wrist height
            if (int(0.8*left_hip_coords[0])>left_wrist_coords[0]>left_shoulder_coords[0]):
                linecolor=(0, 200, 0)
            else:
                linecolor=(0, 0, 200)
            #cv2.line(overlay_image,(0,int(0.8*right_hip_coords[0])),(1280,int(0.8*left_hip_coords[0])),linecolor,9)
            #cv2.line(overlay_image,(0,int(right_shoulder_coords[0])),(1280,int(left_shoulder_coords[0])),linecolor,9)
                
            cv2.imshow('posenet', overlay_image)
            frame_count += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        data = pd.concat(dfs)
        timestring=time.ctime().replace(" ","_")
        data.to_csv('kp_coords/{}.csv'.format(timestring),index=False)
        
        print('Average FPS: ', frame_count / (time.time() - start))
        print('Video length:', (time.time() - start))
        

if __name__ == "__main__":
    main()