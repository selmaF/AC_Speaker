from jakobsfuncs.table_transforms import *
from jakobsfuncs.util_functions import *


def check_angewinkelt(data):

    #falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data=nose_as_origin(data)

    #get elbow angles
    right_elbow_angle = get_angle(data,'rightElbow','rightWrist','rightShoulder')
    left_elbow_angle = get_angle(data,'leftElbow','leftWrist','leftShoulder')

    #für beträge der x-koordinaten gilt: hip<wrist
    subcond_0 = np.abs(data[data['part_names']=='rightHip']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='rightWrist']['x'].reset_index(drop=True))

    #für beträge der x-koordinaten gilt: wrist<elbow
    subcond_1 = np.abs(data[data['part_names']=='rightWrist']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='rightElbow']['x'].reset_index(drop=True))

    #für beträge der x-koordinaten gilt: hip<wrist
    subcond_2 = np.abs(data[data['part_names']=='leftHip']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='leftWrist']['x'].reset_index(drop=True))

    #für beträge der x-koordinaten gilt: wrist<elbow
    subcond_3 = np.abs(data[data['part_names']=='leftWrist']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='leftElbow']['x'].reset_index(drop=True))

    #winkel sind in best. bereich
    subcond_4 = (right_elbow_angle<125) & (right_elbow_angle>95)
    subcond_4 = subcond_4['angle']

    #winkel sind in best. bereich
    subcond_5 = (left_elbow_angle<125) & (left_elbow_angle>95)
    subcond_5 = subcond_5['angle']

    #für beträge der x-koordinaten gilt: hip<wrist<elbow
    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5
    res = res.rename_axis("angewinkelt")

    return res


def check_verschränkt(data):
    "return type needs to be list for consecutive functions to work"

    #falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data=nose_as_origin(data)

    #get elbow angles
    right_elbow_angle = get_angle(data,'rightElbow','rightWrist','rightShoulder')
    left_elbow_angle = get_angle(data,'leftElbow','leftWrist','leftShoulder')
    
    left_shoulder_angle = get_angle(data,'leftShoulder','leftElbow','leftHip')
    right_shoulder_angle = get_angle(data,'rightShoulder','rightElbow','rightHip')

    #höhenunterschied rightelbow und rightwrist kleiner als 50
    subcond_0 = np.abs((data[data['part_names']=='rightElbow']['y'].reset_index(drop=True))-(data[data['part_names']=='rightWrist']['y'].reset_index(drop=True)))<50
    
    #höhenunterschied rightelbow und rightwrist kleiner als 50
    subcond_1 = np.abs((data[data['part_names']=='leftElbow']['y'].reset_index(drop=True))-(data[data['part_names']=='leftWrist']['y'].reset_index(drop=True)))<50

    #rightwrist näher an leftelbow als an rightelbow
    subcond_2 = np.abs((data[data['part_names']=='rightElbow']['x'].reset_index(drop=True))-(data[data['part_names']=='rightWrist']['x'].reset_index(drop=True)))>np.abs((data[data['part_names']=='rightWrist']['x'].reset_index(drop=True))-(data[data['part_names']=='leftElbow']['x'].reset_index(drop=True)))

    #so wie sc2 nur für andere seite
    subcond_3 = np.abs((data[data['part_names']=='leftElbow']['x'].reset_index(drop=True))-(data[data['part_names']=='leftWrist']['x'].reset_index(drop=True)))>np.abs((data[data['part_names']=='leftWrist']['x'].reset_index(drop=True))-(data[data['part_names']=='rightElbow']['x'].reset_index(drop=True)))

    #spitze winkel im ellbogen
    subcond_4 = (right_elbow_angle<100) 
    subcond_4 = subcond_4['angle']

    #winkel sind in best. bereich
    subcond_5 = (left_elbow_angle<100) 
    subcond_5 = subcond_5['angle']
    
    #spitze winkel an der schulter
    subcond_6 = (left_shoulder_angle<35) 
    subcond_6 = subcond_6['angle']
    
    #winkel sind in best. bereich
    subcond_7 = (right_shoulder_angle<35) 
    subcond_7 = subcond_7['angle']

    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5 & subcond_6 & subcond_7
    res = res.rename_axis("verschränkt")
    
    return res


def check_handgelenkgriff(data):
    "return type needs to be list for consecutive functions to work"

    #falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data=nose_as_origin(data)

    #get elbow angles
    right_elbow_angle = get_angle(data,'rightElbow','rightWrist','rightShoulder')
    left_elbow_angle = get_angle(data,'leftElbow','leftWrist','leftShoulder')
    
    left_shoulder_angle = get_angle(data,'leftShoulder','leftElbow','leftHip')
    right_shoulder_angle = get_angle(data,'rightShoulder','rightElbow','rightHip')

    #höhenunterschied elbows kleiner als 30
    subcond_0 = np.abs((data[data['part_names']=='rightElbow']['y'].reset_index(drop=True))-(data[data['part_names']=='leftElbow']['y'].reset_index(drop=True)))<30
    
    #höhenunterschied wrists kleiner als 50
    subcond_1 = np.abs((data[data['part_names']=='leftWrist']['y'].reset_index(drop=True))-(data[data['part_names']=='leftWrist']['y'].reset_index(drop=True)))<50

    #für beträge der x-koordinaten gilt: wrist<Hip
    subcond_2 = np.abs(data[data['part_names']=='rightWrist']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='rightHip']['x'].reset_index(drop=True))

    #für beträge der x-koordinaten gilt: wrist<Hip
    subcond_3 = np.abs(data[data['part_names']=='leftWrist']['x'].reset_index(drop=True))<np.abs(data[data['part_names']=='leftHip']['x'].reset_index(drop=True))
    
    #stumpfe winkel im ellbogen
    subcond_4 = (right_elbow_angle>100) 
    subcond_4 = subcond_4['angle']

    #winkel sind in best. bereich
    subcond_5 = (left_elbow_angle>100) 
    subcond_5 = subcond_5['angle']
    
    #winkel sind in best. bereich
    subcond_6 = (left_shoulder_angle<35) 
    subcond_6 = subcond_6['angle']
    
    #winkel sind in best. bereich
    subcond_7 = (right_shoulder_angle<35) 
    subcond_7 = subcond_7['angle']

    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5 & subcond_6 & subcond_7
    res = res.rename_axis("handgelenke hängend umgriffen")
    
    return res