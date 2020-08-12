import analyze_file as af

import sys
from shutil import copyfile

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np

from pydub import AudioSegment
from pydub.playback import play


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, title, x_data, y_data, x_label, y_label, ylim, add=False, style='bo--'):

        ax = self.figure.add_subplot(111)
        if not add:
            self.axes.clear()
        ax.set_ylim(ylim)
        ax.plot(x_data, y_data, style)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        self.draw()

    def plot_pie(self, labels, sizes):
        ax = self.figure.add_subplot(111)
        self.axes.clear()
        ax.pie(sizes, labels=labels, shadow=True, autopct='%1.1f%%',  startangle=90)
        self.draw()

    def plot_poses(self, array, labels, df):
        maxframe = df['frame_count'].max()
        maxsec = df['timestamp_x'].max()
        secs = df['timestamp_x'].unique()

        ax = self.figure.add_subplot(111)
        self.axes.clear()
        colmap = matplotlib.colors.ListedColormap(np.random.random((21, 3)))
        colmap.colors[0] = [0, 0, 0]
        data_color = (1 + np.arange(array.shape[0]))[:, None] * array
        ax.imshow(data_color, aspect='auto', cmap=colmap)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels)

        ax.set_xticks(np.arange(0, maxframe, int(maxframe / maxsec)), minor=False)
        ax.set_xticklabels(secs, fontdict=None, minor=False)
        ax.set_xlabel('Sekunde')
        self.draw()
        
    def plot_movement(self, dv_prev):
        maxframe = dv_prev['frame_count'].max()
        maxsec = dv_prev['timestamp_x'].max()
        secs = dv_prev['timestamp_x'].unique()

        ax = self.figure.add_subplot(111)
        self.axes.clear()

        #informationen für den ersten und zweiten teilgraphen
        leftwrist=dv_prev[dv_prev['part_names']=='leftWrist']
        leftwrist=leftwrist.set_index('frame_count')
        leftwrist=leftwrist['movement_vector_length']

        rightwrist=dv_prev[dv_prev['part_names']=='rightWrist']
        rightwrist=rightwrist.set_index('frame_count')
        rightwrist=rightwrist['movement_vector_length']

        #plotten der beiden teilgraphen
        leftwrist.plot(ax=ax, legend=True,label="Links")
        rightwrist.plot(ax=ax, legend=True,label="Rechts")

        #x-achsen beschriftung: zuerst wird die position der ticks, dann ihr inhalt festgelegt
        ax.set_xticks(np.arange(0,maxframe,int(maxframe/maxsec)), minor=False)
        ax.set_xticklabels(secs, fontdict=None, minor=False)

        #keine beschriftung an der y achse
        ax.set_yticks([], minor=False)

        ax.set_xlabel('Sekunde')
        ax.set_ylabel('Bewegungsheftigkeit')

        self.draw()


    def plot_clear(self):
        self.axes.clear()
        self.draw()


