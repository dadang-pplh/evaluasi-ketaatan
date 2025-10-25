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
    st.image("logo_dlh.png", width=100)
with col_title:
    st.markdown(
        "<div style='text-align:center;'><h1 style='margin-bottom:0;'>Evaluasi Ketaatan Mandiri</h1>"
        "<p style='font-size:20px; color:#555;'>Dinas Lingkungan Hidup Kabupaten Sukoharjo</p>"
        "<hr style='border:1px solid #2c7a7b; width:70%; margin:auto;'></div>",
        unsafe_allow_html=True
    )

st.subheader("🧾 Identitas Pelaku Usaha")

nama_usaha = st.text_input("Nama Pelaku Usaha / Perusahaan *")
alamat_usaha = st.text_area("Alamat Usaha *")
penanggung_jawab = st.text_input("Nama Penanggung Jawab *")
email = st.text_input("Email (opsional)")

st.markdown("---")


st.write("### 🏢 Identitas Pelaku Usaha")
nama_usaha = st.text_input("Nama Pelaku Usaha")

st.write("### 📋 Kuesioner Evaluasi Ketaatan")
data = pd.read_csv("pertanyaan.csv")
jawaban = {}

for i, row in data.iterrows():
    jawaban[row["pertanyaan"]] = st.radio(row["pertanyaan"], ["Ya", "Tidak"], index=0, key=f"q{i}")

if st.button("Lihat Hasil Evaluasi"):
    total = len(data)
    taat = sum(1 for v in jawaban.values() if v == "Ya")
    skor = round(taat / total * 100, 2)
    status = "Taat" if skor == 100 else "Belum Taat"

    st.success(f"**Hasil Evaluasi:** {status}")
    st.write(f"**Skor Ketaatan:** {skor}%")

    if status == "Belum Taat":
        st.write("#### Kewajiban yang Belum Ditaati:")
        pelanggaran = data[["pertanyaan", "pasal", "pernyataan_pelanggaran"]].loc[
            [jawaban[q] == "Tidak" for q in data["pertanyaan"]]
        ]
        st.table(pelanggaran[["pernyataan_pelanggaran", "pasal"]])

        # Buat PDF dengan text wrapping
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        style_table = ParagraphStyle(name="Table", fontSize=10, leading=12, alignment=0)

        story = []
        story.append(Image("logo_dlh.png", width=60, height=60))
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>LAPORAN EVALUASI KETAATAN MANDIRI</b>", styles["Title"]))
        story.append(Paragraph("Dinas Lingkungan Hidup Kabupaten Sukoharjo", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Nama Usaha:</b> {nama_usaha}", style))
        story.append(Paragraph(f"<b>Alamat:</b> {alamat_usaha}", style))
        story.append(Paragraph(f"<b>Penanggung Jawab:</b> {penanggung_jawab}", style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Tanggal Evaluasi: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
        story.append(Paragraph(f"Hasil Ketaatan: <b>{status}</b>", styles["Normal"]))
        story.append(Paragraph(f"Skor: {skor}%", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Kewajiban yang Belum Ditaati:", styles["Heading3"]))

        # Tabel dengan Paragraph agar bisa wrap
        table_data = [["Pernyataan Pelanggaran", "Pasal yang Dilanggar"]]
        for _, row in pelanggaran.iterrows():
            pelanggaran_text = Paragraph(row["pernyataan_pelanggaran"], style_table)
            pasal_text = Paragraph(row["pasal"], style_table)
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
        
if st.button("Lihat Hasil Evaluasi"):
    if not nama_usaha or not alamat_usaha or not penanggung_jawab:
        st.warning("⚠️ Harap lengkapi semua kolom identitas pelaku usaha sebelum melanjutkan.")
    else:
        # tampilkan hasil evaluasi dan tombol unduh PDF
        tampilkan_hasil(data, nama_usaha, alamat_usaha, penanggung_jawab)

