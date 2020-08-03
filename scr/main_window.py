
import statistics_window
import recording
import ui_compare_window

from PyQt5 import QtCore, QtWidgets
import sys


class Ui_MainWindow(object):

    def open_statistic_window(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = statistics_window.Ui_statistics_window()
        sections = self.horizontalSlider.value()
        self.ui.setupUi(sections)

    def open_recording(self):
        self.window = QtWidgets.QMainWindow()
        self.uiRec = recording.recording_window()
        self.uiRec.initUI(self.horizontalSlider.value())

    def open_compare_window(self):
        self.window = QtWidgets.QMainWindow()
        self.uiComp = ui_compare_window.Ui_compare_window()
        self.uiComp.initUI()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(702, 250)     # Größe vom Fenster

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(90, 40, 481, 150))   #
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.savedButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.savedButton.setObjectName("savedButton")
        self.verticalLayout.addWidget(self.savedButton)
        self.savedButton.clicked.connect(self.open_statistic_window)

        self.compareButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.savedButton.setObjectName("compareButton")
        self.verticalLayout.addWidget(self.compareButton)
        self.compareButton.clicked.connect(self.open_compare_window)

        self.recordButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.recordButton.setObjectName("recordButton")
        self.verticalLayout.addWidget(self.recordButton)
        self.recordButton.clicked.connect(self.open_recording)

        self.label_sec_per_section = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_sec_per_section.setObjectName("sec_per_section_label")
        self.verticalLayout.addWidget(self.label_sec_per_section)

        self.horizontalSlider = QtWidgets.QSlider(self.verticalLayoutWidget)
        self.horizontalSlider.setMinimum(10)
        self.horizontalSlider.setMaximum(30)
        self.horizontalSlider.setValue(20)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.verticalLayout.addWidget(self.horizontalSlider)

        self.lcdNumber = QtWidgets.QLCDNumber(self.verticalLayoutWidget)
        self.lcdNumber.setProperty("value", 20.0)
        self.verticalLayout.addWidget(self.lcdNumber)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 702, 22))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.horizontalSlider.sliderMoved['int'].connect(self.lcdNumber.display)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Reden analyiseren"))
        self.savedButton.setText(_translate("MainWindow", "Analysiere gespeichertes Video"))
        self.recordButton.setText(_translate("MainWindow", "Nehme Video zum Analysieren auf"))
        self.label_sec_per_section.setText(_translate("MainWindow", "Sekunden pro Abschnitt"))
        self.compareButton.setText(_translate("MainWindow", "Vergleiche mit älteren Ergebnissen"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

