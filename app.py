import streamlit as st
import pandas as pd
from datetime import datetime

# --- Konfigurasi halaman ---
st.set_page_config(page_title="Evaluasi Ketaatan Mandiri", layout="centered")

# --- Judul Aplikasi ---
st.title("🧾 Evaluasi Ketaatan Mandiri Lingkungan Hidup")
st.caption("Isi form berikut untuk mengetahui tingkat ketaatan perusahaan terhadap kewajiban lingkungan hidup.")

# --- Identitas Pelaku Usaha ---
with st.expander("📋 Identitas Pelaku Usaha", expanded=True):
    nama_perusahaan = st.text_input("Nama Perusahaan")
    penanggung_jawab = st.text_input("Nama Penanggung Jawab")
    email = st.text_input("Alamat Email (opsional)")
    st.write("---")

# --- Membaca daftar pertanyaan ---
try:
    df_q = pd.read_csv("pertanyaan.csv")
except FileNotFoundError:
    st.error("❌ File 'pertanyaan.csv' tidak ditemukan. Pastikan file tersebut ada di folder yang sama dengan app.py.")
    st.stop()

# Validasi kolom wajib
required_cols = {"Pertanyaan", "Dasar_Hukum", "Pelanggaran"}
if not required_cols.issubset(df_q.columns):
    st.error("❌ File CSV harus memiliki kolom: 'Pertanyaan', 'Dasar_Hukum', dan 'Pelanggaran'.")
    st.stop()

# --- Tampilkan pertanyaan ---
st.header("📘 Daftar Pertanyaan")
st.write("Pilih **Ya** jika kewajiban sudah dipenuhi, dan **Tidak** jika belum.")

responses = {}
for i, row in df_q.iterrows():
    pertanyaan = row["Pertanyaan"]
    responses[pertanyaan] = st.radio(pertanyaan, ["Ya", "Tidak"], horizontal=True, key=f"q_{i}")

# --- Tombol hasil ---
if st.button("🔍 Lihat Hasil Evaluasi"):
    total = len(responses)
    score = sum([1 for r in responses.values() if r == "Ya"])
    percent = (score / total) * 100

    st.subheader("📊 Hasil Evaluasi")
    st.write(f"**Nama Perusahaan:** {nama_perusahaan or '-'}")
    st.write(f"**Tanggal Evaluasi:** {datetime.now().strftime('%d %B %Y')}")
    st.write(f"**Tingkat Ketaatan:** {percent:.0f}%")

    # --- Indikator warna ---
    if percent >= 90:
        st.success("✅ Perusahaan Anda **TAAT** terhadap seluruh kewajiban lingkungan hidup.")
    elif percent >= 60:
        st.info("⚠️ Perusahaan Anda **cukup taat**, namun masih ada beberapa kewajiban yang belum terpenuhi.")
    else:
        st.error("❌ Perusahaan Anda **belum taat** terhadap sebagian besar kewajiban lingkungan hidup.")

    # --- Daftar pelanggaran ---
    belum_taat = [q for q, r in responses.items() if r == "Tidak"]
    if belum_taat:
        st.markdown("### ⚠️ Kewajiban yang Belum Dipenuhi")
        for q in belum_taat:
            dasar = df_q.loc[df_q["Pertanyaan"] == q, "Dasar_Hukum"].values[0]
            pelanggaran = df_q.loc[df_q["Pertanyaan"] == q, "Pelanggaran"].values[0]
            st.markdown(f"- {pelanggaran}  \n  👉 *Melanggar {dasar}*")

    # --- Simpan hasil ke CSV ---
    hasil_df = pd.DataFrame([{
        "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Perusahaan": nama_perusahaan,
        "Penanggung Jawab": penanggung_jawab,
        "Email": email,
        "Skor (%)": percent,
        "Status": "TAAT" if percent >= 90 else "CUKUP TAAT" if percent >= 60 else "BELUM TAAT",
        "Kewajiban Belum Ditaati": "; ".join(
            [df_q.loc[df_q["Pertanyaan"] == q, "Pelanggaran"].values[0] for q in belum_taat]
        )
    }])

    hasil_df.to_csv("hasil_evaluasi.csv", mode="a", header=False, index=False)

    st.download_button(
        label="⬇️ Unduh Hasil (CSV)",
        data=hasil_df.to_csv(index=False).encode("utf-8"),
        file_name=f"Hasil_Ketaatan_{nama_perusahaan or 'Perusahaan'}.csv",
        mime="text/csv"
    )

st.write("---")
st.caption("Aplikasi ini merupakan alat bantu mandiri untuk evaluasi ketaatan lingkungan hidup.")
