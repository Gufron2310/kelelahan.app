#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplikasi Streamlit – Cek Kelelahan Mahasiswa
Fuzzy Logic (scikit‑fuzzy) + Grafik + Riwayat + Tips
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ---------- Konfigurasi Halaman ----------
st.set_page_config(page_title="Cek Kelelahan Mahasiswa",
                   page_icon="🧠",
                   layout="centered")

st.markdown(
    "<h1 style='text-align:center;color:#2E8B57;'>🧠 Cek Kelelahan Mahasiswa</h1>",
    unsafe_allow_html=True,
)

# ---------- Fungsi Fuzzy ----------
def buat_sistem():
    tri = lambda x, a, b, c: fuzz.trimf(x, [a, b, c])

    jam_tidur   = ctrl.Antecedent(np.arange(0, 11), "jam_tidur")
    jumlah_tugas= ctrl.Antecedent(np.arange(0, 11), "jumlah_tugas")
    kafein      = ctrl.Antecedent(np.arange(0,  6), "kafein")
    stres       = ctrl.Antecedent(np.arange(0, 11), "stres")
    jam_belajar = ctrl.Antecedent(np.arange(0, 11), "jam_belajar")
    emosi       = ctrl.Antecedent(np.arange(0, 11), "emosi")
    kelelahan   = ctrl.Consequent(np.arange(0, 11), "kelelahan")

    # Fungsi keanggotaan
    jam_tidur['sedikit'] = tri(jam_tidur.universe,0,0,4)
    jam_tidur['cukup']   = tri(jam_tidur.universe,3,5,7)
    jam_tidur['banyak']  = tri(jam_tidur.universe,6,10,10)

    jumlah_tugas['sedikit'] = tri(jumlah_tugas.universe,0,0,3)
    jumlah_tugas['sedang']  = tri(jumlah_tugas.universe,2,5,8)
    jumlah_tugas['banyak']  = tri(jumlah_tugas.universe,7,10,10)

    kafein['tidak']   = tri(kafein.universe,0,0,1)
    kafein['sedikit'] = tri(kafein.universe,0,2,3)
    kafein['banyak']  = tri(kafein.universe,2,5,5)

    stres['rendah']  = tri(stres.universe,0,0,4)
    stres['sedang']  = tri(stres.universe,3,5,7)
    stres['tinggi']  = tri(stres.universe,6,10,10)

    jam_belajar['sebentar'] = tri(jam_belajar.universe,0,0,3)
    jam_belajar['normal']   = tri(jam_belajar.universe,2,5,8)
    jam_belajar['lama']     = tri(jam_belajar.universe,7,10,10)

    emosi['positif'] = tri(emosi.universe,0,0,3)
    emosi['netral']  = tri(emosi.universe,2,5,8)
    emosi['negatif'] = tri(emosi.universe,7,10,10)

    kelelahan['tidak_lelah']      = tri(kelelahan.universe,0,0,2)
    kelelahan['lelah_ringan']     = tri(kelelahan.universe,1,3,5)
    kelelahan['lelah_sedang']     = tri(kelelahan.universe,4,5,6)
    kelelahan['sangat_lelah']     = tri(kelelahan.universe,5,7,9)
    kelelahan['istirahat_serius'] = tri(kelelahan.universe,8,10,10)

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
        ctrl.Rule(jam_tidur['banyak'] & jumlah_tugas['banyak'],  kelelahan['lelah_sedang']),
        ctrl.Rule(kafein['banyak'] & stres['tinggi'],            kelelahan['lelah_sedang']),
        ctrl.Rule(emosi['negatif'] & stres['tinggi'],            kelelahan['sangat_lelah']),
        ctrl.Rule(jam_belajar['lama'] & kafein['sedikit'] & jam_tidur['sedikit'],
                  kelelahan['sangat_lelah']),
    ]

    return ctrl.ControlSystem(rules)

system = buat_sistem()

def hitung_fuzzy(data: dict):
    sim = ctrl.ControlSystemSimulation(system)
    for k, v in data.items():
        sim.input[k] = v
    sim.compute()
    s = sim.output['kelelahan']
    if s < 2:  return s, "Tidak Lelah",            "😁"
    if s < 4:  return s, "Lelah Ringan",           "🙂"
    if s < 6:  return s, "Lelah Sedang",           "😐"
    if s < 8:  return s, "Sangat Lelah",           "😫"
    return s,  "Butuh Istirahat Serius",           "🛌"

# ---------- Session State untuk Riwayat ----------
if "history" not in st.session_state:
    st.session_state["history"] = []

# ---------- Input Form ----------
st.header("Input Data")
with st.form("form_input"):
    val = {
        "jam_tidur":    st.slider("Jam Tidur (jam)",       0, 10, 6),
        "jumlah_tugas": st.slider("Jumlah Tugas",          0, 10, 3),
        "kafein":       st.slider("Konsumsi Kafein (cangkir)", 0, 5, 1),
        "stres":        st.slider("Tingkat Stres",         0, 10, 5),
        "jam_belajar":  st.slider("Jam Belajar (jam)",     0, 10, 4),
        "emosi":        st.slider("Emosi (0 positif – 10 negatif)", 0, 10, 5),
    }
    submitted = st.form_submit_button("Cek Kelelahan")

# ---------- Hasil & Riwayat ----------
if submitted:
    skor, status, emoji = hitung_fuzzy(val)
    st.markdown(f"### {emoji} **{status}** — Skor: {skor:.2f}")
    st.info("💡 Tips: Jaga kualitas tidur dan kontrol beban tugas untuk kesehatan optimal.")

    # Simpan riwayat ke session_state
    st.session_state["history"].append({**val, "skor": round(skor,2), "status": status})

# Tampilkan grafik & riwayat jika sudah ada data
if st.session_state["history"]:
    df = pd.DataFrame(st.session_state["history"])

    # Grafik batang
    st.subheader("🔎 Grafik Skor Kelelahan")
    fig, ax = plt.subplots()
    ax.bar(df.index, df["skor"], color="#2E8B57")
    ax.set_xticks(df.index)
    ax.set_xticklabels([f"Tes {i+1}" for i in df.index])
    ax.set_ylabel("Skor")
    ax.set_ylim(0, 10)
    st.pyplot(fig)

    # Tabel riwayat
    st.subheader("📄 Riwayat Input & Skor")
    st.dataframe(df, use_container_width=True)
