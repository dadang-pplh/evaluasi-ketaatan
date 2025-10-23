import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Evaluasi Ketaatan Mandiri", page_icon="🧾", layout="centered")

# --- Tema visual ---
st.markdown("""
<style>
    .footer {text-align:center; color:#888; font-size:13px; margin-top:50px;}
    .stProgress > div > div > div > div {background-color: #2c7a7b;}
</style>
""", unsafe_allow_html=True)

# --- Header dengan logo dan nama dinas ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("logo_dlh.png", width=100)
with col_title:
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='margin-bottom: 0; color: #2c3e50;'>Evaluasi Ketaatan Mandiri</h1>
            <p style='font-size: 20px; color: #555;'>Dinas Lingkungan Hidup Kabupaten Contoh</p>
            <hr style='border:1px solid #2c7a7b; width:70%; margin:auto;'>
        </div>
    """, unsafe_allow_html=True)

# --- Identitas Pelaku Usaha ---
with st.container():
    st.header("📋 Identitas Pelaku Usaha")
    col1, col2 = st.columns(2)
    with col1:
        nama_perusahaan = st.text_input("Nama Perusahaan")
        penanggung_jawab = st.text_input("Penanggung Jawab")
    with col2:
        email = st.text_input("Email (opsional)")
        tanggal = datetime.now().strftime("%d %B %Y")
        st.text_input("Tanggal", tanggal, disabled=True)
st.divider()

# --- Membaca pertanyaan dari CSV ---
try:
    df_q = pd.read_csv("pertanyaan.csv", encoding="utf-8", quotechar='"', sep=",", on_bad_lines="skip")
except FileNotFoundError:
    st.error("❌ File 'pertanyaan.csv' tidak ditemukan. Pastikan file tersebut ada di folder yang sama dengan app.py.")
    st.stop()

required_cols = {"Pertanyaan", "Dasar_Hukum", "Pelanggaran"}
if not required_cols.issubset(df_q.columns):
    st.error("❌ File CSV harus memiliki kolom: 'Pertanyaan', 'Dasar_Hukum', dan 'Pelanggaran'.")
    st.stop()

# --- Form Pertanyaan ---
st.header("📘 Daftar Pertanyaan")
st.write("Pilih **Ya** jika kewajiban sudah dipenuhi, dan **Tidak** jika belum.")

responses = {}
for i, row in df_q.iterrows():
    pertanyaan = row["Pertanyaan"]
    responses[pertanyaan] = st.radio(pertanyaan, ["Ya", "Tidak"], horizontal=True, key=f"q_{i}")

# --- Proses Hasil ---
if st.button("🔍 Lihat Hasil Evaluasi"):
    total = len(responses)
    score = sum([1 for r in responses.values() if r == "Ya"])
    percent = (score / total) * 100

    st.divider()
    st.subheader("📊 Hasil Evaluasi")
    st.write(f"**Nama Perusahaan:** {nama_perusahaan or '-'}")
    st.write(f"**Tanggal Evaluasi:** {tanggal}")
    st.write(f"**Tingkat Ketaatan:** {percent:.0f}%")

    st.progress(percent / 100)

    if percent >= 90:
        st.success("✅ Perusahaan telah memenuhi hampir seluruh kewajiban lingkungan hidup. Pertahankan kinerja ini.")
        status = "TAAT"
    elif percent >= 60:
        st.warning("⚠️ Perusahaan cukup taat, namun masih ada beberapa kewajiban yang belum terpenuhi.")
        status = "CUKUP TAAT"
    else:
        st.error("❌ Perusahaan belum memenuhi sebagian besar kewajiban lingkungan hidup. Segera lakukan pembenahan.")
        status = "BELUM TAAT"

    belum_taat = [q for q, r in responses.items() if r == "Tidak"]
    if belum_taat:
        st.markdown("### ⚠️ Kewajiban yang Belum Dipenuhi")
        for q in belum_taat:
            dasar = df_q.loc[df_q["Pertanyaan"] == q, "Dasar_Hukum"].values[0]
            pelanggaran = df_q.loc[df_q["Pertanyaan"] == q, "Pelanggaran"].values[0]
            st.markdown(f"- {pelanggaran}  \n  👉 *Melanggar {dasar}*")

    chart_data = pd.DataFrame({
        "Status": ["Taat", "Belum Taat"],
        "Jumlah": [score, total - score]
    }).set_index("Status")
    st.bar_chart(chart_data)

    hasil_df = pd.DataFrame([{
        "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Perusahaan": nama_perusahaan,
        "Penanggung Jawab": penanggung_jawab,
        "Email": email,
        "Skor (%)": percent,
        "Status": status,
        "Kewajiban Belum Ditaati": "; ".join(
            [df_q.loc[df_q["Pertanyaan"] == q, "Pelanggaran"].values[0] for q in belum_taat]
        )
    }])

    hasil_df.to_csv("hasil_evaluasi.csv", mode="a", header=False, index=False)

    st.download_button(
        label="⬇️ Unduh Hasil Evaluasi (CSV)",
        data=hasil_df.to_csv(index=False).encode("utf-8"),
        file_name=f"Hasil_Ketaatan_{nama_perusahaan or 'Perusahaan'}.csv",
        mime="text/csv"
    )

st.markdown('<p class="footer">© 2025 Dinas Lingkungan Hidup Kabupaten Contoh. Aplikasi ini dibuat untuk meningkatkan kesadaran dan kepatuhan pelaku usaha terhadap peraturan lingkungan hidup.</p>', unsafe_allow_html=True)
