import os
import shutil
import subprocess

from PyQt5 import QtWidgets
from pydub import AudioSegment

import analyzer as a
import recognizer
import wrapper


def analyze_recorded(section_size, name):
    name_video = name + ".avi"
    path_to_files = "../data/audioFiles/recording"

    results = analyze_whole_and_sections(name, path_to_files, section_size, False)
    array_for_plot, labels_for_plot, df_for_movement_plot = wrapper.analyzeVideo(path_to_files + '/' + name_video)

    results_video = {}
    results_video["array_for_poses"] = array_for_plot
    results_video["labels_for_poses"] = labels_for_plot
    results_video["df_for_movement"] = df_for_movement_plot

    return results, results_video, name, path_to_files

def open_and_analyse_file(section_size, only_whole=False):
    """
    Open file and analyze whole file plus sections
    :return:
    """
    name, path_to_files, is_video_file, file_extension = open_file()
    results = analyze_whole_and_sections(name, path_to_files, section_size, only_whole)

    results_video = {}
    if is_video_file:
        filename = path_to_files + "/" + name.split("_audio")[0] + "." + file_extension

        array_for_plot, labels_for_plot, df_for_movement_plot = wrapper.analyzeVideo(filename)


        results_video["array_for_poses"] = array_for_plot
        results_video["labels_for_poses"] = labels_for_plot
        results_video["df_for_movement"] = df_for_movement_plot

    return results, results_video, name, path_to_files


def open_file():
    """
    Choose file to analyze
    :return: file name and file path
    """
    path = QtWidgets.QFileDialog.getOpenFileName(directory="../data/audioFiles")
    file = path[0].split("/")[-1]
    name = file.split(".")[0]
    file_extension = file.split(".")[1]
    path_to_files = path[0].split("/" + name)[0]
    is_video_file = False
    if file_extension == "wav":
        # do audio analysis
        is_video_file = False
        pass
    elif file_extension == "avi" or file_extension == "mp4" or file_extension == "mov":
        # exctract audio from video
        name = extract_audio_file(path[0])
        is_video_file = True
    else:
        print("Format nicht analysierbar")

    return name, path_to_files, is_video_file, file_extension


def split_and_save_audio_file(audio_file, audio_files_path, section_folder, last_second, section_size=15):
    speech = AudioSegment.from_wav(audio_files_path + "/" + audio_file + ".wav")
    # convert stereo to mono
    if speech.channels == 2:
        speech = convert_stereo_to_mono(audio_files_path + "/" + audio_file + ".wav")[:-4]
        audio_file = audio_file + "_mono"

    number_section = 0
    # nice to have: slice at silent pause
    min_size_section = 10 * 1000
    for number_section, section in enumerate(range(0, last_second, section_size)):
        section_speech = []
        section_start = section*1000
        section_end = (section+section_size)*1000-1
        if (last_second*1000) < (section_end + min_size_section):
            end = last_second*1000
            section_speech = speech[section_start:end]
            section_speech.export((section_folder + "/" + audio_file + "_section" + str(number_section + 1) + ".wav"),
                                  format="wav", bitrate="44.1k")
            return number_section+1, audio_file

        section_speech = speech[section_start:section_end]

        section_speech.export((section_folder + "/" + audio_file + "_section" + str(number_section+1) + ".wav"),
                              format="wav", bitrate="44.1k")
    return number_section+1


def extract_audio_file(video_file):
    """
    Read video file, create audio file stub
    :param video_file: path to video file
    :return: extracted audio file
    """
    name = video_file.split('/')[-1].split('.')[0]
    audio_name = "{}_audio".format(name)
    path_audio = video_file.split('/' + name)[0]
    if not os.path.isfile(path_audio + '/' + audio_name + '.wav'):
        # FIXME: für Linux und Mac auskommentieren!
        command = "ffmpeg -i " + video_file + " -ab 160k -ac 2 -ar 44100 -vn {}.wav".format(path_audio + '/' + audio_name)
        subprocess.call(command, shell=True)
    # for windows
    #    command = "D:\\download\\ffmpeg-20200730-134a48a-win64-static\\bin\\ffmpeg -i " + video_file + " -ab 160k -ac 2 -ar 44100 -vn {}.wav".format(path_audio + '/' + audio_name)
    #    subprocess.check_output(command, shell=True)
    return audio_name


def analyze_whole_and_sections(audio_file_name, audio_files_path, sections_size, only_whole):

    results_path = "../data/results"
    # analyze whole File
    analyzer = a.AudioAnalyzer(audio_file_name, audio_files_path)
    analyzer.analyzeWavFile()

    try:
        analyzer.saveResults(results_path)
        data_whole = analyzer.getResults()
    except ImportError:
        print("die Ergebnisse der Analyse konnten nicht abgerufen werden")
        return

    if only_whole:
        return data_whole
    # split sections and save to data/audioFiles/sections:
    # 1. delete old sections
    section_folder = audio_files_path + "/sections"
    try:
        os.mkdir(section_folder, mode=0o777)
    except FileExistsError:
        print("Old sections will be deleted")
        delete_folder_content(section_folder)

    # 2. save new sections
    number_of_sections, audio_file_name = split_and_save_audio_file(audio_file_name, audio_files_path, section_folder,
                                                   data_whole["length_in_sec"], section_size=sections_size)
    # analyze sections
    sections_results = []
    rec_words = []
    filled_pauses = 0
    for i in range(number_of_sections):
        analyzer_section = a.AudioAnalyzer(audio_file_name + "_section" + str(i + 1), section_folder)
        analyzer_section.analyzeWavFile()
        words = analyzer.analyze_recognizer()
        for word in words:
            rec_words.append(word)
        filled_pauses = analyzer.analyzed_values["filled_pauses"] + filled_pauses
        sections_results.append(analyzer_section.getResults())
    filler_rate, most_used_fillers = recognizer.count_fillers("Fuellwoerter.txt", rec_words)
    data_whole["filled_pauses"] = filled_pauses
    data_whole["most_used_fillers"] = most_used_fillers
    data_whole["filler_rate"] = filler_rate
    return data_whole, sections_results


def delete_folder_content(path_to_folder):
    """
    Delete folder with sections
    :param path_to_folder: path to folder containing sections
    :return: None
    """

    for filename in os.listdir(path_to_folder):
        file_path = os.path.join(path_to_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def get_results_from_text_file(nameTextFile="standard.txt"):
    results_path = "../data/results"
    f = open((results_path + '/' + nameTextFile), 'r')
    read_results = {"name": f.readline()}
    for line in f.readlines():
        key = line.split(',')[0]
        value = line.split(',')[1]
        read_results[key] = value
    print(read_results)
    return read_results


def convert_stereo_to_mono(audiofile):
    """
    Convert stereo to mono
    :param audiofile: path to audio file
    :return: mono sound
    """
    sound = AudioSegment.from_wav(audiofile)
    sound = sound.set_channels(1)
    name = str(audiofile[:-4]) + "_mono"
    sound.export(name + ".wav", format="wav")
    return sound
