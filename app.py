import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi tampilan halaman
st.set_page_config(page_title="Evaluasi Ketaatan Mandiri", layout="centered")

# Judul Aplikasi
st.title("🧾 Evaluasi Ketaatan Mandiri Lingkungan Hidup")
st.caption("Isi form berikut untuk mengetahui tingkat ketaatan perusahaan terhadap kewajiban lingkungan hidup.")

# Identitas pelaku usaha
with st.expander("📋 Identitas Pelaku Usaha", expanded=True):
    nama_perusahaan = st.text_input("Nama Perusahaan")
    penanggung_jawab = st.text_input("Nama Penanggung Jawab")
    email = st.text_input("Alamat Email (opsional)")
    st.write("---")

# Daftar pertanyaan dan pasal terkait
questions = {
    "Apakah perusahaan memiliki dokumen UKL-UPL atau Amdal yang masih berlaku?": "UU 32/2009 Pasal 36(1)",
    "Apakah perusahaan telah memiliki izin pembuangan air limbah (IPLC)?": "PP 22/2021 Pasal 214",
    "Apakah perusahaan melakukan pemantauan kualitas air limbah secara berkala dan melaporkannya?": "PP 22/2021 Pasal 269",
    "Apakah perusahaan mengelola limbah B3 sesuai ketentuan (penyimpanan, manifest, pihak pengelola berizin)?": "PP 22/2021 Pasal 261",
    "Apakah perusahaan telah menyampaikan laporan pelaksanaan pengelolaan lingkungan kepada instansi berwenang?": "PermenLHK 1/2021 Pasal 72"
}

st.header("📘 Daftar Pertanyaan")
st.write("Pilih **Ya** jika kewajiban sudah dipenuhi, dan **Tidak** jika belum.")

responses = {}
for q in questions:
    responses[q] = st.radio(q, ["Ya", "Tidak"], horizontal=True)

# Tombol untuk menampilkan hasil
if st.button("🔍 Lihat Hasil Evaluasi"):
    total = len(responses)
    score = sum([1 for r in responses.values() if r == "Ya"])
    percent = (score / total) * 100

    st.subheader("📊 Hasil Evaluasi")
    st.write(f"**Nama Perusahaan:** {nama_perusahaan or '-'}")
    st.write(f"**Tanggal Evaluasi:** {datetime.now().strftime('%d %B %Y')}")

    st.write(f"**Tingkat Ketaatan:** {percent:.0f}%")

    if percent == 100:
        st.success("Selamat! Perusahaan Anda **TAAT** terhadap seluruh kewajiban lingkungan hidup.")
    else:
        st.warning("Masih ada kewajiban yang belum dipenuhi:")

        belum_taat = [q for q, r in responses.items() if r == "Tidak"]
        for q in belum_taat:
            st.markdown(f"- {q}  \n  👉 *Melanggar {questions[q]}*")

    # Simpan hasil ke file CSV lokal (bisa diganti Google Sheet API nanti)
    df = pd.DataFrame([{
        "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Perusahaan": nama_perusahaan,
        "Penanggung Jawab": penanggung_jawab,
        "Email": email,
        "Skor (%)": percent,
        "Status": "TAAT" if percent == 100 else "BELUM TAAT",
        "Kewajiban Belum Ditaati": ", ".join([q for q, r in responses.items() if r == "Tidak"])
    }])

    df.to_csv("hasil_evaluasi.csv", mode="a", header=False, index=False)

    st.success("✅ Hasil evaluasi Anda telah tersimpan.")
    st.download_button(
        label="⬇️ Unduh Hasil (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"Hasil_Ketaatan_{nama_perusahaan or 'Perusahaan'}.csv",
        mime="text/csv"
    )

st.write("---")
st.caption("Aplikasi ini merupakan alat bantu mandiri untuk evaluasi ketaatan lingkungan hidup.")
