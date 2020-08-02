import analyze_file as af

import sys
from shutil import copyfile

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        FigureCanvas.updateGeometry(self)
        ax = self.figure.add_subplot(111)
        if not add:
            self.axes.cla()
        ax.set_ylim(ylim)
        ax.plot(x_data, y_data, style)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        self.draw()

    def plot_pie(self, labels, sizes):
        FigureCanvas.updateGeometry(self)
        ax = self.figure.add_subplot(111)
        self.axes.cla()
        ax.pie(sizes, labels=labels, shadow=True, autopct='%1.1f%%',  startangle=90)
        self.draw()


class Ui_statistics_window(QtWidgets.QDialog):

    def setupUi(self, section_size):
        self.section_size = section_size
        self.width = 531
        self.hight = 700

        results, self.name, self.path_directory = af.open_and_analyse_file(self.section_size)
        # save results of the analsis of the whole file in whole
        self.whole = results[0]
        # save results of the analysis of the sections
        self.sections = results[1]

        #read standard.txt and save results
        self.standard = af.get_results_from_text_file()

        self.setWindowTitle("Analysis")
        self.setObjectName("statistics_window")
        self.resize(self.width, self.hight)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(20, 260, 491, 400))
        self.frame.setObjectName("frame")

        # setup Matplotlib-Widget
        self.canvasStatistik = PlotCanvas(self.frame, width=5, height=4)
        self.canvasStatistik.move(0, 0)

        self.textStatistic = QtWidgets.QTextBrowser(self)
        self.textStatistic.setGeometry(QtCore.QRect(20, 90, 491, 151))
        self.textStatistic.setObjectName("textStatistic")

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 491, 70))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayoutPauses = QtWidgets.QHBoxLayout()
        self.horizontalLayoutPauses.setObjectName("horizontalLayoutPauses")

        self.button_pauses_num = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_pauses_num.setObjectName("button_pauses_num")
        self.horizontalLayoutPauses.addWidget(self.button_pauses_num)
        self.button_pauses_num.clicked.connect(self.show_pause_num_statistic)

        self.button_pauses_len = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_pauses_len.setObjectName("button_pauses_len")
        self.horizontalLayoutPauses.addWidget(self.button_pauses_len)
        self.button_pauses_len.clicked.connect(self.show_pause_len_statistic)

        self.button_fillers = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_fillers.setObjectName("button_fillers")
        self.horizontalLayoutPauses.addWidget(self.button_fillers)
        self.button_fillers.clicked.connect(self.show_fillers_statistic)

        self.verticalLayout.addLayout(self.horizontalLayoutPauses)
        self.horizonalLayoutRest = QtWidgets.QHBoxLayout()
        self.horizonalLayoutRest.setObjectName("horizontalLayoutRest")

        self.button_rate_of_speech = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_rate_of_speech.setObjectName("button_rate_of_speech")
        self.horizonalLayoutRest.addWidget(self.button_rate_of_speech)
        self.button_rate_of_speech.clicked.connect(self.show_rate_of_speech_statistic)

        self.button_balance = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_balance.setObjectName("button_balance")
        self.horizonalLayoutRest.addWidget(self.button_balance)
        self.button_balance.clicked.connect(self.show_balance_statistic)

        self.button_intensity = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_intensity.setObjectName("button_intensity")
        self.horizonalLayoutRest.addWidget(self.button_intensity)
        self.button_intensity.clicked.connect(self.show_intensity_statistic)

        self.button_mood = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_mood.setObjectName("button_mood")
        self.horizonalLayoutRest.addWidget(self.button_mood)
        self.button_mood.clicked.connect(self.show_mood_statistic)

        self.button_sections = QtWidgets.QPushButton(self)
        self.button_sections.setObjectName("button_section")
        self.button_sections.setGeometry(QtCore.QRect(self.width-150, self.hight-30, 130, 20))
        self.button_sections.clicked.connect(self.open_sections)

        self.button_standard = QtWidgets.QPushButton(self)
        self.button_standard.setObjectName("button_standard")
        self.button_standard.setGeometry(QtCore.QRect(20, self.hight - 30, 160, 20))
        self.button_standard.clicked.connect(self.save_standard)

        self.verticalLayout.addLayout(self.horizonalLayoutRest)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self, statistics_window):
        _translate = QtCore.QCoreApplication.translate
        statistics_window.setWindowTitle(_translate("statistics_window", self.name))
        self.button_pauses_num.setText(_translate("statistics_window", "Pausen"))
        self.button_pauses_len.setText(_translate("statistics_window", "Länge stille Pausen"))
        self.button_rate_of_speech.setText(_translate("statistics_window", "Geschwindigkeitslevel"))
        self.button_balance.setText(_translate("statistics_window", "Balance"))
        self.button_mood.setText(_translate("statistics_window", "Stimmung"))
        self.button_intensity.setText(_translate("statistics_window", "Lautstärke"))
        self.button_fillers.setText(_translate("statistics_window", "Füllwörter"))
        self.button_sections.setText(_translate("statistics_window", "öffne Abschnitte"))
        self.button_standard.setText(_translate("statistics_window", "speichere als Standard"))

    def show_pause_num_statistic(self):
        self.textStatistic.setText("Die gesamte Anzahl der stillen Pausen: " + str(self.whole["pauses"]))
        self.textStatistic.append("Die gesamte Anzahl der gefüllten Pausen: " + str(self.whole["filled_pauses"]))
        self.textStatistic.append(
            "Die durchschnittliche Länge der stillen Pausen: " + "%.2f secs" % (self.whole["mean_of_pauses"]))

        pauses_sections = []
        # mean_pauses_sections = []
        sections = []
        end_section = 0
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            end_section = end_section + section_parameter["length_in_sec"]
            pauses_sections.append(section_parameter["pauses"])
            sections.append(section)

        self.canvasStatistik.plot("stille Pausen", sections, pauses_sections,
                                  "Abschnitte" , "Anzahl Pausen",
                                  (0, max(pauses_sections) + 1), False)

    def show_pause_len_statistic(self):
        self.textStatistic.setText("Die durchschnittliche Länge der stillen Pausen: " + "%.2f secs"
                                   % (self.whole["mean_of_pauses"]))
        mean_pauses_sections = []
        sections = []
        end_section = 0
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            end_section = end_section + section_parameter["length_in_sec"]
            mean_pauses_sections.append(section_parameter["mean_of_pauses"])
            sections.append(section)
        self.canvasStatistik.plot("Pausenlänge", sections, mean_pauses_sections,
                                  "Abschnitte", "Länge der Pausen [s]",
                                  (0.2, max(mean_pauses_sections) + 0.2))

    def show_rate_of_speech_statistic(self):
        self.textStatistic.setText("Geschwindigkeitslever der gesamten Rede: " + str(self.whole["rate_of_speech"]))
        rate_sections = []
        sections = []
        end_section = 0
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            end_section = end_section + section_parameter["length_in_sec"]
            rate_sections.append(section_parameter["rate_of_speech"])
            sections.append(section)

        self.canvasStatistik.plot("Geschwindigkeit", sections, rate_sections,
                                  "Abschnitte", "Silben pro Sekunde", (0,9))

    def show_balance_statistic(self):
        self.textStatistic.setText("Balance der gesamten Rede: " + str(self.whole["balance"]))
        # gib plot an self.graphicsStatistik
        balance_sections = []
        sections = []
        end_section = 0
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            end_section = end_section + section_parameter["length_in_sec"]
            balance_sections.append(section_parameter["balance"])
            sections.append(str(section) + "\nEnde bei " + str(end_section) + " sec")

        self.canvasStatistik.plot("Balance", sections, balance_sections, "Abschnitte",
                                  "Gesprochene Zeit/ Gesammte Zeit", (0, 1))

    def show_intensity_statistic(self):
        self.textStatistic.setText(
            "Die durchschnittliche Lautstärke der gesprochenen Rede war: %.2f dB" % self.whole["mean_intensity"])
        # gib plot an self.graphicsStatistik
        mean_intensity = []
        sections = []
        end_section = 0
        for i, section_parameter in enumerate(self.sections):
            section = i+1
            end_section = end_section + section_parameter["length_in_sec"]
            mean_intensity.append(section_parameter["mean_intensity"])


        self.canvasStatistik.plot("Lautstärke", sections, mean_intensity, "Abschnitt",
                                  "Lautstärke [dB]", (min(mean_intensity) - 1, max(mean_intensity) + 1), False)

    def show_fillers_statistic(self):
        self.textStatistic.setText(
            "Das Verhältnis der Füllwörter zu anderen Wörtern:  " + str(self.whole["filler_rate"]))
        for key, value in self.whole["most_used_fillers"].items():
            self.textStatistic.append(
                "Das Füllwort \"{0}\" wurde {1} mal verwendet".format(key, value))

        self.canvasStatistik.plot("Keine Analyse der Abschnitte vorhanden", [0], [0], " "," ", (0,1) )

    def show_mood_statistic(self):
        self.textStatistic.setText("Stimmung der gesamten Rede: " + str(self.whole["mood"]))
        labels = ["speaking passionately", "showing no emotion", "reading"]
        distribution = [0, 0, 0]
        for i, section_parameter in enumerate(self.sections):
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

        self.canvasStatistik.plot_pie(labels, distribution)

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


# start_gui_statistics()

if __name__ == '__main__':
    start_gui_statistics()
    # app = QtWidgets.QApplication(sys.argv)
    # ex = App()
    # sys.exit(app.exec_())
