from jakobsfuncs.table_transforms import *
from jakobsfuncs.util_functions import *


def check_angewinkelt(data):
    # falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data = nose_as_origin(data)

    # get elbow angles
    right_elbow_angle = get_angle(data, 'rightElbow', 'rightWrist', 'rightShoulder')
    left_elbow_angle = get_angle(data, 'leftElbow', 'leftWrist', 'leftShoulder')

    # für beträge der x-koordinaten gilt: hip<wrist
    subcond_0 = np.abs(data[data['part_names'] == 'rightHip']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True))

    # für beträge der x-koordinaten gilt: wrist<elbow
    subcond_1 = np.abs(data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'rightElbow']['x'].reset_index(drop=True))

    # für beträge der x-koordinaten gilt: hip<wrist
    subcond_2 = np.abs(data[data['part_names'] == 'leftHip']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True))

    # für beträge der x-koordinaten gilt: wrist<elbow
    subcond_3 = np.abs(data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'leftElbow']['x'].reset_index(drop=True))

    # winkel sind in best. bereich
    subcond_4 = (right_elbow_angle < 125) & (right_elbow_angle > 95)
    subcond_4 = subcond_4['angle']

    # winkel sind in best. bereich
    subcond_5 = (left_elbow_angle < 125) & (left_elbow_angle > 95)
    subcond_5 = subcond_5['angle']

    # für beträge der x-koordinaten gilt: hip<wrist<elbow
    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5
    res = res.rename_axis("angewinkelt")

    return res


