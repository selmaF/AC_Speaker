import parselmouth
from parselmouth.praat import run_file
import numpy as np
import os
import scipy.io.wavfile as wav
import math
import sys
import subprocess
from pydub import AudioSegment

import statistics
import recognizer


class AudioAnalyzer:

    def __init__(self, name, audio_files_path):
        self.name = name
        self.audio_file = name + ".wav"
        self.grid_file = name + ".TextGrid"
        self.audio_files_path = audio_files_path
        self.analyzed_values = {}
        self.analysis_done = False
        self.path_to_model = "model"

    def setStandard(self):
        # write data in txt-file
        if self.analysis_done:
            f = open('standard.txt', 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))
            pass

        else:
            print("noch keine Werte analysiert")
        return

    def getResults(self):
        if self.analysis_done:
            return self.analyzed_values
        else:
            print("Noch keine Analyseergebnisse vorhanden")
            raise ImportError

    def saveResults(self, path):
        if self.analysis_done:
            f = open(path + "/" + self.name + ".txt", 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))
        else:
            print("noch keine Werte analysiert, daher gibt es keine Werte zu speichern")
        return

    def printResults(self):
        if self.analysis_done:
            length = str(self.analyzed_values["length_in_sec"])
            pauses = str(self.analyzed_values["pauses"])
            mean_pauses = self.analyzed_values["mean_of_pauses"]
            print("\n")
            print(self.name)
            print("Die durchschnittliche Lautstärke beträgt %.2f dB" % self.analyzed_values["mean_intensity"])
            print("Bei einer Gesamtlänge von " + length + " Sekunden wurden " + pauses + " Pausen mit einer durchschnittlichen Länge von %.2f sec gemacht" % mean_pauses)
            print("Die durchschnittlich gesprochenen Silben pro Sekunde betragen " + str(self.analyzed_values["rate_of_speech"]))
            print("Das Verhältnis von geprochener Zeit zu der Gesamtzeit ist " + str(self.analyzed_values["balance"]))
            print("Die semantische Analyse ergab:  " + self.analyzed_values["mood"])
            print("Filler rate: " + str(self.analyzed_values["filler_rate"]))
            print("meist gebrauchte Füllwörter: " + str(self.analyzed_values["most_used_fillers"]))
            print("Anzahl von gefüllten Pausen: " + str(self.analyzed_values["filled_pauses"]))
        else:
            print("noch keine Werte analysiert")

    def runMyspsolutionPraatFile(self):
        # added from myspsolution.py
        sound = self.audio_files_path + "/" + self.audio_file
        sourcerun = "myspsolution.praat"
        path = self.audio_files_path + "/"

        return run_file(sourcerun, -20, 2, 0.3, "yes", sound, path, 80, 400, 0.01, capture_output=True)

    def analyzeWavFile(self):
        try:
            object = self.runMyspsolutionPraatFile()
            self.analyzed_values["length_in_sec"] = self.analyze_length()
            self.analyzed_values["mean_intensity"] = self.analyze_intensity()
            self.analyzed_values["pauses"] = self.analyze_num_pauses(object)
            self.analyzed_values["mean_of_pauses"] = self.compute_pause_length(self.audio_files_path + "/" + self.grid_file)
            self.analyzed_values["rate_of_speech"] = self.analyze_rate_of_speech(object)
            self.analyzed_values["balance"] = self.analyze_balance(object)
            self.analyzed_values["mood"] = self.analyze_mood(object)


            self.analysis_done = True
        except:
            print("couldn't read file")

    def analyze_recognizer(self):
        path_to_rec_text = recognizer.recognize_speech(self.audio_files_path + "/" + self.audio_file, self.path_to_model)
        words, end_timestamps, start_timestamps = recognizer.read_file(path_to_rec_text)
        timestamps = recognizer.detect_filled_pauses(end_timestamps, start_timestamps)
        self.analyze_filled_pauses(self.audio_files_path + "/" + self.audio_file, timestamps)
        filler_rate, most_used_fillers = recognizer.count_fillers("Fuellwoerter.txt", words)
        self.analyzed_values["filler_rate"] = filler_rate
        self.analyzed_values["most_used_fillers"] = most_used_fillers

    def analyze_length(self):
        # length of the .wav file nach https://stackoverflow.com/questions/40651891/get-length-of-wav-file-in-samples-with-python
        sound = self.audio_files_path + "/" + self.audio_file
        if os.path.isfile(sound):
            (source_rate, source_sig) = wav.read(sound)
            duration_seconds = len(source_sig) / float(source_rate)
            return math.ceil(duration_seconds)
        else:
            print("Couldn't find path to file")

    def analyze_intensity(self):
        # todo nicht allgemeine Lautstärke analysieren, sondern nur die in der gesprochenen Zeit
        # nehme abschnitte sounding aus TextGrid und analysiere Lautstärke und mean
        snd = parselmouth.Sound(self.audio_files_path + "/" + self.audio_file)
        intensity = snd.to_intensity(minimum_pitch=0.2)
        intensity_points = intensity.values.T
        spoken_intensity = intensity_points[intensity_points > 25]
        mean = np.mean(spoken_intensity)
        return mean

    def analyze_filled_pauses(self, sound, timestamps):
        snd = parselmouth.Sound(sound)
        pauses_number = 0
        for timestamp in timestamps:
            snd_part = snd.extract_part(from_time=timestamp[0], to_time=timestamp[1])
            intensity = snd_part.to_intensity()
            intensity_points = intensity.values.T
            spoken_intensity = intensity_points[intensity_points > 25]
            mean = np.mean(spoken_intensity)
            if mean > 50:
                pauses_number += 1
        self.analyzed_values["filled_pauses"] = pauses_number

    @staticmethod
    def analyze_num_pauses(parsel_object):
        # mysp.mysppaus(p,c)
        # count number of pauses
        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = int(z2[1])  # will be the integer number 10
        return z3

    @staticmethod
    def compute_pause_length(path_to_textGrid):
        pauses_intervall = []
        length_of_pause = []
        with open(path_to_textGrid) as textGrid:
            lines = textGrid.readlines()
            for i, line in enumerate(lines):
                words = line.split()
                if "\"silent\"" in words:
                    pauses_intervall.append(
                        (lines[i - 2].split()[-1], lines[i - 1].split()[-1]))  # append beginning and end of the pause
                    length_of_pause.append(
                        float(lines[i - 1].split()[-1]) - float(lines[i - 2].split()[-1]))  # append length of the pause

        mean_of_pauses = statistics.mean(length_of_pause)
        return mean_of_pauses

    @staticmethod
    def analyze_rate_of_speech(parsel_object):
        # mysp.myspsr(p, c)

        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = int(z2[2])  # will be the integer number 10
        # print("rate_of_speech=", z3, "# syllables/sec original duration")
        return z3

    @staticmethod
    def analyze_balance(parsel_object):
        # mysp.myspbala(p,c)

        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z4 = float(z2[6])  # will be the floating point number 8.3
        return z4

    @staticmethod
    def analyze_mood(parsel_object):
        # mysp.myspgend(p,c)

        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = float(z2[8])  # will be the integer number 10
        z4 = float(z2[7])  # will be the floating point number 8.3

        if 97 < z4 <= 114:
            return "showing no emotion"
        elif 114 < z4 <= 135:
            return "reading"
        elif 135 < z4 <= 163:
            return "speaking passionately"
        elif 163 < z4 <= 197:
            return "showing no emotion"
        elif 197 < z4 <= 226:
            return "reading"
        elif 226 < z4 <= 245:
            return "speaking passionately"
        else:
            print("Voice not recognized")
            return "Voice not recognized"