class Ui_statistics_window(QtWidgets.QDialog):

    def setupUi(self, section_size, name = None):

        self.section_size = section_size
        self.width = 550
        self.hight = 700
        self.width_canvas = self.width - 30
        self.hight_canvas = int(self.hight/2)
        self.width_text = self.width_canvas
        self.hight_text = int(self.hight/5)

        if name == None:
            results, self.results_video, self.name, self.path_directory = af.open_and_analyse_file(self.section_size)
        else:
            results, self.results_video, self.name, self.path_directory = af.analyze_recorded(self.section_size, name)

        # save results of the analsis of the whole file in whole
        if results != None:
            self.whole = results[0]
            # save results of the analysis of the sections
            self.sections = results[1]


        self.setWindowTitle("Analysis")
        self.setObjectName("statistics_window")
        self.resize(self.width, self.hight)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(20, 260, self.width_canvas, self.width_canvas))
        #self.frame.setGeometry(QtCore.QRect(left,top,width,height))
        self.frame.setObjectName("frame")

        # setup Matplotlib-Widget
        self.canvasStatistik = PlotCanvas(self.frame, width=5, height=4)
        self.canvasStatistik.move(0, 0)

        self.textStatistic = QtWidgets.QTextBrowser(self)
        self.textStatistic.setGeometry(QtCore.QRect(20, 100, self.width_text, self.hight_text))
        self.textStatistic.setObjectName("textStatistic")

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, self.width_text, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayoutPauses = QtWidgets.QHBoxLayout()
        self.horizontalLayoutPauses.setObjectName("horizontalLayoutPauses")

        self.button_pauses_num = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_pauses_num.setObjectName("button_pauses_num")
        self.horizontalLayoutPauses.addWidget(self.button_pauses_num)


        self.button_pauses_len = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_pauses_len.setObjectName("button_pauses_len")
        self.horizontalLayoutPauses.addWidget(self.button_pauses_len)


        self.button_fillers = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_fillers.setObjectName("button_fillers")
        self.horizontalLayoutPauses.addWidget(self.button_fillers)

        self.verticalLayout.addLayout(self.horizontalLayoutPauses)


        self.horizontalLayoutRest = QtWidgets.QHBoxLayout()
        self.horizontalLayoutRest.setObjectName("horizontalLayoutRest")

        self.button_rate_of_speech = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_rate_of_speech.setObjectName("button_rate_of_speech")
        self.horizontalLayoutRest.addWidget(self.button_rate_of_speech)


        self.button_balance = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_balance.setObjectName("button_balance")
        self.horizontalLayoutRest.addWidget(self.button_balance)


        self.button_intensity = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_intensity.setObjectName("button_intensity")
        self.horizontalLayoutRest.addWidget(self.button_intensity)


        self.button_mood = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_mood.setObjectName("button_mood")
        self.horizontalLayoutRest.addWidget(self.button_mood)


        self.verticalLayout.addLayout(self.horizontalLayoutRest)

        self.horizontalLayoutVideo = QtWidgets.QHBoxLayout()
        self.horizontalLayoutVideo.setObjectName("horizontalLayoutVideo")

        self.button_visual = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_visual.setObjectName("button_visual")
        self.horizontalLayoutVideo.addWidget(self.button_visual)


        self.button_visual2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_visual2.setObjectName("button_movement")
        self.horizontalLayoutVideo.addWidget(self.button_visual2)

        self.verticalLayout.addLayout(self.horizontalLayoutVideo)

        self.button_sections = QtWidgets.QPushButton(self)
        self.button_sections.setObjectName("button_section")
        self.button_sections.setGeometry(QtCore.QRect(self.width-150, self.hight-30, 130, 20))


        self.button_standard = QtWidgets.QPushButton(self)
        self.button_standard.setObjectName("button_standard")
        self.button_standard.setGeometry(QtCore.QRect(20, self.hight - 30, 160, 20))



        self.button_pauses_num.clicked.connect(self.show_pause_num_statistic)
        self.button_pauses_len.clicked.connect(self.show_pause_len_statistic)
        self.button_fillers.clicked.connect(self.show_fillers_statistic)
        self.button_rate_of_speech.clicked.connect(self.show_rate_of_speech_statistic)
        self.button_balance.clicked.connect(self.show_balance_statistic)
        self.button_intensity.clicked.connect(self.show_intensity_statistic)
        self.button_mood.clicked.connect(self.show_mood_statistic)
        self.button_visual.clicked.connect(self.show_visual_statistic)
        self.button_visual2.clicked.connect(self.show_movement_statistic)

        self.button_sections.clicked.connect(self.open_sections)
        self.button_standard.clicked.connect(self.save_standard)



        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self, statistics_window):
        _translate = QtCore.QCoreApplication.translate
        #        statistics_window.setWindowTitle(_translate("statistics_window", self.name))
        self.button_pauses_num.setText(_translate("statistics_window", "Pausen"))
        self.button_pauses_len.setText(_translate("statistics_window", "Länge stille Pausen"))
        self.button_rate_of_speech.setText(_translate("statistics_window", "Geschwindigkeitslevel"))
        self.button_balance.setText(_translate("statistics_window", "Balance"))
        self.button_mood.setText(_translate("statistics_window", "Stimmung"))
        self.button_intensity.setText(_translate("statistics_window", "Lautstärke"))
        self.button_fillers.setText(_translate("statistics_window", "Füllwörter"))
        self.button_visual.setText(_translate("statistics_window", "Posen"))
        self.button_visual2.setText(_translate("statistics_window", "Bewegung"))
        self.button_sections.setText(_translate("statistics_window", "öffne Abschnitte"))
        self.button_standard.setText(_translate("statistics_window", "speichere als Standard"))



    def show_pause_num_statistic(self):
        try:
            self.textStatistic.setText("Die gesamte Anzahl der stillen Pausen: " + str(self.whole["pauses"]))
            self.textStatistic.append("Die gesamte Anzahl der gefüllten Pausen: " + str(self.whole["filled_pauses"]))
            self.textStatistic.append(
                "Die durchschnittliche Länge der stillen Pausen: " + "%.2f secs" % (self.whole["mean_of_pauses"]))

            pauses_sections = []
            # mean_pauses_sections = []
            sections = []
            end_section = 0
            start_section = 0
            for i, section_parameter in enumerate(self.sections):
                section = i + 1
                end_section = end_section + section_parameter["length_in_sec"]
                pauses_sections.append(section_parameter["pauses"])
                sections.append(str(section) + "\nbis " + str(end_section) + " sec")

            self.canvasStatistik.plot("stille Pausen", sections, pauses_sections,
                                      "Abschnitte" , "Anzahl Pausen",
                                      (0, 10), False)
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_pause_len_statistic(self):
        try:
            self.textStatistic.setText("Die durchschnittliche Länge der stillen Pausen: " + "%.2f secs"
                                       % (self.whole["mean_of_pauses"]))
            mean_pauses_sections = []
            sections = []
            end_section = 0
            start_section = 0
            for i, section_parameter in enumerate(self.sections):
                section = i + 1
                end_section = end_section + section_parameter["length_in_sec"]
                mean_pauses_sections.append(section_parameter["mean_of_pauses"])
                sections.append(str(section) + "\nbis " + str(end_section) + " sec")

            try:
                max_len = max(mean_pauses_sections) + 0.2
            except:
                max_len = 1.6
            self.canvasStatistik.plot("Pausenlänge", sections, mean_pauses_sections,
                                      "Abschnitte", "Länge der Pausen [s]",
                                      (0.2, max_len))
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_rate_of_speech_statistic(self):
        print("anfang_rate")
        try:
            self.textStatistic.setText("Das Geschwindigkeitslevel der gesamten Rede: "+str(self.whole["rate_of_speech"]))
            rate_sections = []
            sections = []
            end_section = 0
            start_section = 0
            print("vor for schleife")
            for i, section_parameter in enumerate(self.sections):
                print(section_parameter["rate_of_speech"])
                section = i + 1
                end_section = end_section + section_parameter["length_in_sec"]
                print(section_parameter["length_in_sec"])
                rate_sections.append(float(section_parameter["rate_of_speech"]))
                print(rate_sections)
                sections.append(str(section) + "\nbis " + str(end_section) + " sec")
                print(sections)
                print("ende for schleife" + str(i))
            print(rate_sections)
            self.canvasStatistik.plot("Geschwindigkeit", sections, rate_sections,
                                      "Abschnitte", "Silben pro Sekunde", (0,9))
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")
            self.canvasStatistik.plot_clear()

    def show_balance_statistic(self):
        try:
            self.textStatistic.setText("Balance der gesamten Rede: " + str(self.whole["balance"]))
            # gib plot an self.graphicsStatistik
            balance_sections = []
            sections = []
            end_section = 0
            start_section = 0
            for i, section_parameter in enumerate(self.sections):
                section = i + 1
                end_section = end_section + section_parameter["length_in_sec"]
                balance_sections.append(section_parameter["balance"])
                sections.append(str(section) + "\nbis " + str(end_section) + " sec")

            self.canvasStatistik.plot("Balance", sections, balance_sections, "Abschnitte",
                                      "Gesprochene Zeit/ Gesammte Zeit", (0, 1))
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_intensity_statistic(self):
        try:
            self.textStatistic.setText(
                "Die durchschnittliche Lautstärke der gesprochenen Rede war: %.2f dB" % self.whole["mean_intensity"])
            # gib plot an self.graphicsStatistik
            mean_intensity = []
            sections = []
            end_section = 0
            start_section = 0
            for i, section_parameter in enumerate(self.sections):
                section = i+1
                end_section = end_section + section_parameter["length_in_sec"]
                mean_intensity.append(section_parameter["mean_intensity"])
                sections.append(str(section) + "\nbis " + str(end_section) + " sec")
            try:
                min_int =  min(mean_intensity) - 1
                max_int =  max(mean_intensity) + 1
            except:
                min_int = 55
                max_int = 75
            self.canvasStatistik.plot("Lautstärke", sections, mean_intensity, "Abschnitt",
                                      "Lautstärke [dB]", (min_int, max_int), False)
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_fillers_statistic(self):
        try:
            print("anfang filler")
            print(self.whole["filler_rate"])
            self.textStatistic.setText(
                "Verhältnis von Füllwörtern zu allen Wörtern:  %.2f " % self.whole["filler_rate"])
            for key, value in self.whole["most_used_fillers"].items():
                self.textStatistic.append(
                    "Das Füllwort \"{0}\" wurde {1} mal verwendet".format(key, value))

            self.canvasStatistik.plot_clear()
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_mood_statistic(self):
        try:
            self.textStatistic.setText("Stimmung der gesamten Rede: " + str(self.whole["mood"]))
            min_length = 19
            if self.sections[0]["length_in_sec"] > min_length:
                labels = ["speaking passionately", "showing no emotion", "reading"]
                distribution = [0, 0, 0]
                for i, section_parameter in enumerate(self.sections):
                    if section_parameter["length_in_sec"] > min_length:
                        if section_parameter["mood"] != self.whole["mood"]:
                            self.textStatistic.append("Die Stimmung in Abschnitt %i ist " % (i + 1) + section_parameter["mood"])
                        if section_parameter["mood"] == labels[0]:
                            distribution[0] += 1
                        elif section_parameter["mood"] == labels[1]:
                            distribution[1] += 1
                        elif section_parameter["mood"] == labels[2]:
                            distribution[2] += 1
                        else:
                            print("unbekannte Stimmung")
                    else:
                        self.textStatistic.append("Abschnitt "+ str(i+1) + " ist zu kurz für die Analyse")
                self.canvasStatistik.plot_pie(labels, distribution)
            else:
                self.textStatistic.append("Abschnitte zu kurz für Stimmungsanalyse")
                self.canvasStatistik.plot_clear()
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")

    def show_visual_statistic(self):

        self.textStatistic.setText("Analyse der Posen: "
                                   "\nAngewinkelte Arme (Arme angew.)"
                                   "\nVerschränkte Arme (Arme versch.)"
                                   "\nDie Hände werden vor dem Körper mittig gefaltet (Handg. umf.)" 
                                   "\nEinseitig herunterhängender Arm (Arm hängt)"
                                   "\nNach vorn gestreckter Arm (Arm ausge.)"
                                   "\nDas Gesicht wird verdeckt (Ges. verd.)")
        try:
            self.canvasStatistik.plot_poses(self.results_video["array_for_poses"], self.results_video["labels_for_poses"],
                                            self.results_video["df_for_movement"])
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")


    def show_movement_statistic(self):
        try:
            self.textStatistic.setText("Analyse der Bewegungsintensität des linken und rechten Arms")
            print("versuche plot_movement")
            self.canvasStatistik.plot_movement(self.results_video["df_for_movement"])
        except:
            self.textStatistic.setText("keine Analysedaten vorhanden")


    def open_sections(self):
        path_sections = self.path_directory + "/sections"
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(directory= path_sections)
            sound = AudioSegment.from_wav(file[0])
            play(sound)
        except:
            print("kein Abschnitt ausgewählt")

    def save_standard(self):
        results_path = "../data/results"
        copyfile(results_path + "/" + self.name + ".txt", results_path + "/standard.txt")


def start_gui_statistics():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_statistics_window()
    ui.setupUi(15)
    sys.exit(app.exec_())


#start_gui_statistics()

#if __name__ == '__main__':
 #   start_gui_statistics()
    # app = QtWidgets.QApplication(sys.argv)
    # ex = App()
    # sys.exit(app.exec_())

def save_plot(self, title, x_data, y_data, x_label, y_label, ylim, add=False, style='bo--'):
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.set_ylim(ylim)
    ax.plot(x_data, y_data, style)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    plt.savefig("..data/results/test.png")
