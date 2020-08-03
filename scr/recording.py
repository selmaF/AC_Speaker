import argparse
import queue
import sys
from datetime import datetime

import cv2
import sounddevice as sd
import soundfile as sf
import threading

from PyQt5 import QtCore, QtWidgets


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

        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("recording_status")
        self.verticalLayout.addWidget((self.label))


        self.play_button.clicked.connect(self.start)

        self.video_recorded = False
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self, recording_window):
        _translate = QtCore.QCoreApplication.translate
        self.play_button.setText(_translate("recording_window", "Play"))

    def start(self):
        now = datetime.now()
        timestamp = now.strftime("_%y%m%d_%H:%M")
        filename = "recording" + timestamp
        self.label.setText("Aufnahme gestartet ...")
        self.recording_started = True
        audio_thread = threading.Thread(target=self.record_audio)
        audio_thread.start()
        self.record_video()

        self.label.setText("Aufnahme beendet ...")
        if self.video_recorded:
            audio_thread.join(timeout=0.1)

    def record_video(self, filename="test2.avi"):
        """
        Record a video file in avi format. Stop recording with q press.
        :param filename: Name of the recorded file
        :return: None
        """

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
        self.video_recorded = True
        cv2.destroyAllWindows()

    def record_audio(self, filename="test2.wav"):
        """
        Record a mono audio file. Done when video file is recorded.
        :param filename: name of the recorded file
        :return: None
        """
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
                    print("Wird aufgenommen...")
                    while True:
                        if self.video_recorded:
                            parser.exit(0)
                        file.write(q.get())

        except KeyboardInterrupt:
            print('\nRecording finished')
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ': ' + str(e))


def start_gui_recording():
    app = QtWidgets.QApplication(sys.argv)
    ui = recording_window()
    ui.initUI()
    sys.exit(app.exec_())
