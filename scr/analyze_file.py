import os
import shutil
import subprocess

from PyQt5 import QtWidgets
from pydub import AudioSegment

import analyzer as a


def open_and_analyse_file():
    """
    Open file and analyze whole file plus sections
    :return:
    """
    name, path_to_files = open_file()
    results = analyze_whole_and_sections(name, path_to_files)
    return results, name


def open_file():
    """
    Choose file to analyze
    :return: file name and file path
    """
    path = QtWidgets.QFileDialog.getOpenFileName(directory="../data/audioFiles")
    file = path[0].split("/")[-1]
    name = file.split(".")[0]
    file_extension = file.split(".")[1]
    # todo verbinde audio und video-analyse
    if file_extension == "wav":
        # do audio analysis
        pass
    elif file_extension == "avi" or file_extension == "mp4":
        # exctract audio from video
        extract_audio_file(path[0])
    else:
        print("Format nicht analysierbar")
    path_to_files = path[0].split("/" + name)[0]
    return name, path_to_files


def split_and_save_audio_file(audio_file, audio_files_path, section_folder, last_second, section_size=15):
    speech = AudioSegment.from_wav(audio_files_path + "/" + audio_file + ".wav")
    number_section = 0
    # todo slice bei einer stillen Pause
    for number_section, section in enumerate(range(0, last_second, section_size)):
        section_speech = []
        section_start = section*1000
        section_end = (section+section_size)*1000-1
        if section_end > (last_second - 7)*1000:
            section_end = last_second*1000
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
    first_audio = "{}_audio".format(video_file)

    command = "ffmpeg -i " + video_file + " -ab 160k -ac 2 -ar 44100 -vn {}.wav".format(first_audio)
    subprocess.call(command, shell=True)
    return str(video_file + "_audio.wav")


def analyze_whole_and_sections(audio_file_name, audio_files_path):

    results_path = "../data/results"

    # analyze whole File
    analyzer = a.AudioAnalyzer(audio_file_name, audio_files_path)
    analyzer.analyzeWavFile()
    analyzer.analyze_recognizer()

    try:
        analyzer.saveResults(results_path)
        data_whole = analyzer.getResults()
    except ImportError:
        print("die Ergebnisse der Analyse konnten nicht abgerufen werden")

    # save_as_gold = input("\n Wollen Sie die Werte als Goldstandard speichern? Geben Sie ein j wenn ja " + "\n")
    # if save_as_gold == "j":
    #    analyzer.setStandard("data")

    # split sections and save to data/audioFiles/sections:
    # 1. delete old sections
    section_folder = audio_files_path + "/sections"
    try:
        os.mkdir(section_folder, mode=0o777)
    except FileExistsError:
        print("Old sections will be deleted")
        delete_folder_content(section_folder)
    # 2. save new sections
    number_of_sections = split_and_save_audio_file(audio_file_name, audio_files_path, section_folder,
                                                   data_whole["length_in_sec"])
    sections_results = []
    for i in range(number_of_sections):
        analyzer_section = a.AudioAnalyzer(audio_file_name + "_section" + str(i + 1), section_folder)
        analyzer_section.analyzeWavFile()
        sections_results.append(analyzer_section.getResults())
    return data_whole, sections_results


def delete_folder_content(path_to_folder):

    for filename in os.listdir(path_to_folder):
        file_path = os.path.join(path_to_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
