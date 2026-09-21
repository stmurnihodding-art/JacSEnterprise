import streamlit as st
from google import genai
from google.genai import types
import io
import docx
from fpdf import FPDF
from PIL import Image

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="JacS Media Studio AI - TikTok, IG & FB",
    page_icon="🎬",
    layout="wide"
)

# 2. Styling UI Neon Modern
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
    margin-top: 6px;
    margin-bottom: 16px;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Header & Identitas
st.markdown('<div class="hero-title">🎬 JacS MEDIA STUDIO AI</div>', unsafe_allow_html=True)
st.caption("Generator Visual, Desain Feed/Story, dan Naskah Video Pendek untuk TikTok, Instagram & Facebook")
st.markdown('<div class="neon-bar"></div>', unsafe_allow_html=True)

# 4. Pengaturan API Key
with st.sidebar:
    st.header("⚙️ Pengaturan Studio")
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if secret_key:
        api_key = secret_key
        st.success("✅ API Key Terhubung Otomatis")
    else:
        api_key = st.text_input("Masukkan Gemini API Key:", type="password")
        st.markdown("[Dapatkan API Key di Google AI Studio](https://aistudio.google.com/)")

# State Manajemen Sesi
if "result_text" not in st.session_state:
    st.session_state.result_text = ""
if "result_image" not in st.session_state:
    st.session_state.result_image = None

# Fungsi Generator Berkas Unduhan
def get_docx_download(text_content):
    doc = docx.Document()
    doc.add_heading("Naskah & Rencana Konten Medsos - JacS Media", level=1)
    for p in text_content.split("\n"):
        if p.strip():
            doc.add_paragraph(p.strip())
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()

def get_pdf_download(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, text="Naskah & Rencana Konten Medsos - JacS Media", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    for line in text_content.split("\n"):
        safe = line.strip().encode('latin-1', 'replace').decode('latin-1')
        if safe:
            pdf.multi_cell(0, 6, text=safe)
            pdf.ln(1)
    return bytes(pdf.output())

# 5. Formulir Input & Parameter Studio
col_main1, col_main2 = st.columns([1.8, 1.2], gap="large")

with col_main1:
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
            "Deskripsi Konten / Produk / Kampanye:",
            placeholder="Contoh: 'Promosi kegiatan literasi sekolah menyenangkan bagi siswa baru, tampilkan kesan ceria dan penuh semangat'",
            height=90
        )

        # FITUR UPLOAD FILE
        uploaded_file = st.file_uploader(
            "📎 Unggah Gambar Acuan / Logo / Dokumen Pendukung (Opsional):",
            type=["jpg", "jpeg", "png", "webp", "txt", "docx"],
            help="Unggah foto produk, logo, atau dokumen naskah yang ingin dirujuk oleh AI."
        )

        btn_generate = st.button("⚡ Hasilkan Desain & Naskah Lengkap", use_container_width=True)

with col_main2:
    with st.container(border=True):
        st.markdown("#### 💡 Tips Kreator Medsos")
        st.markdown("""
        * **TikTok / Reels (9:16):** Fokus pada *Hook* 3 detik pertama dengan gerakan dinamis dan teks tebal di layar.
        * **Instagram Feed (1:1):** Gunakan komposisi visual bersih dan tajam yang menarik perhatian saat di-*scroll*.
        * **AI Video Generator:** Salin prompt bahasa Inggris yang dihasilkan ke platform video (seperti Kling AI, Luma Dream Machine, atau Runway) untuk membuat animasi video.
        """)

