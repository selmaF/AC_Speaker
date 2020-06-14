import parselmouth
from parselmouth.praat import run_file
import numpy as np
from scipy.stats import ks_2samp
from scipy.stats import ttest_ind
import scipy.io.wavfile as wav
import seaborn as sns
import matplotlib.pyplot as plt
import math


class AudioAnalyzer:

    def __init__(self, name, first_audio, audio_files_path):
        self.name = name
        self.audio_file = first_audio
        self.audio_files_path = audio_files_path
        self.analyzed_values = {}
        # for the userCaseAnalysis:
        # userCaseValues["length_in_sec"]
        # self.userCaseValues["pauses"]
        # self.userCaseValues["rate_of_speech"] = z3
        # self.userCaseValues["balance"]
        # self.userCaseValues["mood"]

    def analyzeWholeFile(self):
        self.analyzeIntensity()
        self.analyze()
        self.printResults()
        #self.testPlot()

    def setStandard(self):
        # write data in txt-file
        if self.analyzed_values["pauses"] != 0:
            f = open('standard.txt', 'w')
            f.write(self.name + '\n')
            for key in self.analyzed_values.keys():
                f.write("%s, %s\n" % (key, self.analyzed_values[key]))
            pass

        else:
            print("noch keine Werte analysiert")
        return

    def getResults(self):
        return self.analyzed_values

    def printResults(self):
        length = str(self.analyzed_values["length_in_sec"])
        pauses = str(self.analyzed_values["pauses"])
        print("\n")
        print(self.name)
        print("Bei einer Gesamtlänge von " + length + " Sekunden wurden " + pauses + " Pausen gemacht")
        print("Die durchschnittlich gesprochenen Silben pro Sekunde betragen " + str(self.analyzed_values["rate_of_speech"]))
        print("Das Verhältnis von geprochener Zeit zu der Gesamtzeit ist " + str(self.analyzed_values["balance"]))
        print("Die semantische Analyse ergab:  " + self.analyzed_values["mood"])

    def testPlot(self):
        # versuch zu plotten aus Parselmouth Documentation, Release 0.4.0.dev0
        sns.set()  # Use seaborn's default style to make attractive graphsplt.rcParams['figure.dpi'] = 100# Show nicely large images in this noteboo
        plt.rcParams['figure.dpi'] = 100  # Show nicely large images in this notebook
        snd = parselmouth.Sound(self.audio_files_path + "/" + self.audio_file)
        plotter = Plotter(snd)
        plotter.draw_intensity()
        #plotter.draw_spectrogram()

    def runPraatFile(self):
        # added from myspsolution.py
        try:
            sound = self.audio_files_path + "/" + self.audio_file
            sourcerun = "myspsolution.praat"
            path = self.audio_files_path + "/"
        except:
            print("Try again the sound of the audio was not clear")
        return run_file(sourcerun, -20, 2, 0.3, "yes", sound, path, 80, 400, 0.01, capture_output=True)

    def analyzeIntensity(self):
        snd = parselmouth.Sound(self.audio_files_path + "/" + self.audio_file)
        intensity = snd.to_intensity()
        intensity_points = intensity.values.T
        mean = np.mean(intensity_points)
        self.analyzed_values["mean_intensity"] = mean

    def analyze(self, section="whole"):

        # added from myspsolution.py
        sound = self.audio_files_path + "/" + self.audio_file

        # length of the .wav file nach https://stackoverflow.com/questions/40651891/get-length-of-wav-file-in-samples-with-python
        try:
            (source_rate, source_sig) = wav.read(sound)
            duration_seconds = len(source_sig) / float(source_rate)
            # print("Länge des Audiofiles= ", duration_seconds)
            self.analyzed_values["length_in_sec"] = math.ceil(duration_seconds)
        except:
            print("Try again the sound of the audio was not clear")

        # mysp.mysppaus(p,c)
        try:
            # count number of pauses
            objects = self.runPraatFile()
            # print(objects[0])  # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
            z1 = str(objects[
                         1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
            z2 = z1.strip().split()
            z3 = int(z2[1])  # will be the integer number 10
            # print("number_of_pauses=", z3)
            self.analyzed_values["pauses"] = z3
        except:
            print("Try again the sound of the audio was not clear")

        # mysp.myspsr(p, c)
        try:
            # print(objects[0])  # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
            z1 = str(objects[1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
            z2 = z1.strip().split()
            z3 = int(z2[2])  # will be the integer number 10
            # print("rate_of_speech=", z3, "# syllables/sec original duration")
            self.analyzed_values["rate_of_speech"] = z3
        except:
            print("Try again the sound of the audio was not clear")

        # mysp.myspbala(p,c)
        try:
            # print(objects[0])  # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
            z1 = str(objects[
                         1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
            z2 = z1.strip().split()
            z4 = float(z2[6])  # will be the floating point number 8.3
            # print("balance=", z4, "# ratio (speaking duration)/(original duration)")
            self.analyzed_values["balance"] = z4
        except:
            print("Try again the sound of the audio was not clear")

        # mysp.myspgend(p,c)
        try:
            # print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
            z1 = str(objects[
                         1])  # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
            z2 = z1.strip().split()
            z3 = float(z2[8])  # will be the integer number 10
            z4 = float(z2[7])  # will be the floating point number 8.3
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
                self.analyzed_values["mood"] = "showing no emotion"
            elif 114 < z4 <= 135:
                # print("a Male, mood of speech: Reading")
                self.analyzed_values["mood"] = "reading"
            elif 135 < z4 <= 163:
                # print("a Male, mood of speech: speaking passionately")
                self.analyzed_values["mood"] = "speaking passionately"
            elif 163 < z4 <= 197:
                # print("a female, mood of speech: Showing no emotion, normal")
                self.analyzed_values["mood"] = "showing no emotion"
            elif 197 < z4 <= 226:
                # print("a female, mood of speech: Reading")
                self.analyzed_values["mood"] = "reading"
            elif 226 < z4 <= 245:
                # print("a female, mood of speech: speaking passionately")
                self.analyzed_values["mood"] = "speaking passionately"
            else:
                print("Voice not recognized")
                self.analyzed_values["mood"] = "Voice not recognized"
        except:
            print("Try again the sound of the audio was not clear")


class Plotter:
    # snd entspricht Ausgabe von parselmouth.Sound(path to wav-file)
    def __init__(self, snd):
        self.snd = snd
        self.intensity = snd.to_intensity()
        self.spectrogram = snd.to_spectrogram()

    def draw_spectrogram(self, dynamic_range=70):
        X, Y = self.spectrogram.x_grid(), self.spectrogram.y_grid()
        sg_db = 10 * np.log10(self.spectrogram.values)
        plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        plt.ylim([self.spectrogram.ymin, self.spectrogram.ymax])
        plt.xlabel("time [s]")
        plt.ylabel("frequency [Hz]")
        plt.show()

    def draw_intensity(self):
        plt.figure()
        plt.plot(self.intensity.xs(), self.intensity.values.T, linewidth=3, color='w')
        plt.plot(self.intensity.xs(), self.intensity.values.T, linewidth=1)
        plt.grid(False)
        plt.ylim(0)
        plt.ylabel("intensity [dB]")
        plt.xlim([self.snd.xmin, self.snd.xmax])
        plt.show()