def check_verschränkt(data):
    "return type needs to be list for consecutive functions to work"

    # falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data = nose_as_origin(data)

    # get elbow angles
    right_elbow_angle = get_angle(data, 'rightElbow', 'rightWrist', 'rightShoulder')
    left_elbow_angle = get_angle(data, 'leftElbow', 'leftWrist', 'leftShoulder')

    left_shoulder_angle = get_angle(data, 'leftShoulder', 'leftElbow', 'leftHip')
    right_shoulder_angle = get_angle(data, 'rightShoulder', 'rightElbow', 'rightHip')

    # höhenunterschied rightelbow und rightwrist kleiner als 50
    subcond_0 = np.abs((data[data['part_names'] == 'rightElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True))) < 50

    # höhenunterschied rightelbow und rightwrist kleiner als 50
    subcond_1 = np.abs((data[data['part_names'] == 'leftElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 50

    # rightwrist näher an leftelbow als an rightelbow
    subcond_2 = np.abs((data[data['part_names'] == 'rightElbow']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True))) > np.abs(
        (data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True)) - (
            data[data['part_names'] == 'leftElbow']['x'].reset_index(drop=True)))

    # so wie sc2 nur für andere seite
    subcond_3 = np.abs((data[data['part_names'] == 'leftElbow']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True))) > np.abs(
        (data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True)) - (
            data[data['part_names'] == 'rightElbow']['x'].reset_index(drop=True)))

    # spitze winkel im ellbogen
    subcond_4 = (right_elbow_angle < 100)
    subcond_4 = subcond_4['angle']

    # winkel sind in best. bereich
    subcond_5 = (left_elbow_angle < 100)
    subcond_5 = subcond_5['angle']

    # spitze winkel an der schulter
    subcond_6 = (left_shoulder_angle < 35)
    subcond_6 = subcond_6['angle']

    # winkel sind in best. bereich
    subcond_7 = (right_shoulder_angle < 35)
    subcond_7 = subcond_7['angle']

    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5 & subcond_6 & subcond_7
    res = res.rename_axis("verschränkt")

    return res


def check_handgelenkgriff(data):
    "return type needs to be list for consecutive functions to work"

    # falls data schon im nosecoords format, egal: nose_as_origin ist idempotent
    data = nose_as_origin(data)

    # get elbow angles
    right_elbow_angle = get_angle(data, 'rightElbow', 'rightWrist', 'rightShoulder')
    left_elbow_angle = get_angle(data, 'leftElbow', 'leftWrist', 'leftShoulder')

    left_shoulder_angle = get_angle(data, 'leftShoulder', 'leftElbow', 'leftHip')
    right_shoulder_angle = get_angle(data, 'rightShoulder', 'rightElbow', 'rightHip')

    # höhenunterschied elbows kleiner als 30
    subcond_0 = np.abs((data[data['part_names'] == 'rightElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftElbow']['y'].reset_index(drop=True))) < 30

    # höhenunterschied wrists kleiner als 50
    subcond_1 = np.abs((data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 50

    # für beträge der x-koordinaten gilt: wrist<Hip
    subcond_2 = np.abs(data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'rightHip']['x'].reset_index(drop=True))

    # für beträge der x-koordinaten gilt: wrist<Hip
    subcond_3 = np.abs(data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True)) < np.abs(
        data[data['part_names'] == 'leftHip']['x'].reset_index(drop=True))

    # stumpfe winkel im ellbogen
    subcond_4 = (right_elbow_angle > 100)
    subcond_4 = subcond_4['angle']

    # winkel sind in best. bereich
    subcond_5 = (left_elbow_angle > 100)
    subcond_5 = subcond_5['angle']

    # winkel sind in best. bereich
    subcond_6 = (left_shoulder_angle < 35)
    subcond_6 = subcond_6['angle']

    # winkel sind in best. bereich
    subcond_7 = (right_shoulder_angle < 35)
    subcond_7 = subcond_7['angle']

    res = subcond_0 & subcond_1 & subcond_2 & subcond_3 & subcond_4 & subcond_5 & subcond_6 & subcond_7
    res = res.rename_axis("handgelenke hängend umgriffen")

    return res


def check_einarmhaengt(data):
    right_elbow_angle = get_angle(data, 'rightElbow', 'rightWrist', 'rightShoulder')
    left_elbow_angle = get_angle(data, 'leftElbow', 'leftWrist', 'leftShoulder')

    # zusatz rg oder lg steht für rechts-gerade bzw links-gerade. d.h. bei rg umfasst die linke hand den rechten ellbogen

    # höhenunterschied leftelbow-rightwrist  kleiner als 40
    subcond_0rg = np.abs((data[data['part_names'] == 'leftElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True))) < 40

    # höhenunterschied rightelbow-leftwrist kleiner als 40
    subcond_0lg = np.abs((data[data['part_names'] == 'rightElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 40

    # rightwrist etwa auf höhe der hüfte
    subcond_1rg = np.abs((data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightHip']['y'].reset_index(drop=True))) < 50

    # leftwrist etwa auf höhe der hüfte
    subcond_1lg = np.abs((data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftHip']['y'].reset_index(drop=True))) < 50

    # leftwrist etwa auf höhe des leftelbow
    subcond_2rg = np.abs((data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftElbow']['y'].reset_index(drop=True))) < 30

    # rightwrist etwa auf höhe des rightelbow
    subcond_2lg = np.abs((data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightElbow']['y'].reset_index(drop=True))) < 30

    # rightwrist nahe an leftelbow (bzgl der xwerte)
    subcond_3lg = np.abs((data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftElbow']['x'].reset_index(drop=True))) < 40

    # leftwrist nahe an rightelbow (bzgl der xwerte)
    subcond_3rg = np.abs((data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightElbow']['x'].reset_index(drop=True))) < 40

    # stumpfe winkel im right ellbogen
    subcond_4rg = (right_elbow_angle > 100)
    subcond_4rg = subcond_4rg['angle']

    # stumpfe winkel im left ellbogen
    subcond_4lg = (left_elbow_angle > 100)
    subcond_4lg = subcond_4lg['angle']

    res = (subcond_0rg & subcond_1rg & subcond_2rg & subcond_3rg & subcond_4rg) | (
                subcond_0lg & subcond_1lg & subcond_2lg & subcond_3lg & subcond_4lg)
    res = res.rename_axis("ein arm hängt")

    return res


def check_armgestreckt(data):
    # right_elbow_angle = get_angle(data,'rightElbow','rightWrist','rightShoulder')
    # left_elbow_angle = get_angle(data,'leftElbow','leftWrist','leftShoulder')

    # zusatz rg oder lg steht für rechts-gestreckt oder linksgestreckt

    # höhenunterschied leftelbow-leftwrist  kleiner als 80
    subcond_0lg = np.abs((data[data['part_names'] == 'leftElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 80

    # höhenunterschied rightelbow-rightwrist kleiner als 80
    subcond_0rg = np.abs((data[data['part_names'] == 'rightElbow']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True))) < 80

    # höhenunterschied leftshoulder-leftwrist  kleiner als 30
    subcond_1lg = np.abs((data[data['part_names'] == 'leftShoulder']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 70

    # höhenunterschied rightshoulder-rightwrist kleiner als 30
    subcond_1rg = np.abs((data[data['part_names'] == 'rightShoulder']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True))) < 70

    # xunterschied leftelbow-leftwrist  kleiner als
    subcond_2lg = np.abs((data[data['part_names'] == 'leftElbow']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True))) < 70

    # xunterschied rightelbow-rightwrist kleiner als
    subcond_2rg = np.abs((data[data['part_names'] == 'rightElbow']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True))) < 70

    # xunterschied leftshoulder-leftwrist  kleiner als
    subcond_3lg = np.abs((data[data['part_names'] == 'leftShoulder']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True))) < 50

    # xunterschied rightshoulder-rightwrist kleiner als
    subcond_3rg = np.abs((data[data['part_names'] == 'rightShoulder']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True))) < 50

    res = (subcond_0rg & subcond_1rg & subcond_2rg & subcond_3rg) | (
                subcond_0lg & subcond_1lg & subcond_2lg & subcond_3lg)
    res = res.rename_axis("arm ausgestreckt")

    return res


def check_gesichtverdeckt(data):
    # höhenunterschied nose-leftwrist  kleiner als 130
    subcond_0lv = np.abs((data[data['part_names'] == 'nose']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['y'].reset_index(drop=True))) < 130

    # höhenunterschied nose-rightwrist kleiner als 130
    subcond_0rv = np.abs((data[data['part_names'] == 'nose']['y'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['y'].reset_index(drop=True))) < 130

    # xunterschied nose-leftwrist  kleiner als 60
    subcond_1lv = np.abs((data[data['part_names'] == 'nose']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'leftWrist']['x'].reset_index(drop=True))) < 80

    # xunterschied nose-rightwrist kleiner als 60
    subcond_1rv = np.abs((data[data['part_names'] == 'nose']['x'].reset_index(drop=True)) - (
        data[data['part_names'] == 'rightWrist']['x'].reset_index(drop=True))) < 80

    # konfidenz erkennung nase kleiner als 50 %
    subcond_3 = data[data['part_names'] == 'nose']['keypoint_score'].reset_index(drop=True) <= 0.9875

    # konfidenz erkennung rechtesauge kleiner als 50 %
    subcond_4 = data[data['part_names'] == 'rightEye']['keypoint_score'].reset_index(drop=True) <= 0.9875

    # konfidenz erkennung linkesauge kleiner als 50 %
    subcond_5 = data[data['part_names'] == 'leftEye']['keypoint_score'].reset_index(drop=True) <= 0.9875

    res = ((subcond_0rv & subcond_1rv) | (subcond_0lv & subcond_1lv)) & (subcond_3 | subcond_4 | subcond_5)
    res = res.rename_axis("gesicht verdeckt")

    return res
