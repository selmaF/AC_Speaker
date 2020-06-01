import myspsolution as mysp
import pickle

# bis jetzt liest jede funktione das Audio File neu ein, alalysiert es und schließt es wieder
# das ist zwar super ineffizient aber bis Mittwoch/UserCase wohl egal

current_number_of_pauses = 0
current_rate_of_speech = 0


def find_frames(audio_frame):
    number_of_pauses = 10
    rate_of_speech = 5
    if (number_of_pauses - current_number_of_pauses) > 5 or (number_of_pauses - current_number_of_pauses) < -5:
        print("In diesen Abschnitten haben Sie " + str(number_of_pauses) + " gemacht:")
        print(audio_frame)
    if (current_rate_of_speech) > rate_of_speech:
        print("In diesem Abschnitt war Ihre Rede mit " + str(current_number_of_pauses) + " Silben pro Sekunde am langsamsten:")
        print(audio_frame)
    if (current_rate_of_speech) < rate_of_speech:
        print("In diesem Abschnitt war Ihre Rede mit " + str(current_number_of_pauses) + " Silben pro Sekunde am schnellsten:")
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


