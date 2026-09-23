import streamlit as st
from google import genai
from google.genai import types
import io
import docx
from fpdf import FPDF

# 1. Konfigurasi Halaman & Tema Responsif
st.set_page_config(
    page_title="JacS All-in-One AI Creative Studio Engine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Styling UI Mobile & Desktop Responsif
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.4rem, 4vw, 2.2rem);
    font-weight: 800;
    background: linear-gradient(90deg, #00e5ff, #ff7b00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
}
.neon-bar {
    height: 3px;
    width: 100%;
    background: linear-gradient(90deg, #00e5ff 0%, #ff7b00 100%);
    border-radius: 4px;
    margin-top: 4px;
    margin-bottom: 16px;
}
.stButton > button, div[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}
.preview-empty-box {
    border: 2px dashed rgba(0, 229, 255, 0.35);
    border-radius: 10px;
    padding: 30px 15px;
    text-align: center;
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.02);
    margin-top: 10px;
}
@media (max-width: 768px) {
    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 3. Header Studio
st.markdown('<div class="hero-title">🎬 JacS ALL-IN-ONE AI CREATIVE STUDIO ENGINE</div>', unsafe_allow_html=True)
st.caption("Mesin Produksi Konten Terpadu: Konsistensi Karakter, Branding Mockup, Food Commercial, & Story Video")
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

# Manajemen Sesi Data
if "res_img" not in st.session_state:
    st.session_state.res_img = None
if "res_text" not in st.session_state:
    st.session_state.res_text = ""
if "ref_img_preview" not in st.session_state:
    st.session_state.ref_img_preview = None
if "active_module_name" not in st.session_state:
    st.session_state.active_module_name = "Character Gen"

# Generator Unduhan Berkas
def generate_docx(content_text, title="Naskah Produksi AI Studio"):
    doc = docx.Document()
    doc.add_heading(title, level=1)
    for p in content_text.split("\n"):
        if p.strip():
            doc.add_paragraph(p.strip())
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()

def generate_pdf(content_text, title="Naskah Produksi AI Studio"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(4)
    for line in content_text.split("\n"):
        safe_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
        if safe_line:
            pdf.multi_cell(0, 6, text=safe_line)
            pdf.ln(1)
    return bytes(pdf.output())

# 5. Tab Pemilihan 4 Modul Alur Kerja
tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
    "👤 Modul 1: Karakter Konsisten",
    "🏷️ Modul 2: Branding & Mockup",
    "🍜 Modul 3: Kuliner & Food Gen",
    "🎥 Modul 4: Story Video & Film Engine"
])

# MODUL 1: CHARACTER GEN
with tab_m1:
    with st.container(border=True):
        st.markdown("##### 👤 Modul 1: Consistent Persona & Face Embedding")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            m1_name = st.text_input("Nama / ID Karakter:", value="Rina_Protagonist")
        with col_c2:
            m1_style = st.selectbox("Gaya Seni:", ["Photorealistic 8K", "Cinematic Film Still", "3D Pixar Animation", "Vintage Retro"], key="m1_s")
        with col_c3:
            m1_ratio = st.selectbox("Rasio Frame:", ["9:16 (Vertikal)", "1:1 (Persegi)", "16:9 (Landscape)"], key="m1_r")

        m1_details = st.text_area("Ciri Fisik, Usia, Ekspresi & Pakaian:", "Wanita usia 25 tahun, rambut hitam sebahu, tatapan fokus percaya diri, blazer navy modern, pencahayaan studio lembut.", height=70)
        m1_files = st.file_uploader("📷 Unggah Foto Acuan Wajah Asli / Karakter (1-3 Foto):", type=["jpg", "png", "webp"], accept_multiple_files=True, key="m1_up")
        btn_m1 = st.button("🚀 Generate", key="btn_gen_m1", use_container_width=True)

