import myspsolution as mysp
import pickle

# die wav dateien sollten 44.100 Hz und 16 bit resolution besitzen
p = "affectus_laut_leise.wav"
c = "data/myprosody/audioFiles"

# bis jetzt liest jede funktione das Audio File neu ein, alalysiert es und schließt es wieder
# das ist zwar super ineffizient aber bis Mittwoch/UserCase wohl egal

mysp.mysppaus(p,c)
mysp.myspsr(p,c)
mysp.myspbala(p,c)
mysp.myspf0mean(p,c)
mysp.myspgend(p,c)