# 6. Pemrosesan AI
if btn_generate:
    if not api_key:
        st.error("⚠️ Masukkan Gemini API Key di menu samping terlebih dahulu.")
    elif not topik_konten and not uploaded_file:
        st.warning("⚠️ Silakan tuliskan deskripsi topik konten atau unggah berkas terlebih dahulu.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            st.session_state.result_image = None
            st.session_state.result_text = ""

            ratio_map = {
                "9:16 (Vertikal - TikTok/Reels)": "9:16",
                "1:1 (Persegi - Feed)": "1:1",
                "16:9 (Landscape - Banner/FB)": "16:9"
            }
            selected_ratio = ratio_map.get(aspek_rasio, "1:1")

            # Persiapan Payload Teks & Berkas
            system_instruction = "Anda adalah Asisten Sutradara Kreatif & Ahli Pemasaran Media Sosial Viral (TikTok, Instagram, Facebook). Sajikan hook memikat, naskah narasi, instruksi kamera, tagar relevan, serta prompt teks-ke-video dalam bahasa Inggris."
            prompt_konten = f"Platform: {platform}\nGaya: {gaya_visual}\nTopik/Detail: {topik_konten}\n\nSusun naskah video dan rencana publikasi media sosial yang lengkap, terstruktur, dan siap diproduksi."

            text_payload = [prompt_konten]

            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    mime = uploaded_file.type if uploaded_file.type else "image/jpeg"
                    text_payload.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
                elif uploaded_file.name.lower().endswith('.docx'):
                    doc_preview = docx.Document(io.BytesIO(file_bytes))
                    doc_text = "\n".join([p.text for p in doc_preview.paragraphs if p.text])
                    text_payload.append(f"\n--- TEKS DOKUMEN ACUAN ---\n{doc_text}")
                elif uploaded_file.name.lower().endswith('.txt'):
                    text_payload.append(f"\n--- TEKS DOKUMEN ACUAN ---\n{file_bytes.decode('utf-8', errors='ignore')}")

            with st.spinner("Sedang merancang materi visual dan menyusun naskah video..."):
                # A. Generate Gambar Desain (Imagen 3)
                try:
                    img_prompt = f"Professional social media photography/poster for {platform}, theme: {topik_konten}, aesthetic: {gaya_visual}, ultra high quality, clean lighting, 8k"
                    img_resp = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=img_prompt,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            aspect_ratio=selected_ratio
                        )
                    )
                    for gen_img in img_resp.generated_images:
                        st.session_state.result_image = gen_img.image.image_bytes
                except Exception as img_err:
                    st.warning(f"Catatan gambar: {img_err}")

                # B. Generate Naskah & Storyboard Video (Gemini 2.5 Flash)
                teks_resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=text_payload,
                    config={"system_instruction": system_instruction}
                )
                if teks_resp and teks_resp.text:
                    st.session_state.result_text = teks_resp.text

        except Exception as err:
            st.error(f"Terjadi kesalahan saat memproses: {err}")

# 7. Tampilan Hasil, Editor Naskah, dan Pusat Unduh
if st.session_state.result_image or st.session_state.result_text:
    st.write("")
    st.markdown("### 🎨 HASIL KREASI STUDIO")

    # FITUR DOWNLOAD BERKAS LENGKAP
    if st.session_state.result_text:
        st.markdown("##### 📥 Pusat Unduh Naskah:")
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            docx_data = get_docx_download(st.session_state.result_text)
            st.download_button(
                label="📄 Unduh Naskah Word (.docx)",
                data=docx_data,
                file_name="Naskah_JacS_Media.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with d_col2:
            pdf_data = get_pdf_download(st.session_state.result_text)
            st.download_button(
                label="📑 Unduh Naskah PDF (.pdf)",
                data=pdf_data,
                file_name="Naskah_JacS_Media.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d_col3:
            st.download_button(
                label="📝 Unduh Teks (.txt)",
                data=st.session_state.result_text,
                file_name="Naskah_JacS_Media.txt",
                mime="text/plain",
                use_container_width=True
            )

    tab_res1, tab_res2, tab_res3 = st.tabs(["🖼️ Desain Visual Siap Pakai", "📝 Naskah & Storyboard", "✏️ Edit Naskah Langsung"])

    with tab_res1:
        if st.session_state.result_image:
            st.image(st.session_state.result_image, caption="Desain Visual Media Sosial Siap Pakai", use_container_width=True)
            st.download_button(
                label="💾 Unduh Desain Visual (PNG)",
                data=st.session_state.result_image,
                file_name="desain_jacs_media.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.info("Gambar belum dibuat atau deskripsi tidak memerlukan render visual.")

    with tab_res2:
        st.markdown(st.session_state.result_text)

    # FITUR EDIT LANGSUNG
    with tab_res3:
        st.caption("Anda dapat mengubah atau menambah poin naskah sebelum diekspor:")
        edited_text = st.text_area("Editor Naskah:", value=st.session_state.result_text, height=350)
        if st.button("💾 Simpan Perubahan Naskah", use_container_width=True):
            st.session_state.result_text = edited_text
            st.success("✅ Perubahan naskah disimpan! Berkas unduhan otomatis diperbarui.")
            st.rerun()
