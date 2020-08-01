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
        self.path_to_model = "../model"

    def setStandard(self):
        # write data in txt-file
        if self.analysis_done:
            f = open('standard.txt', 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))

        else:
            print("Noch keine Werte analysiert")

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
            print("Noch keine Werte analysiert, daher gibt es keine Werte zu speichern")

    def saveAsStandard(self, path):
        if self.analysis_done:
            f = open(path + "/" + "standard.txt", 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))
        else:
            print("Noch keine Werte analysiert, daher gibt es keine Werte als Standard zu speichern")

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
            print("Meist gebrauchte Füllwörter: " + str(self.analyzed_values["most_used_fillers"]))
            print("Anzahl von gefüllten Pausen: " + str(self.analyzed_values["filled_pauses"]))
        else:
            print("Keine Werte analysiert")

    def runMyspsolutionPraatFile(self):
        # added from myspsolution.py
        sound = self.audio_files_path + "/" + self.audio_file
        sourcerun = "myspsolution.praat"
        path = self.audio_files_path + "/"

        return run_file(sourcerun, -20, 2, 0.3, "yes", sound, path, 80, 400, 0.01, capture_output=True)

    def analyzeWavFile(self):
        try:
            print("Starte Analyse von " + self.name)
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
            print("analyzeWavFile hat nicht vollständig funktioniert")

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
        snd = parselmouth.Sound(self.audio_files_path + "/" + self.audio_file)
        intensity = snd.to_intensity(minimum_pitch=50)
        intensity_points = intensity.values.T
        mean_all = np.mean(intensity_points)
        spoken_intensity = intensity_points[intensity_points > (mean_all - 25)]
        mean = np.mean(spoken_intensity)
        return mean

    def analyze_filled_pauses(self, sound, timestamps):
        snd = parselmouth.Sound(sound)
        pauses_number = 0
        time_filled_pauses = []
        for timestamp in timestamps:
            minimum_pause_length = 0.2
            if (timestamp[1] - timestamp[0]) > minimum_pause_length:
                snd_part = snd.extract_part(from_time=timestamp[0], to_time=timestamp[1])
                intensity = snd_part.to_intensity(minimum_pitch=50)
                intensity_points = intensity.values.T
                mean = np.mean(intensity_points)
                if mean > 50:
                    pauses_number += 1
                    time_filled_pauses.append((timestamp[0],timestamp[1]))
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

        z1 = str(parsel_object[1])
        z2 = z1.strip().split()
        z3 = z2[2]
        # syllables/sec original duration
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