# MODUL 2: BRANDING & COMMERCIAL MOCKUP
with tab_m2:
    with st.container(border=True):
        st.markdown("##### 🏷️ Modul 2: Commercial Mockup & Model Ads")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            m2_brand = st.text_input("Nama Brand & Tagline:", value="Kopi Senja - Aroma Otentik")
        with col_b2:
            m2_vibe = st.selectbox("Vibe / Suasana Iklan:", ["Luxury Minimalist", "Modern Coffee Shop", "Outdoor Nature Adventure", "Neon Cyberpunk Cafe"], key="m2_v")
        with col_b3:
            m2_ratio = st.selectbox("Format Kampanye:", ["9:16 (Story/TikTok)", "1:1 (Feed IG)", "16:9 (Banner Ad)"], key="m2_r")

        m2_desc = st.text_area("Deskripsi Interaksi Model & Produk:", "Model wanita muda memegang botol cold brew kaca dengan senyum santai, latar belakang meja marmer dan tanaman hias.", height=70)
        m2_prod_file = st.file_uploader("📎 Unggah Logo Transparan (PNG) atau Foto Kemasan Produk:", type=["png", "jpg", "webp"], key="m2_up")
        btn_m2 = st.button("🚀 Generate", key="btn_gen_m2", use_container_width=True)

# MODUL 3: CULINARY & FOOD GEN
with tab_m3:
    with st.container(border=True):
        st.markdown("##### 🍜 Modul 3: High-End Food & Beverage Photography")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            m3_dish = st.text_input("Nama Menu Hidangan:", value="Nasi Rawon Daging Sapi Premium")
        with col_f2:
            m3_angle = st.selectbox("Sudut Kamera:", ["Top-Down / Flat Lay (90°)", "Macro Close-Up (Tekstur)", "45° Eye-Level Resto", "Side-Profile Hero Shot"], key="m3_a")
        with col_f3:
            m3_ratio = st.selectbox("Rasio Foto Menu:", ["1:1 (Feed Katalog)", "9:16 (Reels/TikTok)", "16:9 (Website Banner)"], key="m3_r")

        m3_details = st.text_area("Detail Visual (Uap Panas, Tekstur, Garnish, Piring/Meja):", "Kuah hitam pekat berkilau gurih, potongan daging empuk beruap panas, taburan tauge pendek renyah, sambal terasi dan telur asin di piring tembikar rustic meja kayu.", height=70)
        m3_sample = st.file_uploader("📎 Unggah Foto Referensi Sajian Asli (Opsional):", type=["png", "jpg", "webp"], key="m3_up")
        btn_m3 = st.button("🚀 Generate", key="btn_gen_m3", use_container_width=True)

# MODUL 4: STORY VIDEO & FILM ENGINE
with tab_m4:
    with st.container(border=True):
        st.markdown("##### 🎥 Modul 4: Multi-Scene Story Video Engine")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            m4_char = st.text_input("Karakter Utama:", value="Rina_Protagonist")
        with col_s2:
            m4_genre = st.selectbox("Genre / Mood:", ["Inspiratif & Emosional", "Komedi Situasi Ringan", "Thriller / Aksi Sinematik", "Edukatif Dokumenter"], key="m4_g")
        with col_s3:
            m4_ratio = st.selectbox("Rasio Video:", ["9:16 (TikTok/Reels)", "16:9 (YouTube/Film)"], key="m4_r")

        m4_premise = st.text_area("Premis Cerita / Naskah Adegan:", "Seorang guru muda yang menemukan metode mengajar interaktif baru untuk membangkitkan semangat siswanya yang sedang putus asa.", height=70)
        m4_ref_doc = st.file_uploader("📎 Unggah File Naskah / Kerangka Cerita (Word / PDF / Teks):", type=["docx", "txt", "pdf"], key="m4_up")
        btn_m4 = st.button("🚀 Generate", key="btn_gen_m4", use_container_width=True)

# 6. Pemrosesan Logika Berdasarkan Modul
active_trigger = btn_m1 or btn_m2 or btn_m3 or btn_m4

