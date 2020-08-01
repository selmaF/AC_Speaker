import analyze_file as af

import sys

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
            self.axes.cla()
        ax.set_ylim(ylim)
        ax.plot(x_data, y_data, style)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        self.draw()

    def plot_pie(self, labels, sizes):
        ax = self.figure.add_subplot(111)
        self.axes.cla()
        ax.pie(sizes, labels=labels, shadow=True, startangle=90)
        self.draw()


class Ui_statistics_window(QtWidgets.QDialog):
    def setupUi(self):
        results, self.name = af.open_and_analyse_file()
        # save results of the analsis of the whole file in whole
        self.whole = results[0]
        # save results of the analysis of the sections
        self.sections = results[1]

        self.setWindowTitle("Analysis")
        self.setObjectName("statistics_window")
        self.resize(531, 700)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(20, 260, 491, 400))
        self.frame.setObjectName("frame")

        # setup Matplotlib-Widget
        self.canvasStatistik = PlotCanvas(self.frame, width=5, height=4)
        self.canvasStatistik.move(0, 0)

        # self.graphicsStatistik.setGeometry(QtCore.QRect(20, 260, 491, 301))
        # self.graphicsStatistik.setObjectName("graphicsStatistik")

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

        self.verticalLayout.addLayout(self.horizonalLayoutRest)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self, statistics_window):
        _translate = QtCore.QCoreApplication.translate
        statistics_window.setWindowTitle(_translate("statistics_window", self.name))
        self.button_pauses_num.setText(_translate("statistics_window", "stille Pausen"))
        self.button_pauses_len.setText(_translate("statistics_window", "Länge stille Pausen"))
        self.button_rate_of_speech.setText(_translate("statistics_window", "Geschwindigkeitslevel"))
        self.button_balance.setText(_translate("statistics_window", "Balance"))
        self.button_mood.setText(_translate("statistics_window", "Stimmung"))
        self.button_intensity.setText(_translate("statistics_window", "Lautstärke"))
        self.button_fillers.setText(_translate("statistics_window", "gefüllt"))

    def show_pause_num_statistic(self):
        self.textStatistic.setText("Die gesamte Anzahl der Pausen: " + str(self.whole["pauses"]))
        self.textStatistic.append(
            "Die durchschnittliche Längen der Pausen: " + "%.2f secs" % (self.whole["mean_of_pauses"]))

        pauses_sections = []
        # mean_pauses_sections = []
        sections = []
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            pauses_sections.append(section_parameter["pauses"])
            #    mean_pauses_sections.append(section_parameter["mean_of_pauses"])
            sections.append(section)

        self.canvasStatistik.plot("stille Pausen", sections, pauses_sections, "Abschnitte", "Anzahl Pausen",
                                  (0, max(pauses_sections) + 1), False)
        # self.canvasStatistik.plot("Pausenlänge", sections, mean_pauses_sections, "Abschnitte", "länge der Pausen",
        #                          (0, max(mean_pauses_sections)), True)

    def show_pause_len_statistic(self):
        self.textStatistic.setText("Die durchschnittliche Längen der stillen Pausen: " + "%.2f secs"
                                   % (self.whole["mean_of_pauses"]))
        mean_pauses_sections = []
        sections = []
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            mean_pauses_sections.append(section_parameter["mean_of_pauses"])
            sections.append(section)
        self.canvasStatistik.plot("Pausenlänge", sections, mean_pauses_sections, "Abschnitte", "Länge der Pausen [s]",
                                  (0.2, max(mean_pauses_sections) + 0.2), False)

    def show_rate_of_speech_statistic(self):
        self.textStatistic.setText("Rate of Speech der gesamten Rede: " + str(self.whole["rate_of_speech"]))
        # gib plot an self.graphicsStatistik
        rate_sections = []
        sections = []
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            rate_sections.append(section_parameter["rate_of_speech"])
            sections.append(section)

        self.canvasStatistik.plot("Geschwindigkeitslevel", sections, rate_sections, "Abschnitte",
                                  "Silben pro Sekunde", (0, 1), False)

        self.textStatistic.append("Mit einer Geschwindigkeit von " + str(min(rate_sections)) + " ist Abschnitt "
                                  + str(sections[rate_sections.index(min(rate_sections))]) + " der langsamste")

    def show_balance_statistic(self):
        self.textStatistic.setText("Balance der gesamten Rede: " + str(self.whole["balance"]))
        # gib plot an self.graphicsStatistik
        balance_sections = []
        sections = []
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            balance_sections.append(section_parameter["balance"])
            sections.append(section)

        self.canvasStatistik.plot("Balance", sections, balance_sections, "Abschnitte",
                                  "Gesprochene Zeit/ Gesammte Zeit", (0, 1), False)

    def show_intensity_statistic(self):
        self.textStatistic.setText(
            "Die durchschnittliche Lautstärke der gesprochenen Rede war: %.2f dB" % self.whole["mean_intensity"])
        # gib plot an self.graphicsStatistik
        mean_intensity = []
        sections = []
        for i, section_parameter in enumerate(self.sections):
            section = i + 1
            mean_intensity.append(section_parameter["mean_intensity"])
            sections.append(section)

        self.canvasStatistik.plot("Lautstärke", sections, mean_intensity, "Abschnitte",
                                  "Lautstärke [dB]", (min(mean_intensity) - 1, max(mean_intensity) + 1), False)

    def show_fillers_statistic(self):
        self.textStatistic.setText(
            "Das Verhältnis der Füllwörter zum Rest:  " + str(self.whole["filler_rate"]))
        self.textStatistic.setText(
            "Die Anzahl der gefüllten Pausen: " + str(self.whole["filled_pauses"])
        )
        for key, value in self.whole["most_used_fillers"].items():
            self.textStatistic.append(
                "Das Füllwort \"{0}\" wurde {1} mal verwendet".format(key, value))

    def show_mood_statistic(self):
        self.textStatistic.setText("Stimmung der gesamten Rede: " + str(self.whole["mood"]))
        labels = ["speaking passionatly", "showing no emotion", "reading"]
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


def start_gui_statistics():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_statistics_window()
    ui.setupUi()
    sys.exit(app.exec_())


# start_gui_statistics()

if __name__ == '__main__':
    start_gui_statistics()
    # app = QtWidgets.QApplication(sys.argv)
    # ex = App()
    # sys.exit(app.exec_())
