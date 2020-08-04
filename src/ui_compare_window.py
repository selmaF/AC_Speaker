import os
import sys

from PyQt5 import QtCore, QtWidgets
import analyzer
import analyze_file as af


class Ui_compare_window(QtWidgets.QWidget):

    def initUI(self):

        self.setObjectName("Vergleiche_Statistik")
        self.resize(250, 170)

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

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def open_file(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(directory=os.path.dirname(os.path.abspath(__file__)))
            #file = QtWidgets.QFileDialog.getOpenFileName(directory="../data/results")
            self.old_results = analyzer.load_old_results(file[0])
        except:
            print("Die Datei konnte nicht analysiert werden")

    def analyze_audio(self):
        self.results, self.name, self.path_directory = af.open_and_analyse_file(0, True)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.open_file_button.setText(_translate("Vergleiche_Statistik", "Statistik laden"))
        self.open_analyze_button.setText(_translate("Vergleiche_Statistik", "Audio analysieren"))

def start_gui_compare():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_compare_window()
    ui.initUI()
    sys.exit(app.exec_())

