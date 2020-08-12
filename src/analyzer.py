import parselmouth
from parselmouth.praat import run_file
import numpy as np
import os
import scipy.io.wavfile as wav
import math
from scipy.stats import ks_2samp
from scipy.stats import ttest_ind

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
        """
        Write data in txt-file
        :return: None
        """
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
        """
        Save results of analysis in a text file
        :param path: path to folder to store the text file
        :return: None
        """
        if self.analysis_done:
            f = open(path + "/" + self.name + ".txt", 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))
        else:
            print("Noch keine Werte analysiert, daher gibt es keine Werte zu speichern")

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
        """
        Run praat file. Added from myspsolution.py
        :return: results of praat script
        """
        sound = self.audio_files_path + "/" + self.audio_file
        sourcerun = "myspsolution.praat"
        path = self.audio_files_path + "/"

        return run_file(sourcerun, -20, 2, 0.3, "yes", sound, path, 80, 400, 0.01, capture_output=True)

    def analyzeWavFile(self):
        """
        Analyze a wav file and store results in a dictionary
        :return: None
        """
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

        return words

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
                    time_filled_pauses.append((timestamp[0], timestamp[1]))
        self.analyzed_values["filled_pauses"] = pauses_number

    @staticmethod
    def analyze_num_pauses(parsel_object):
        """
        Count number of pauses
        :param parsel_object: parselmouth.Data object
        :return: number of silent pauses
        """
        # mysp.mysppaus(p,c)
        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        try:
            z3 = int(z2[1])
        except:
            return 0
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
        """
        Analyze rate of speech
        :param parsel_object: parselmouth.Data object
        :return: syllables per second
        """

        z1 = str(parsel_object[1])
        z2 = z1.strip().split()
        z3 = z2[2]
        try:
            float(z3)
        except:
            return 0
        # syllables/sec original duration
        return z3

    @staticmethod
    def analyze_balance(parsel_object):
        """
        Analyze ratio of spoken speech to total speech
        :param parsel_object: parselmouth.Data object
        :return: ratio
        """
        # mysp.myspbala(p,c)

        z1 = str(parsel_object[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        try:
            z4 = float(z2[6])
        except:
            return 0
        return z4

    @staticmethod
    def analyze_mood(parsel_object):

        try:
            z1 = str(parsel_object[1])
            z2 = z1.strip().split()
            z3 = float(z2[8])
            z4 = float(z2[7])
            if z4 <= 114:
                g = 101
                j = 3.4
            elif 114 < z4 <= 135:
                g = 128
                j = 4.35
            elif 135 < z4 <= 163:
                g = 142
                j = 4.85
            elif 163 < z4 <= 197:
                g = 182
                j = 2.7
            elif 197 < z4 <= 226:
                g = 213
                j = 4.5
            elif z4 > 226:
                g = 239
                j = 5.3
            else:
                print("Voice not recognized")
                exit()

            def teset(a, b, c, d):
                d1 = np.random.wald(a, 1, 1000)
                d2 = np.random.wald(b, 1, 1000)
                d3 = ks_2samp(d1, d2)
                c1 = np.random.normal(a, c, 1000)
                c2 = np.random.normal(b, d, 1000)
                c3 = ttest_ind(c1, c2)
                y = ([d3[0], d3[1], abs(c3[0]), c3[1]])
                return y

            nn = 0
            mm = teset(g, j, z4, z3)
            while mm[3] > 0.05 and mm[0] > 0.04 or nn < 5:
                mm = teset(g, j, z4, z3)
                nn = nn + 1
            nnn = nn
            if mm[3] <= 0.09:
                mmm = mm[3]
            else:
                mmm = 0.35
            if 97 < z4 <= 114:
                # print("a Male, mood of speech: Showing no emotion, normal")
                return "showing no emotion"
            elif 114 < z4 <= 135:
                # print("a Male, mood of speech: Reading")
                return "reading"
            elif 135 < z4 <= 163:
                # print("a Male, mood of speech: speaking passionately")
                return "speaking passionately"
            elif 163 < z4 <= 197:
                # print("a female, mood of speech: Showing no emotion, normal")
                return "showing no emotion"
            elif 197 < z4 <= 226:
                # print("a female, mood of speech: Reading")
                return "reading"
            elif 226 < z4 <= 245:
                # print("a female, mood of speech: speaking passionately")
                return "speaking passionately"
            else:
                print("Voice not recognized")
                return  "Stimmung nicht erkannt"
        except:
            print("Try again the sound of the audio was not clear")


def compare_results(self, old_results):
        print("Durchschnittliche Lautstärke:")
        print("Goldstandart: " + old_results["mean_intensity"] + "\t" + "Ihre Aufnahme: " + str(self.analyzed_values["mean_intensity"]))

        print("Redegeschwindigkeit (Silben pro Sekunde):")
        print("Goldstandart: " + old_results["rate_of_speech"] + "\t" + "Ihre Aufnahme: " + str(self.analyzed_values["rate_of_speech"]))

        print("Gesamtlänge und Anzahl von Pausen: ")
        print("Goldstandart: " + old_results["length"] + " Sek, davon  " + old_results["pauses"] + " Pausen"+ "\t" +
              "Ihre Aufnahme: " + str(self.analyzed_values["length"]) + " Sek, davon  " + str(self.analyzed_values["pauses"]) + " Pausen")

        print("Durchschnittliche Pausenlänge:")
        print("Goldstandart: " + old_results["mean_pauses"] + " Sek \t" + "Ihre Aufnahme: " + str(self.analyzed_values["mean_pauses"]) + " Sek")

        print("Verhältnis von geprochener Zeit zu der Gesamtzeit: ")
        print("Goldstandart: " + old_results["balance"] + "\t" + "Ihre Aufnahme: " + str(self.analyzed_values["balance"]))

        print("Verhältnis von Füllwörtern zu allen Wörtern: ")
        print("Goldstandart: " + old_results["filler_rate"] + "\t" + "Ihre Aufnahme: " + str(self.analyzed_values["filler_rate"]))

        print("Stil der gesamten Rede: ")
        print("Goldstandart: " + old_results["mood"] + "\t" + "Ihre Aufnahme: " + str(self.analyzed_values["mood"]))


def load_old_results(file_path):
    old_results = {}
    with open(file_path, encoding="utf8", mode="r") as file:
        for line in file.readlines():
            words = line.split()
            if len(words) > 1:
                old_results[words[0][:-1]] = words[1:]
    return old_results