if active_trigger:
    if not api_key:
        st.error("⚠️ Masukkan Gemini API Key di menu samping terlebih dahulu.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            st.session_state.res_img = None
            st.session_state.res_text = ""
            st.session_state.ref_img_preview = None

            if btn_m1:
                st.session_state.active_module_name = f"Modul 1: Karakter {m1_name}"
                target_ratio = "9:16" if "9:16" in m1_ratio else ("16:9" if "16:9" in m1_ratio else "1:1")
                img_prompt = f"Cinematic studio character portrait of {m1_name}, {m1_details}, style: {m1_style}, ultra detailed facial features, realistic skin texture, 8k resolution, identity preserved"
                sys_inst = "Anda adalah Master Director & Pakar Prompt Karakter Konsisten. Rinci profil identitas karakter, rumus prompt text-to-image konsisten, serta seed guidelines."
                analysis_prompt = f"Kunci profil karakter {m1_name} dengan gaya {m1_style}. Rincikan formula prompt konsisten (Image-to-Image & Text-to-Video) dan panduan pose untuk adegan berikutnya."
                active_files = m1_files

            elif btn_m2:
                st.session_state.active_module_name = f"Modul 2: Branding {m2_brand}"
                target_ratio = "9:16" if "9:16" in m2_ratio else ("16:9" if "16:9" in m2_ratio else "1:1")
                img_prompt = f"High-end commercial advertisement for {m2_brand}, {m2_desc}, aesthetic: {m2_vibe}, studio lighting, clean composition, luxury product photography, 8k"
                sys_inst = "Anda adalah Creative Advertising Director. Buat panduan eksekusi kampanye, penempatan logo/mockup, serta salinan copywriting iklan media sosial viral."
                analysis_prompt = f"Susun rencana iklan komersial untuk brand {m2_brand}. Sertakan arahan layer penempatan logo, headline iklan, caption medsos, dan prompt video komersial 15 detik."
                active_files = [m2_prod_file] if m2_prod_file else []

            elif btn_m3:
                st.session_state.active_module_name = f"Modul 3: Kuliner {m3_dish}"
                target_ratio = "1:1" if "1:1" in m3_ratio else ("9:16" if "9:16" in m3_ratio else "16:9")
                img_prompt = f"Commercial food photography of {m3_dish}, camera angle: {m3_angle}, {m3_details}, soft studio lighting, glistening appetizing textures, shallow depth of field, 8k resolution"
                sys_inst = "Anda adalah Food Stylist & Fotografer Kuliner Komersial Kelas Dunia. Buat deskripsi menu, narasi selera, serta formula prompt fotografi makro."
                analysis_prompt = f"Rancang panduan visual dan narasi marketing untuk menu kuliner: {m3_dish}. Sudut: {m3_angle}. Rincikan highlight uap, tekstur, dan copywriting menggugah selera."
                active_files = [m3_sample] if m3_sample else []

            else:
                st.session_state.active_module_name = f"Modul 4: Film Engine ({m4_char})"
                target_ratio = "9:16" if "9:16" in m4_ratio else "16:9"
                img_prompt = f"Cinematic keyframe scene 1 for film, featuring {m4_char}, premise: {m4_premise}, mood: {m4_genre}, volumetric lighting, 24fps film aesthetic, master shot"
                sys_inst = "Anda adalah Sutradara & Showrunner Serial Profesional. Lakukan script breakdown per adegan (Scene 1-4), naskah dialog TTS, instruksi kamera, serta prompt siap pakai untuk AI Video (Runway Gen-3 / Kling)."
                analysis_prompt = f"Pecah premis ini menjadi naskah 3-4 adegan: {m4_premise}. Karakter: {m4_char}. Genre: {m4_genre}. Format: Scene, Visual Frame, Voiceover/Dialog TTS, BGM/SFX, dan English Prompt siap salin untuk Kling/Luma."
                active_files = [m4_ref_doc] if m4_ref_doc else []

            # Siapkan Payload Analisis
            payload = [analysis_prompt]
            for f in active_files:
                if f is not None:
                    fb = f.getvalue()
                    if f.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        st.session_state.ref_img_preview = fb
                        payload.append(types.Part.from_bytes(data=fb, mime_type=f.type or "image/jpeg"))
                    elif f.name.lower().endswith('.docx'):
                        doc_r = docx.Document(io.BytesIO(fb))
                        payload.append("\n--- DOKUMEN ACUAN ---\n" + "\n".join([p.text for p in doc_r.paragraphs if p.text]))
                    elif f.name.lower().endswith('.txt'):
                        payload.append("\n--- DOKUMEN ACUAN ---\n" + fb.decode('utf-8', errors='ignore'))

            with st.spinner("⚡ Engine sedang merender visual keyframe dan menyusun rencana produksi..."):
                # A. Render Keyframe Visual (Imagen 3)
                try:
                    img_res = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=img_prompt,
                        config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=target_ratio)
                    )
                    for g in img_res.generated_images:
                        st.session_state.res_img = g.image.image_bytes
                except Exception as img_err:
                    st.warning(f"Catatan visual render: {img_err}")

                # B. Eksekusi Naskah & Prompt AI Video (Gemini 2.5 Flash)
                txt_res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=payload,
                    config={"system_instruction": sys_inst}
                )
                if txt_res and txt_res.text:
                    st.session_state.res_text = txt_res.text

        except Exception as e:
            st.error(f"Gagal memproses alur kerja: {e}")

