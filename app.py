import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

st.set_page_config(page_title="Evaluasi Ketaatan Mandiri", layout="centered")

# Header
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo_dlh.png", width=100)
    except Exception:
        pass
with col_title:
    st.markdown(
        "<div style='text-align:center;'><h1 style='margin-bottom:0;'>Evaluasi Ketaatan Mandiri</h1>"
        "<p style='font-size:20px; color:#555;'>Dinas Lingkungan Hidup Kabupaten Sukoharjo</p>"
        "<hr style='border:1px solid #2c7a7b; width:70%; margin:auto;'></div>",
        unsafe_allow_html=True
    )

st.write("### 🏢 Identitas Pelaku Usaha (WAJIB diisi sebelum evaluasi)")

nama_usaha = st.text_input("Nama Pelaku Usaha", key="nama_usaha")
alamat = st.text_input("Alamat", key="alamat")
pemilik = st.text_input("Nama Pemilik / Penanggung Jawab", key="pemilik")
npwp = st.text_input("NPWP (boleh kosong jika tidak punya)", key="npwp")
email = st.text_input("Email (opsional)", key="email")
telepon = st.text_input("No. Telepon / WhatsApp (opsional)", key="telepon")

required_filled = bool(nama_usaha.strip()) and bool(pemilik.strip())

if not required_filled:
    st.warning("Isi **Nama Pelaku Usaha** dan **Nama Pemilik / Penanggung Jawab** terlebih dahulu untuk melanjutkan evaluasi.")

st.write("---")
st.write("### 📋 Kuesioner Evaluasi Ketaatan")

try:
    data = pd.read_csv("pertanyaan.csv")
except FileNotFoundError:
    st.error("File 'pertanyaan.csv' tidak ditemukan. Silakan unggah file pertanyaan.csv pada folder yang sama atau gunakan fitur upload.")
    uploaded = st.file_uploader("Unggah pertanyaan.csv (format CSV)", type=["csv"])
    if uploaded is not None:
        data = pd.read_csv(uploaded)
    else:
        st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca pertanyaan.csv: {e}")
    st.stop()

jawaban = {}

with st.form(key="form_evaluasi"):
    for i, row in data.iterrows():
        jawaban[row["pertanyaan"]] = st.radio(row["pertanyaan"], ["Ya", "Tidak"], index=0, key=f"q{i}")

    if required_filled:
        submit = st.form_submit_button("Lihat Hasil Evaluasi")
    else:
        st.button("Lihat Hasil Evaluasi (Lengkapi identitas dulu)", disabled=True)
        submit = False

if 'submit' in locals() and submit:
    total = len(data)
    taat = sum(1 for v in jawaban.values() if v == "Ya")
    skor = round(taat / total * 100, 2) if total > 0 else 0
    status = "Taat" if skor == 100 else "Belum Taat"

    st.success(f"**Hasil Evaluasi:** {status}")
    st.write(f"**Skor Ketaatan:** {skor}%")

    st.write("#### Identitas Pelaku Usaha yang tercatat:")
    st.write(f"- **Nama Pelaku Usaha:** {nama_usaha}")
    st.write(f"- **Alamat:** {alamat or '-'}")
    st.write(f"- **Pemilik / Penanggung Jawab:** {pemilik}")
    st.write(f"- **NPWP:** {npwp or '-'}")
    st.write(f"- **Email:** {email or '-'}")
    st.write(f"- **Telepon:** {telepon or '-'}")

    if status == "Belum Taat":
        st.write("#### Kewajiban yang Belum Ditaati:")
        mask = [jawaban[q] == "Tidak" for q in data["pertanyaan"]]
        pelanggaran = data.loc[mask, ["pertanyaan", "pasal", "pernyataan_pelanggaran"]]
        if not pelanggaran.empty:
            st.table(pelanggaran[["pernyataan_pelanggaran", "pasal"]])

        # Generate PDF with wrapped text
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        style_table = ParagraphStyle(name="Table", fontSize=10, leading=12, alignment=0)

        story = []
        try:
            story.append(Image("logo_dlh.png", width=60, height=60))
        except Exception:
            pass
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>LAPORAN EVALUASI KETAATAN MANDIRI</b>", styles["Title"]))
        story.append(Paragraph("Dinas Lingkungan Hidup Kabupaten Sukoharjo", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Nama Pelaku Usaha: <b>{nama_usaha or '-'} </b>", styles["Normal"]))
        story.append(Paragraph(f"Alamat: {alamat or '-'}", styles["Normal"]))
        story.append(Paragraph(f"Pemilik / Penanggung Jawab: {pemilik}", styles["Normal"]))
        story.append(Paragraph(f"NPWP: {npwp or '-'}", styles["Normal"]))
        story.append(Paragraph(f"Tanggal Evaluasi: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
        story.append(Paragraph(f"Hasil Ketaatan: <b>{status}</b>", styles["Normal"]))
        story.append(Paragraph(f"Skor: {skor}%", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Kewajiban yang Belum Ditaati:", styles["Heading3"]))

        table_data = [["Pernyataan Pelanggaran", "Pasal yang Dilanggar"]]
        for _, row in pelanggaran.iterrows():
            pelanggaran_text = Paragraph(row["pernyataan_pelanggaran"], style_table)
            pasal_text = Paragraph(str(row["pasal"]), style_table)
            table_data.append([pelanggaran_text, pasal_text])

        table = Table(table_data, colWidths=[300, 180])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c7a7b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)

        doc.build(story)
        buffer.seek(0)

        st.download_button(
            label="📄 Unduh Hasil Evaluasi (PDF)",
            data=buffer,
            file_name=f"Hasil_Evaluasi_{nama_usaha or 'Tanpa_Nama'}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Selamat! Semua kewajiban telah dipenuhi.")

    try:
        hasil = {
            "waktu": datetime.now().isoformat(),
            "nama_usaha": nama_usaha,
            "alamat": alamat,
            "pemilik": pemilik,
            "npwp": npwp,
            "email": email,
            "telepon": telepon,
            "skor": skor,
            "status": status
        }
        df_hasil = pd.DataFrame([hasil])
        df_hasil.to_csv("hasil_evaluasi.csv", mode="a", header=not pd.io.common.file_exists("hasil_evaluasi.csv"), index=False)
    except Exception:
        pass
else:
    st.info("Lengkapi identitas di atas (Nama Pelaku Usaha & Pemilik) lalu tekan 'Lihat Hasil Evaluasi'.")
