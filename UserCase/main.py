import myspsolution as mysp
import pickle
import sys

# bis jetzt liest jede funktione das Audio File neu ein, alalysiert es und schließt es wieder
# das ist zwar super ineffizient aber bis Mittwoch/UserCase wohl egal

current_number_of_pauses = 0            # TODO: Maike, könntest du in diesen Variablen die vom Tool ausgegebenen Werte reinspeichern?
current_rate_of_speech = 0
ratio = 0


def find_frames(audio_frame):           # TODO: am besten den Audioabschnitt durch das Tool analysieren und die Werte in Variablen abspeichern. Wenn das bis morgen nicht fertig ist, dann nehmen wir die fake Werte.
    # mysp.mysppaus(first_audio, audio_files_path)
    # mysp.myspsr(first_audio, audio_files_path)
    # mysp.myspbala(first_audio, audio_files_path)
    # mysp.myspf0mean(first_audio, audio_files_path)
    # mysp.myspgend(first_audio, audio_files_path)
    number_of_pauses = 10
    rate_of_speech = 5
    current_ration = 0.5
    if (number_of_pauses - current_number_of_pauses) > 5 or (number_of_pauses - current_number_of_pauses) < -5:
        print("In diesen Abschnitten haben Sie " + str(number_of_pauses) + " gemacht:")
        print(audio_frame)
    if current_rate_of_speech > rate_of_speech:
        print("In diesem Abschnitt war Ihre Rede mit " + str(current_number_of_pauses) + " Silben pro Sekunde am langsamsten:")
        print(audio_frame)
    if current_rate_of_speech < rate_of_speech:
        print("In diesem Abschnitt war Ihre Rede mit " + str(current_number_of_pauses) + " Silben pro Sekunde am schnellsten:")
        print(audio_frame)
    if ratio < current_ration:
        print("Verhältnis zwischen aktiver Sprechzeit und Gesamtsprechzeit lag in diesem Abschnitt " + str(current_number_of_pauses))
        print(audio_frame)


if __name__ == '__main__':
    first_audio = sys.argv[1]       # die wav dateien sollten 44.100 Hz und 16 bit resolution besitzen
    audio_files_path = sys.argv[2]
    mysp.mysppaus(first_audio, audio_files_path)
    mysp.myspsr(first_audio, audio_files_path)
    mysp.myspbala(first_audio, audio_files_path)
    mysp.myspf0mean(first_audio, audio_files_path)
    mysp.myspgend(first_audio, audio_files_path)
    save_as_gold = input("Wollen Sie die Werte als Goldstandard speichern? Gebe ein y wenn ja "+ "\n")
    if save_as_gold == "y":
        pass
    find_frames("C:...path to audio frame")         #TODO: 10 sec Anbschnitt rausschneiden und den Pfad als argument der Funktion übergeben

