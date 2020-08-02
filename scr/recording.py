import argparse
import queue
import sys
from datetime import datetime

import cv2
import sounddevice as sd
import soundfile as sf
#import msvcrt
from scipy.io.wavfile import write
from PyQt5.QtCore import pyqtSignal, QObject
import threading

from PyQt5 import QtCore, QtWidgets
import statistics_window

class recording_window(QtWidgets.QWidget):

    def initUI(self):
        self.recording_started = False
        self.setObjectName("recording_window")
        self.setWindowTitle("Aufnahme")
        self.resize(250, 170)

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 10, 170, 140))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.play_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.play_button.setObjectName("play_button")
        self.verticalLayout.addWidget(self.play_button)

        self.stop_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.stop_button.setObjectName("stop_button")
        self.verticalLayout.addWidget(self.stop_button)

        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("recording_status")
        self.verticalLayout.addWidget((self.label))

        self.quit_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.quit_button.setObjectName("quit_button")
        self.verticalLayout.addWidget(self.quit_button)


        self.play_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.quit_button.clicked.connect(self.close)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self, recording_window):
        _translate = QtCore.QCoreApplication.translate
        self.play_button.setText(_translate("recording_window", "Play"))
        self.stop_button.setText(_translate("recording_window", "Stop"))
        self.quit_button.setText(_translate("recording_window", "Quit"))


    def start(self):
        now = datetime.now()
        timestamp = now.strftime("_%y%m%d_%H:%M")
        filename = "recording" + timestamp
        self.label.setText("Aufnahme gestartet ...")
        self.recording_started = True
        audio_thread = threading.Thread(target=record_audio)
        audio_thread.start()
        #video_thread = threading.Thread(target=record_video)
        #video_thread.start()
        record_video()



    def stop(self):
        if self.recording_started:
            self.label.setText("Aufnahme wird gestoppt \nund gespeichert")
        else:
            self.label.setText("Aufnahme noch nicht \ngestartet")


def record_audio(filename="test2.wav"):
    q = queue.Queue()
    parser = argparse.ArgumentParser(add_help=False)

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    try:

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(filename, mode='x', samplerate=44100,
                          channels=1) as file:
            with sd.InputStream(samplerate=44100,
                                channels=1, callback=callback):
                print("Recording...")
                while True:
                    #if msvcrt.kbhit():
                    #    key_stroke = msvcrt.getch()
                    #    if key_stroke.decode("utf-8") == "q":
                    #        parser.exit(0)
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))

def record_video(filename="test2.avi"):

    frames_per_second = 24.0

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, frames_per_second, (640,  480))

    while True:
        ret, frame = cap.read()
        out.write(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def start(self):

    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()
    #video_thread = threading.Thread(target=record_video)
    #video_thread.start()
    record_video()

#start("test2")



def start_gui_recording():
    app = QtWidgets.QApplication(sys.argv)
    ui = recording_window()
    sys.exit(app.exec_())

#start_gui_recording()

