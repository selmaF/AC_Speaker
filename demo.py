#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import os
import wave


def recognize_speech(audio_path, ac_model_path):
    model = Model(ac_model_path)
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    recognized_text = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            recognized_text.append(rec.Result())
    with open("text_file.txt", "w") as fp:
        for element in recognized_text:
            fp.write(element)
    return os.path.join(os.path.dirname(__file__), "text_file.txt")


def count_fillers(path_to_filler_file, sentences):
    filler_counter = {}
    filler_words = []
    words_number = []
    with open(path_to_filler_file, encoding="utf-8", mode="r") as fp:
        fil_words = fp.read()
        for fil_word in fil_words.split():
            filler_words.append(fil_word.rstrip(","))
    with open(sentences, encoding="utf-8", mode="r") as file:
        for rec_sentence in file.readlines():
            for line in rec_sentence.splitlines():
                if '"word"' in line:
                    word = line.split()[2].strip('"')
                    words_number.append(word)
                    if word in filler_words:
                        if word not in filler_counter:
                            filler_counter[word] = 0
                        filler_counter[word] += 1
    rate = sum(filler_counter.values()) / len(words_number) * 100
    sorted_counter = {k: v for k, v in sorted(filler_counter.items(), key=lambda item: item[1], reverse=True)}
    return rate, sorted_counter


path_to_file = recognize_speech("D:\\LMU\\affective_computing\\test.wav", "D:\\LMU\\affective_computing\\models\\kaldi-generic-de-tdnn_f-r20190328")

count_fillers("D:\\LMU\\affective_computing\\Fuellwoerter.txt", path_to_file)