def split_and_save_audio_file(audio_file, audio_files_path, section_folder, last_second):
    speech = AudioSegment.from_wav(audio_files_path + "/" + audio_file + ".wav")
    section_size = 15 # todo wo kann man diesen Parameter einstellen? In der GUI?
    for number_section, section in enumerate(range(0, last_second, section_size)):
        section_speech = []
        section_start = section*1000
        section_end = (section+section_size)*1000-1
        section_speech = speech[section_start:section_end]
        section_speech.export((section_folder + "/" + audio_file + "_section" + str(number_section+1) + ".wav"),
                              format="wav", bitrate="44.1k")
    return number_section+1

def extract_audio_file(video_file_path, video_file_name):
    # read video file, create audio file stub
    video_file = video_file_path + "/"+ video_file_name + ".mp4"
    first_audio = "{}_audio".format(video_file)

    # extract audio track and save it with the marker "_audio"
    command = "ffmpeg -i " + video_file + " -ab 160k -ac 2 -ar 44100 -vn {}.wav".format(first_audio)
    subprocess.call(command, shell=True)
    return str(video_file + "_audio.wav")

def analyze_whole_and_sections(audio_file_name, audio_files_path):

    #audio_file_name = "SusanDavid_2017W_kurz"  # TODO: show error message (Daria)
    #audio_files_path = "data/audioFiles"
    results_path = "data/results"

    # analyze whole File
    analyzer = AudioAnalyzer(audio_file_name, audio_files_path)
    analyzer.analyzeWavFile()

    try:
        # analyzer.printResults()
        analyzer.saveResults(results_path)
        data_whole = analyzer.getResults()
    except ImportError:
        print("Analyse noch nicht durchgeführt")

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
        analyzer_section = AudioAnalyzer(audio_file_name + "_section" + str(i + 1), section_folder)
        analyzer_section.analyzeWavFile()
        sections_results.append(analyzer_section.getResults())
        # find_frames(audio_file_name + "_section" + str(i+1), section_folder, data_whole)
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