# 7. Area Preview & Pusat Unduhan
st.divider()
if st.session_state.res_img or st.session_state.res_text:
    st.markdown(f"### 🎨 PREVIEW: {st.session_state.active_module_name}")

    if st.session_state.ref_img_preview:
        with st.expander("📷 Lihat Aset Acuan yang Diunggah", expanded=False):
            st.image(st.session_state.ref_img_preview, width=260)

    # Pusat Unduhan Naskah
    if st.session_state.res_text:
        st.markdown("##### 📥 Pusat Unduh Panduan & Naskah:")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "📄 Unduh Dokumen Word (.docx)",
                data=generate_docx(st.session_state.res_text, st.session_state.active_module_name),
                file_name=f"{st.session_state.active_module_name.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with d2:
            st.download_button(
                "📑 Unduh Dokumen PDF (.pdf)",
                data=generate_pdf(st.session_state.res_text, st.session_state.active_module_name),
                file_name=f"{st.session_state.active_module_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d3:
            st.download_button(
                "📝 Unduh Teks Mentah (.txt)",
                data=st.session_state.res_text,
                file_name=f"{st.session_state.active_module_name.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.write("")
    pv1, pv2, pv3 = st.tabs(["🖼️ Preview Visual", "📱 Storyboard / Naskah Adegan", "✏️ Edit Naskah"])

    with pv1:
        if st.session_state.res_img:
            cv1, cv2 = st.columns([1.8, 1.2], gap="medium")
            with cv1:
                st.image(st.session_state.res_img, caption="Keyframe Visual Siap Pakai", use_container_width=True)
            with cv2:
                st.markdown("#### 💾 Simpan Visual")
                st.caption("Gambar resolusi tinggi siap diunggah atau dijadikan acuan Image-to-Video di Kling/Runway:")
                st.download_button(
                    "💾 Unduh Gambar PNG",
                    data=st.session_state.res_img,
                    file_name=f"render_{st.session_state.active_module_name.lower().replace(' ', '_')}.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            st.info("Visual render tidak diminta atau sedang disiapkan.")

    with pv2:
        st.markdown(st.session_state.res_text)

    with pv3:
        st.caption("Ubah prompt atau dialog naskah di bawah ini sebelum mengunduh:")
        edited_txt = st.text_area("Editor Teks:", value=st.session_state.res_text, height=320)
        if st.button("💾 Simpan Perubahan Naskah", use_container_width=True):
            st.session_state.res_text = edited_txt
            st.success("✅ Perubahan tersimpan! Berkas Word & PDF otomatis diperbarui.")
            st.rerun()

else:
    st.markdown("""
    <div class="preview-empty-box">
        <h4>⚡ Preview & Pascaproduksi</h4>
        <p>Pilih salah satu dari 4 modul di atas, lengkapi parameter atau aset gambar, lalu klik tombol Generate. Hasil render visual resolusi tinggi dan naskah produksi siap unduh akan tampil di sini.</p>
    </div>
    """, unsafe_allow_html=True)
