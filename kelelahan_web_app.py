import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

st.set_page_config(page_title="Deteksi Kelelahan Mahasiswa", layout="centered")

# ----- Definisi variabel fuzzy -----
jam_tidur   = ctrl.Antecedent(np.arange(0, 11, 1), 'jam_tidur')
jumlah_tugas= ctrl.Antecedent(np.arange(0, 11, 1), 'jumlah_tugas')
kafein      = ctrl.Antecedent(np.arange(0, 6, 1), 'kafein')
stres       = ctrl.Antecedent(np.arange(0, 11, 1), 'stres')
jam_belajar = ctrl.Antecedent(np.arange(0, 11, 1), 'jam_belajar')
emosi       = ctrl.Antecedent(np.arange(0, 11, 1), 'emosi')

kelelahan   = ctrl.Consequent(np.arange(0, 11, 1), 'kelelahan')

def seg(x, a, b, c):
    return fuzz.trimf(x, [a, b, c])

# Fungsi keanggotaan
jam_tidur['sedikit'] = seg(jam_tidur.universe, 0, 0, 4)
jam_tidur['cukup']   = seg(jam_tidur.universe, 3, 5, 7)
jam_tidur['banyak']  = seg(jam_tidur.universe, 6, 10, 10)

jumlah_tugas['sedikit'] = seg(jumlah_tugas.universe, 0, 0, 3)
jumlah_tugas['sedang']  = seg(jumlah_tugas.universe, 2, 5, 8)
jumlah_tugas['banyak']  = seg(jumlah_tugas.universe, 7, 10, 10)

kafein['tidak']   = seg(kafein.universe, 0, 0, 1)
kafein['sedikit'] = seg(kafein.universe, 0, 2, 3)
kafein['banyak']  = seg(kafein.universe, 2, 5, 5)

stres['rendah']  = seg(stres.universe, 0, 0, 4)
stres['sedang']  = seg(stres.universe, 3, 5, 7)
stres['tinggi']  = seg(stres.universe, 6, 10, 10)

jam_belajar['sebentar'] = seg(jam_belajar.universe, 0, 0, 3)
jam_belajar['normal']   = seg(jam_belajar.universe, 2, 5, 8)
jam_belajar['lama']     = seg(jam_belajar.universe, 7, 10, 10)

emosi['positif'] = seg(emosi.universe, 0, 0, 3)
emosi['netral']  = seg(emosi.universe, 2, 5, 8)
emosi['negatif'] = seg(emosi.universe, 7, 10, 10)

kelelahan['tidak_lelah']        = seg(kelelahan.universe, 0, 0, 2)
kelelahan['lelah_ringan']       = seg(kelelahan.universe, 1, 3, 5)
kelelahan['lelah_sedang']       = seg(kelelahan.universe, 4, 5, 6)
kelelahan['sangat_lelah']       = seg(kelelahan.universe, 5, 7, 9)
kelelahan['istirahat_serius']   = seg(kelelahan.universe, 8, 10, 10)

# Aturan fuzzy
rules = [
    ctrl.Rule(jam_tidur['sedikit'] & jumlah_tugas['banyak'] & stres['tinggi'] &
              jam_belajar['lama'] & emosi['negatif'], kelelahan['istirahat_serius']),
    ctrl.Rule(jam_tidur['sedikit'] & jumlah_tugas['banyak'], kelelahan['sangat_lelah']),
    ctrl.Rule(jam_tidur['sedikit'] & stres['tinggi'],        kelelahan['sangat_lelah']),
    ctrl.Rule(jam_tidur['cukup'] & jumlah_tugas['sedang'] & stres['sedang'],
              kelelahan['lelah_sedang']),
    ctrl.Rule(jam_tidur['cukup'] & kafein['banyak'] & stres['rendah'],
              kelelahan['lelah_ringan']),
    ctrl.Rule(jam_tidur['banyak'] & jumlah_tugas['sedikit'] & emosi['positif'],
              kelelahan['tidak_lelah']),
    ctrl.Rule(jam_tidur['banyak'] & jumlah_tugas['banyak'], kelelahan['lelah_sedang']),
    ctrl.Rule(kafein['banyak'] & stres['tinggi'],           kelelahan['lelah_sedang']),
    ctrl.Rule(emosi['negatif'] & stres['tinggi'],           kelelahan['sangat_lelah']),
    ctrl.Rule(jam_belajar['lama'] & kafein['sedikit'] & jam_tidur['sedikit'],
              kelelahan['sangat_lelah']),
]

system = ctrl.ControlSystem(rules)

def hitung(data):
    sim = ctrl.ControlSystemSimulation(system)
    for k, v in data.items():
        sim.input[k] = v
    sim.compute()
    nilai = sim.output['kelelahan']
    if nilai < 2:
        status = "Tidak Lelah"
    elif nilai < 4:
        status = "Lelah Ringan"
    elif nilai < 6:
        status = "Lelah Sedang"
    elif nilai < 8:
        status = "Sangat Lelah"
    else:
        status = "Butuh Istirahat Serius"
    return nilai, status

# ----- UI Streamlit -----
st.title("🧠 Deteksi Kelelahan Mahasiswa")

with st.form("form_input"):
    jam_tidur     = st.slider("Jam Tidur", 0, 10, 6)
    jumlah_tugas  = st.slider("Jumlah Tugas", 0, 10, 3)
    kafein        = st.slider("Kafein (cangkir)", 0, 5, 1)
    stres         = st.slider("Tingkat Stres", 0, 10, 5)
    jam_belajar   = st.slider("Jam Belajar", 0, 10, 4)
    emosi         = st.slider("Emosi (0 = positif, 10 = negatif)", 0, 10, 5)
    submit = st.form_submit_button("Cek Kelelahan")

if submit:
    data = {
        'jam_tidur': jam_tidur,
        'jumlah_tugas': jumlah_tugas,
        'kafein': kafein,
        'stres': stres,
        'jam_belajar': jam_belajar,
        'emosi': emosi
    }
    skor, status = hitung(data)
    st.success(f"Hasil: **{status}** (Skor: {skor:.2f})")
