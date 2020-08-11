import os
import sys

from PyQt5 import QtCore, QtWidgets
import analyzer
import analyze_file as af


class statistik_window(QtWidgets.QWidget):

    def setupUi(self, old_results, results):
        self.setObjectName("Ergebnis")
        self.resize(700, 700)
    #    self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.old_results = old_results
        self.analyzed_values = results
        self.textStatistic = QtWidgets.QTextBrowser(self)
        self.textStatistic.setGeometry(QtCore.QRect(20, 90, 600, 400))
        self.textStatistic.setObjectName("textStatistic")

        self.textStatistic.setText("Durchschnittliche Lautstärke:" + "\n" +
                                   "Goldstandart: %.2f dB \nIhre Aufnahme: %.2f dB \n" % (float(self.old_results["mean_intensity"][0]),
                                                                                     self.analyzed_values["mean_intensity"]))
        self.textStatistic.append("Redegeschwindigkeit (Silben pro Sekunde):\n" +
                                  "Goldstandart: {} \nIhre Aufnahme: {}\n".format(self.old_results["rate_of_speech"][0],
                                                                                   self.analyzed_values["rate_of_speech"]))
        self.textStatistic.append("Gesamtlänge und Anzahl von Pausen: " + "\n" +
                                  "Goldstandart: %s Sek, davon %s Pausen \n" % (self.old_results["length_in_sec"][0],
                                                                                   self.old_results["pauses"][0]) +
                                  "Ihre Aufnahme: %s Sek, davon %i Pausen\n" % (self.analyzed_values["length_in_sec"],
                                                                                    self.analyzed_values["pauses"]))
        self.textStatistic.append("Durchschnittliche Pausenlänge:" + "\n" +
                                  "Goldstandart: %.2f Sek\nIhre Aufnahme: %.2f Sek\n" %(float(self.old_results["mean_of_pauses"][0]),
                                                                                          self.analyzed_values["mean_of_pauses"]))
        self.textStatistic.append("Verhältnis von geprochener Zeit zu der Gesamtzeit: " + "\n" +
                                   "Goldstandart: {} \nIhre Aufnahme: {}\n".format(self.old_results["balance"][0],
                                                                                   self.analyzed_values["balance"]))
        self.textStatistic.append("Stil der gesamten Rede: " + "\n" +
                                  "Goldstandart: {}\nIhre Aufnahme: {}\n".format(' '.join(old_results["mood"]),
                                                                                 ''.join(self.analyzed_values["mood"])))

        self.show()



class Ui_compare_window(QtWidgets.QWidget):

    def initUI(self):

        self.setObjectName("Vergleiche_Statistik")
        self.resize(250, 170)
        self.old_results = None
        self.results = None

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 10, 170, 140))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.open_file_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.open_file_button.setObjectName("open_stat_file")
        self.verticalLayout.addWidget(self.open_file_button)
        self.open_file_button.clicked.connect(self.open_file)

        self.open_analyze_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.open_file_button.setObjectName("open_stat_file")
        self.verticalLayout.addWidget(self.open_analyze_button)
        self.open_analyze_button.clicked.connect(self.analyze_audio)

        self.show_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.open_file_button.setObjectName("open_stat_file")
        self.verticalLayout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.show_statistik)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def open_file(self):
        try:
            #FIXME change with file = QtWidgets.QFileDialog.getOpenFileName(directory=os.path.dirname(os.path.abspath(__file__))
            result_path = "../data/results"
            file = QtWidgets.QFileDialog.getOpenFileName(directory=result_path)
            self.old_results = analyzer.load_old_results(file[0])
            print("Datei bearbeitet")
        except:
            print("Die Datei konnte nicht analysiert werden")

    def analyze_audio(self):
        self.results, _, self.name, self.path_directory = af.open_and_analyse_file(0, True)
        print("Analyse fertig")

    def show_statistik(self):
        if self.old_results is not None and self.results is not None:
            self.window = QtWidgets.QMainWindow()
            self.uiRec = statistik_window()
            self.uiRec.setupUi(self.old_results, self.results)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.open_file_button.setText(_translate("Vergleiche_Statistik", "Statistik laden"))
        self.open_analyze_button.setText(_translate("Vergleiche_Statistik", "Audio analysieren"))
        self.show_button.setText(_translate("Vergleiche_Statistik", "Statistik zeigen"))


def start_gui_compare():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_compare_window()
    ui.initUI()
    sys.exit(app.exec_())

