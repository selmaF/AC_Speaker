import analyzer as a
import sys
from pydub import AudioSegment

# die wav dateien sollten 44.100 Hz und 16 bit resolution besitzen

current_number_of_pauses = 0
current_rate_of_speech = 0
current_ratio = 0


def find_frames(section_name, audio_frame, audio_files_path, data_whole_file):

    analyzer_section = a.AudioAnalyzer(audio_frame, audio_files_path)
    analyzer_section.analyzeWavFile()
    data_section = analyzer_section.getResults()

    length_section = data_section["length_in_sec"]
    number_of_pauses_section = data_section["pauses"]
    rate_of_speech_section = data_section["rate_of_speech"]
    ratio_section = data_section["balance"]
    mood_section = data_section["mood"]
    mean_intensity_section = data_section["mean_intensity"]
    mean_pauses_section = data_section["mean_of_pauses"]

    # pauses/length
    pauses_length_section = (float(number_of_pauses_section)/float(length_section))
    pauses_length_whole = float(data_whole_file["pauses"])/ float(data_whole_file["length_in_sec"])
    print("\n")
    print("Auffällig an " + section_name + " mit der Länge " + str(length_section) + " sec: ")      # TODO: kein print wenn nichts Auffäliges vorhanden (Daria)
    if pauses_length_section > pauses_length_whole + 0.1:
        print("In " + section_name + " haben Sie mit " + str(number_of_pauses_section) + " Pausen mehr Pausen als im Durchschnitt gemacht")
    if pauses_length_section + 0.1 < pauses_length_whole:
        print("In " + section_name + " haben Sie mit " + str(number_of_pauses_section) + " Pausen weniger Pausen als im Durchschnitt gemacht")
    if mean_intensity_section < (data_whole_file["mean_intensity"] - 4): # 10 ist random gewählt --> todo finde realistischen Schwellenwert
        print("In " + section_name + " haben sie im Durchschnitt deutlich leiser gesprochen")
    if mean_pauses_section > (data_whole_file["mean_of_pauses"] + 0.3 ):  # 0.3 ist random gewählt --> todo finde realistischen Schwellenwert
        print("In " + section_name + " sind Ihre Pausen mit einer durchnittlichen Länge von %.2f deutlich länger als im Durchschnitt" % mean_pauses_section)
    if current_rate_of_speech > rate_of_speech_section:
        print("In " + section_name + " war Ihre Rede mit " + str(rate_of_speech_section) + " Silben pro Sekunde langsamer als im Durchscnitt")
    if current_rate_of_speech < rate_of_speech_section:
        print("In " + section_name + " war Ihre Rede mit " + str(rate_of_speech_section) + " Silben pro Sekunde schneller als im Durchschnitt")
    if ratio_section < data_whole_file["balance"]:
        print("Verhältnis zwischen aktiver Sprechzeit und Gesamtsprechzeit lag in dem " + section_name + " mit " + str(ratio_section) + " unter dem Durchschnitt")
        # print(audio_frame)
    if mood_section != data_whole_file["mood"]:
        print("Die semantische Analyse von " + section_name + " unterscheidet sich mit \"" + mood_section + "\" von der der gesammten Rede")


def split_audio_file(audio_file, last_second):
    speech = AudioSegment.from_wav(audio_files_path + "/" + audio_file + ".wav")
    section_size = 15
    for number_section, section in enumerate(range(0, last_second, section_size)):
        section_start = section*1000
        section_end = (section+section_size)*1000-1
        section_speech = speech[section_start:section_end]
        section_speech.export((audio_files_path + "/" + "Abschnitt" + str(number_section) + ".wav"), format="wav", bitrate="44.1k")
        number_of_sections = number_section
    return number_of_sections


if __name__ == '__main__':
    
    # TODO: read video file, extract audio (Jakob)
    
    try:
        first_audio = sys.argv[1]       # die wav Dateien sollten 44.100 Hz und 16 bit resolution besitzen
    except IndexError:
        first_audio = "langsam_denkend"
    audio_files_path = "audio"

    analyzer = a.AudioAnalyzer(first_audio, audio_files_path)
    analyzer.analyzeWavFile()
    analyzer.analyze_recognizer()

    try:
        analyzer.printResults()
        data_whole = analyzer.getResults()
    except ImportError:
        print("Analyse noch nicht durchgeführt")

    #save_as_gold = input("\n Wollen Sie die Werte als Goldstandard speichern? Geben Sie ein j wenn ja " + "\n")
    #if save_as_gold == "j":
    #    analyzer.setStandard()

    # number_of_sections = split_audio_file(first_audio, data_whole["length_in_sec"])
    # for i in range(number_of_sections):
    #     find_frames("Abschnitt " + str(i), "Abschnitt" + str(i), audio_files_path, data_whole)
