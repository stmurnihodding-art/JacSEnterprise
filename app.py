import streamlit as st
from google import genai
from google.genai import types
import io
import docx
from fpdf import FPDF

# 1. Konfigurasi Halaman & Tema
st.set_page_config(
    page_title="JacS Media Studio AI - TikTok, IG & FB",
    page_icon="🎬",
    layout="wide"
)

# 2. Styling UI Modern
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00e5ff, #ff7b00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}
.neon-bar {
    height: 3px;
    width: 100%;
    background: linear-gradient(90deg, #00e5ff 0%, #ff7b00 100%);
    border-radius: 4px;
    margin-top: 4px;
    margin-bottom: 16px;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
}
div[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header Studio
st.markdown('<div class="hero-title">🎬 JacS MEDIA STUDIO AI</div>', unsafe_allow_html=True)
st.caption("Generator Visual, Desain Feed/Story, dan Naskah Video Pendek untuk TikTok, Instagram & Facebook")
st.markdown('<div class="neon-bar"></div>', unsafe_allow_html=True)

# 4. Pengaturan API Key (Sidebar)
with st.sidebar:
    st.header("⚙️ Pengaturan Studio")
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if secret_key:
        api_key = secret_key
        st.success("✅ API Key Terhubung Otomatis")
    else:
        api_key = st.text_input("Masukkan Gemini API Key:", type="password")
        st.markdown("[Dapatkan API Key di Google AI Studio](https://aistudio.google.com/)")

# Manajemen Sesi Data Hasil
if "res_img_bytes" not in st.session_state:
    st.session_state.res_img_bytes = None
if "res_text_content" not in st.session_state:
    st.session_state.res_text_content = ""
if "uploaded_preview" not in st.session_state:
    st.session_state.uploaded_preview = None

# Generator File Unduhan
def generate_docx(content_text):
    doc = docx.Document()
    doc.add_heading("Naskah & Panduan Produksi Konten - JacS Studio", level=1)
    for paragraph in content_text.split("\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()

def generate_pdf(content_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, text="Naskah & Panduan Konten Medsos - JacS Studio", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    for line in content_text.split("\n"):
        safe_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
        if safe_line:
            pdf.multi_cell(0, 6, text=safe_line)
            pdf.ln(1)
    return bytes(pdf.output())

# 5. Form Input & Parameter Studio
col_in1, col_in2 = st.columns([1.8, 1.2], gap="large")

with col_in1:
    with st.container(border=True):
        st.markdown("#### 📝 Konsep & Rencana Konten")
        c1, c2, c3 = st.columns(3)
        with c1:
            platform = st.selectbox("Platform Target:", ["TikTok", "Instagram Reels / Story", "Instagram Feed", "Facebook Post"])
        with c2:
            aspek_rasio = st.selectbox("Format Ukuran:", ["9:16 (Vertikal - TikTok/Reels)", "1:1 (Persegi - Feed)", "16:9 (Landscape - Banner/FB)"])
        with c3:
            gaya_visual = st.selectbox("Gaya Visual Gambar:", ["Fotorealistik Modern", "3D Karakter Animasi", "Poster Desain Minimalis", "Sinematik Berkelas"])

        topik_konten = st.text_area(
            "Deskripsi Konten / Produk / Acara:",
            placeholder="Contoh: 'Promosi kegiatan literasi sekolah ramah anak dan seru bagi siswa baru, tampilkan kesan ceria dan penuh semangat'",
            height=90
        )

        uploaded_file = st.file_uploader(
            "📎 Unggah Dokumen Rujukan / Foto Logo (Opsional):",
            type=["jpg", "jpeg", "png", "webp", "txt", "docx"],
            help="Unggah foto atau dokumen materi untuk dianalisis oleh AI."
        )

        btn_generate = st.button("⚡ Hasilkan Desain Visual & Naskah Lengkap", use_container_width=True)

with col_in2:
    with st.container(border=True):
        st.markdown("#### 💡 Tips Kreator Medsos")
        st.markdown("""
        * **TikTok / Reels (9:16):** Prioritaskan *Hook* 3 detik pertama dengan gerakan dinamis dan teks tebal di layar.
        * **Instagram Feed (1:1):** Komposisi visual fokus pada warna cerah dan teks yang tidak terlalu padat.
        * **AI Video Generator:** Salin prompt bahasa Inggris yang dihasilkan ke pembuat video AI (seperti Kling AI, Luma Dream Machine, atau Runway) untuk menganimasikan visual.
        """)

# 6. Pemrosesan AI saat Tombol Ditekan
if btn_generate:
    if not api_key:
        st.error("⚠️ Masukkan Gemini API Key di menu samping terlebih dahulu.")
    elif not topik_konten and not uploaded_file:
        st.warning("⚠️ Silakan ketik deskripsi konten atau unggah berkas rujukan terlebih dahulu.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            st.session_state.res_img_bytes = None
            st.session_state.res_text_content = ""
            st.session_state.uploaded_preview = None

            ratio_dict = {
                "9:16 (Vertikal - TikTok/Reels)": "9:16",
                "1:1 (Persegi - Feed)": "1:1",
                "16:9 (Landscape - Banner/FB)": "16:9"
            }
            selected_ratio = ratio_dict.get(aspek_rasio, "1:1")

            sys_inst = (
                "Anda adalah Asisten Sutradara Kreatif & Pakar Pemasaran Media Sosial Viral (TikTok, Instagram, Facebook). "
                "Susun hook 3 detik yang memikat, naskah narasi, panduan teks di layar, alur kamera per adegan, "
                "rekomendasi musik/audio tren, tagar relevan, serta prompt teks-ke-video dalam Bahasa Inggris."
            )

            prompt_konten = f"Platform Target: {platform}\nFormat Rasio: {aspek_rasio}\nGaya Visual: {gaya_visual}\nDetail Konten: {topik_konten}\n\nSusun panduan konten video dan publikasi yang terperinci dan siap pakai:"
            contents_payload = [prompt_konten]

            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    st.session_state.uploaded_preview = file_bytes
                    mime = uploaded_file.type if uploaded_file.type else "image/jpeg"
                    contents_payload.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
                elif uploaded_file.name.lower().endswith('.docx'):
                    doc_read = docx.Document(io.BytesIO(file_bytes))
                    doc_txt = "\n".join([p.text for p in doc_read.paragraphs if p.text])
                    contents_payload.append(f"\n--- DOKUMEN ACUAN ---\n{doc_txt}")
                elif uploaded_file.name.lower().endswith('.txt'):
                    contents_payload.append(f"\n--- DOKUMEN ACUAN ---\n{file_bytes.decode('utf-8', errors='ignore')}")

            with st.spinner("⚡ Sedang merender visual desain dan menyusun naskah produksi..."):
                # A. Generate Gambar Desain (Imagen 3)
                try:
                    img_prompt = f"Professional social media graphic and photoshoot for {platform}, aesthetic: {gaya_visual}, theme: {topik_konten}, clean layout, hyper-detailed, 8k resolution"
                    img_res = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=img_prompt,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            aspect_ratio=selected_ratio
                        )
                    )
                    for g_img in img_res.generated_images:
                        st.session_state.res_img_bytes = g_img.image.image_bytes
                except Exception as err_img:
                    st.warning(f"Catatan render visual: {err_img}")

                # B. Generate Naskah & Storyboard Video (Gemini 2.5 Flash)
                txt_res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents_payload,
                    config={"system_instruction": sys_inst}
                )
                if txt_res and txt_res.text:
                    st.session_state.res_text_content = txt_res.text

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")

# 7. PRATINJAU HASIL & PUSAT UNDUH LENGKAP
if st.session_state.res_img_bytes or st.session_state.res_text_content:
    st.divider()
    st.markdown("### 🎨 PRATINJAU HASIL KREASI & PUSAT UNDUH")

    if st.session_state.uploaded_preview:
        with st.expander("📷 Lihat Berkas / Foto Acuan yang Anda Unggah", expanded=False):
            st.image(st.session_state.uploaded_preview, width=300)

    # Pusat Unduhan Berkas Naskah
    if st.session_state.res_text_content:
        st.markdown("##### 📥 Unduh Naskah & Panduan:")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            docx_data = generate_docx(st.session_state.res_text_content)
            st.download_button(
                label="📄 Unduh Naskah Word (.docx)",
                data=docx_data,
                file_name="Naskah_JacS_Media.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with col_d2:
            pdf_data = generate_pdf(st.session_state.res_text_content)
            st.download_button(
                label="📑 Unduh Naskah PDF (.pdf)",
                data=pdf_data,
                file_name="Naskah_JacS_Media.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_d3:
            st.download_button(
                label="📝 Unduh Teks Mentah (.txt)",
                data=st.session_state.res_text_content,
                file_name="Naskah_JacS_Media.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.write("")

    # Tab Pratinjau Interaktif
    tab_view1, tab_view2, tab_view3 = st.tabs(["🖼️ Pratinjau Gambar Visual", "📱 Naskah & Storyboard Video", "✏️ Edit Naskah"])

    with tab_view1:
        if st.session_state.res_img_bytes:
            col_v1, col_v2 = st.columns([2, 1])
            with col_v1:
                st.image(st.session_state.res_img_bytes, caption=f"Desain Siap Pakai ({aspek_rasio})", use_container_width=True)
            with col_v2:
                st.markdown("#### 💾 Unduh Gambar")
                st.write("Resolusi visual tinggi siap diunggah ke media sosial:")
                st.download_button(
                    label="💾 Unduh Gambar Desain (.png)",
                    data=st.session_state.res_img_bytes,
                    file_name=f"jacs_{platform.lower().replace(' ', '_')}.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            st.info("Render gambar sedang diproses atau tidak diminta.")

    with tab_view2:
        st.markdown(st.session_state.res_text_content)

    with tab_view3:
        st.caption("Ubah atau rapikan kalimat naskah langsung di bawah ini:")
        edited_naskah = st.text_area("Editor Teks:", value=st.session_state.res_text_content, height=350)
        if st.button("💾 Simpan Perubahan Teks", use_container_width=True):
            st.session_state.res_text_content = edited_naskah
            st.success("✅ Perubahan naskah tersimpan! Berkas Word & PDF otomatis diperbarui.")
            st.rerun()
