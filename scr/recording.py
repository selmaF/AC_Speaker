import argparse
import queue
import sys

import cv2
import sounddevice as sd
import soundfile as sf
import msvcrt
from scipy.io.wavfile import write


def record_video(filename):

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


def record_audio(filename):
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
                    if msvcrt.kbhit():
                        key_stroke = msvcrt.getch()
                        if key_stroke.decode("utf-8") == "q":
                            parser.exit(0)
                    file.write(q.get())

    except KeyboardInterrupt:
        print('\nRecording finished')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))


def start(filename):

    record_audio(filename + ".wav")
    record_video(filename + ".mp4")