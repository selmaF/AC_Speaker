
import statistics_window

from PyQt5 import QtCore, QtWidgets
import sys


class Ui_MainWindow(object):


    def open_statistic_window(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = statistics_window.Ui_statistics_window()
        self.ui.setupUi()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(702, 369)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(90, 40, 481, 101))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.savedButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.savedButton.setObjectName("savedButton")
        self.verticalLayout.addWidget(self.savedButton)
        self.savedButton.clicked.connect(self.open_statistic_window)

        self.recordButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.recordButton.setObjectName("recordButton")
        self.verticalLayout.addWidget(self.recordButton)

        self.compareButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.compareButton.setObjectName("compareButton")
        self.verticalLayout.addWidget(self.compareButton)

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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Reden analyiseren"))
        self.savedButton.setText(_translate("MainWindow", "Analysiere gespeichertes Video"))
        self.recordButton.setText(_translate("MainWindow", "Nehme Video zum Analysieren auf"))
        self.compareButton.setText(_translate("MainWindow", "Vergleiche ältere Ergebnisse"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
