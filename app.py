import streamlit as st
from google import genai
from google.genai import types
import io
import time
import urllib.parse
import urllib.request
import docx
from fpdf import FPDF

# 1. Konfigurasi Halaman & Tema Responsif
st.set_page_config(
    page_title="JacS AI Creative - Workspace Image & Video",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Desain UI Glassmorphism & Neon Studio Interaktif
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.6rem, 4.5vw, 2.4rem);
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #00e5ff 0%, #7928ca 50%, #ff7b00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}
.hero-subtitle {
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #64748b;
    margin-top: 2px;
    margin-bottom: 8px;
}
.neon-divider {
    height: 2px;
    width: 100%;
    background: linear-gradient(90deg, #00e5ff 0%, rgba(121,40,202,0.8) 50%, transparent 100%);
    border-radius: 4px;
    margin-bottom: 18px;
}

div[data-testid="stTabs"] button[role="tab"] {
    border-radius: 20px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin-right: 8px !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 229, 255, 0.15), rgba(121, 40, 202, 0.25)) !important;
    border: 1px solid #00e5ff !important;
    color: #00e5ff !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(0, 229, 255, 0.2) !important;
    border-radius: 14px !important;
    background: rgba(15, 23, 42, 0.45) !important;
    backdrop-filter: blur(12px) !important;
    padding: 16px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
}

.stButton > button {
    background: linear-gradient(90deg, #00e5ff 0%, #ff7b00 100%) !important;
    color: #050505 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    min-height: 48px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.5) !important;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
    border: 1px solid rgba(0, 229, 255, 0.4) !important;
}

.preview-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 14px;
}
.preview-mini-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.preview-mini-card h5 {
    color: #00e5ff;
    margin-bottom: 4px;
    font-size: 0.95rem;
}
.preview-mini-card p {
    font-size: 0.8rem;
    color: #94a3b8;
    margin: 0;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 3. Header Studio
st.markdown('<div class="hero-title">🎬 JacS AI CREATIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Workspace Image & Video Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

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

# Helper Dimensi Aspek Rasio
def get_dimensions(raw_ratio_str):
    if "9:16" in raw_ratio_str:
        return 720, 1280, "9:16"
    elif "16:9" in raw_ratio_str or "21:9" in raw_ratio_str:
        return 1280, 720, "16:9"
    elif "4:5" in raw_ratio_str or "3:4" in raw_ratio_str:
        return 800, 1000, "4:3"
    return 1024, 1024, "1:1"

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

# 5. Tab Pemilihan Modul
tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
    "👤 Karakter Konsisten",
    "🏷️ Branding & Mockup",
    "🍜 Kuliner & Food",
    "🎥 Story Video & Film"
])

# MODUL 1: CHARACTER GEN
with tab_m1:
    with st.container(border=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            char_preset = st.selectbox(
                "Pilih / Buat Profil Karakter:",
                ["Rina_Protagonist (Wanita Muda)", "Kenji_Explorer (Pria Petualang)", "Maya_Creator (Kreator Digital)", "Budi_Teacher (Guru Inspiratif)", "Kakek_Aris (Sesepuh Bijak)", "Kustom Nama / ID Sendiri..."],
                key="m1_char_preset"
            )
            if "Kustom" in char_preset:
                m1_name = st.text_input("Ketik Nama ID Baru:", value="Karakter_Saya", key="m1_custom_id")
            else:
                m1_name = char_preset.split(" ")[0]

        with col_c2:
            m1_style = st.selectbox(
                "Gaya Visual:",
                [
                    "Photorealistic 8K Studio Portrait",
                    "High-Fashion Editorial",
                    "Cinematic Film Still (35mm)",
                    "3D Pixar Animation Style",
                    "Makoto Shinkai Anime Aesthetic",
                    "Cyberpunk Neo-Tokyo",
                    "Vintage 90s Polaroid Grain",
                    "Renaissance Oil Painting"
                ],
                key="m1_s"
            )
        with col_c3:
            m1_ratio = st.selectbox(
                "Rasio Layar:",
                [
                    "9:16 (Vertikal - TikTok/Reels)",
                    "1:1 (Persegi - Feed Instagram)",
                    "4:5 (Portrait - Feed Medsos)",
                    "16:9 (Landscape - YouTube/PC)",
                    "3:4 (Portrait Klasik)"
                ],
                key="m1_r"
            )

        m1_details = st.text_area(
            "Ciri Fisik, Usia, Ekspresi & Busana:",
            "Wanita usia 25 tahun, rambut hitam sebahu, tatapan fokus percaya diri, blazer navy modern, pencahayaan studio lembut.",
            height=70,
            key="m1_details_in"
        )
        m1_files = st.file_uploader("📷 Unggah Foto Acuan Wajah / Karakter (1-3 Foto):", type=["jpg", "png", "webp"], accept_multiple_files=True, key="m1_up")
        btn_m1 = st.button("🚀 Generate Karakter", key="btn_gen_m1", use_container_width=True)

# MODUL 2: BRANDING & MOCKUP
with tab_m2:
    with st.container(border=True):
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            m2_brand = st.text_input("Nama Brand & Tagline:", value="Kopi Senja - Aroma Otentik", key="m2_brand_in")
        with col_b2:
            m2_vibe = st.selectbox(
                "Suasana & Vibe Iklan:",
                [
                    "Luxury Minimalist Studio",
                    "Aesthetic Korean Warm Cafe",
                    "Modern Urban Co-working",
                    "Tropical Nature & Outdoor Sunshine",
                    "Cyberpunk Neon Night",
                    "Clean Scandinavian Lifestyle",
                    "Retro 80s Vintage Diner",
                    "Vibrant Pop-Art Bold Colors"
                ],
                key="m2_v"
            )
        with col_b3:
            m2_ratio = st.selectbox(
                "Format Kampanye:",
                [
                    "9:16 (Story / TikTok / Reels Ad)",
                    "1:1 (Feed Post Standar)",
                    "4:5 (Instagram Portrait Boost)",
                    "16:9 (Website Hero Banner / FB Ad)",
                    "21:9 (Ultrawide Billboard / Display)"
                ],
                key="m2_r"
            )

        m2_desc = st.text_area(
            "Interaksi Model & Produk:",
            "Model wanita muda memegang botol cold brew kaca dengan senyum santai, latar meja marmer dan tanaman hias.",
            height=70,
            key="m2_desc_in"
        )
        m2_prod_file = st.file_uploader("📎 Unggah Logo Transparan (PNG) / Kemasan Produk:", type=["png", "jpg", "webp"], key="m2_up")
        btn_m2 = st.button("🚀 Generate Mockup & Iklan", key="btn_gen_m2", use_container_width=True)

# MODUL 3: KULINER & FOOD GEN
with tab_m3:
    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            m3_dish = st.text_input("Nama Hidangan / Minuman:", value="Coto Makassar Legendaris Daging Sapi", key="m3_dish_in")
        with col_f2:
            m3_angle = st.selectbox(
                "Sudut Kamera (Angle):",
                [
                    "Top-Down Flat Lay (90° overhead shot)",
                    "Macro Extreme Close-Up on textures and garnish",
                    "45-degree restaurant eye-level hero shot",
                    "Side-profile depth of field shot",
                    "Low-Angle dramatic commercial view"
                ],
                key="m3_a"
            )
        with col_f3:
            m3_ratio = st.selectbox(
                "Rasio Foto:",
                [
                    "9:16 (Story / Reels / TikTok F&B)",
                    "1:1 (Katalog Menu / Feed IG)",
                    "4:5 (Portrait Feed Instagram)",
                    "16:9 (Website Header / Banner Resto)"
                ],
                key="m3_r"
            )

        m3_details = st.text_area(
            "Detail Visual (Uap Panas, Garnish, Piring & Meja):",
            "Mangkuk berisi kuah kaldu rempah cokelat gurih dengan potongan daging sapi empuk, taburan daun bawang iris segar dan bawang goreng keemasan di atasnya. Di samping mangkuk ada irisan jeruk nipis segar berbulir, sambal tauco merah, dan potongan ketupat anyaman daun kelapa di atas meja kayu rustic bertekstur hangat dengan pencahayaan studio F&B profesional.",
            height=85,
            key="m3_details_in"
        )
        m3_sample = st.file_uploader("📎 Unggah Foto Referensi Hidangan (Opsional):", type=["png", "jpg", "webp"], key="m3_up")
        btn_m3 = st.button("🚀 Generate Foto Kuliner", key="btn_gen_m3", use_container_width=True)

# MODUL 4: STORY VIDEO & FILM ENGINE
with tab_m4:
    with st.container(border=True):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            m4_char = st.text_input("Karakter Utama:", value=m1_name, key="m4_char_in")
        with col_s2:
            m4_genre = st.selectbox(
                "Genre & Nuansa Film:",
                [
                    "Inspiratif & Emosional",
                    "Komedi Situasi Hangat & Ringan",
                    "Thriller & Aksi Sinematik",
                    "Dokumenter Realistis & Alam",
                    "Sci-Fi & Cyberpunk Futuristik",
                    "Romansa Puitis Senja",
                    "Misteri & Horor Psikologis",
                    "Iklan Naratif Komersial Cepat"
                ],
                key="m4_g"
            )
        with col_s3:
            m4_ratio = st.selectbox(
                "Format Video:",
                [
                    "9:16 (TikTok / Instagram Reels / Shorts)",
                    "16:9 (YouTube Standard / Bioskop)",
                    "1:1 (Instagram Feed Video)",
                    "4:5 (Medsos In-Feed Video)",
                    "21:9 (Anamorphic Cinema Scope)"
                ],
                key="m4_r"
            )

        m4_premise = st.text_area(
            "Premis Cerita / Naskah Adegan:",
            "Seorang guru muda yang menemukan metode mengajar interaktif baru untuk membangkitkan semangat siswanya yang sedang putus asa.",
            height=70,
            key="m4_premise_in"
        )
        m4_ref_doc = st.file_uploader("📎 Unggah File Naskah (Word / PDF / Teks):", type=["docx", "txt", "pdf"], key="m4_up")
        btn_m4 = st.button("🚀 Generate Story Video", key="btn_gen_m4", use_container_width=True)

# 6. Pemrosesan Logika Engine
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
                w_px, h_px, target_ratio = get_dimensions(m1_ratio)
                img_prompt_raw = f"High-end studio portrait of {m1_name}, {m1_details}, visual style: {m1_style}, ultra-realistic face, 8k resolution, cinematic lighting, masterpiece photography"
                sys_inst = "Anda adalah Master Director & Pakar Prompt Karakter Konsisten. Rinci profil identitas karakter, formula prompt konsisten (Image-to-Image & Text-to-Video), serta seed guidelines."
                analysis_prompt = f"Kunci profil karakter {m1_name} dengan gaya {m1_style}. Rasio: {m1_ratio}. Rincikan formula prompt konsisten lintas adegan dan panduan pose."
                active_files = m1_files

            elif btn_m2:
                st.session_state.active_module_name = f"Modul 2: Branding {m2_brand}"
                w_px, h_px, target_ratio = get_dimensions(m2_ratio)
                img_prompt_raw = f"Commercial product advertisement photograph for {m2_brand}, {m2_desc}, environment: {m2_vibe}, studio lighting, clean luxury composition, 8k commercial photography"
                sys_inst = "Anda adalah Creative Advertising Director. Buat panduan eksekusi kampanye, penempatan logo/mockup tanpa distorsi, serta salinan copywriting iklan media sosial viral."
                analysis_prompt = f"Susun kampanye iklan untuk brand {m2_brand}. Suasana: {m2_vibe}, Format: {m2_ratio}. Sertakan arahan penempatan logo, headline, caption medsos, dan prompt video iklan 15 detik."
                active_files = [m2_prod_file] if m2_prod_file else []

            elif btn_m3:
                st.session_state.active_module_name = f"Modul 3: Kuliner {m3_dish}"
                w_px, h_px, target_ratio = get_dimensions(m3_ratio)
                img_prompt_raw = f"Award-winning commercial food photography of Indonesian Coto Makassar beef soup in a traditional authentic clay bowl, tender beef pieces in rich spiced brown broth, garnished with fresh sliced spring onions and crispy fried shallots, side of lime wedges, sambal, ketupat rice cake on rustic dark wood table, camera angle: {m3_angle}, warm culinary softbox lighting, shallow depth of field, 8k resolution, appetizing, photorealistic Michelin dining"
                sys_inst = "Anda adalah Food Stylist & Fotografer Kuliner Komersial Kelas Dunia. Buat deskripsi menu, narasi selera, serta formula prompt fotografi makro."
                analysis_prompt = f"Rancang panduan visual dan narasi marketing untuk menu kuliner: {m3_dish}. Sudut kamera: {m3_angle}. Format: {m3_ratio}. Rincikan highlight uap, tekstur gurih, dan copywriting menggugah selera."
                active_files = [m3_sample] if m3_sample else []

            else:
                st.session_state.active_module_name = f"Modul 4: Film Engine ({m4_char})"
                w_px, h_px, target_ratio = get_dimensions(m4_ratio)
                img_prompt_raw = f"Cinematic film keyframe featuring {m4_char}, premise: {m4_premise}, mood: {m4_genre}, 35mm lens, volumetric cinematic lighting, 24fps movie still, ultra realistic"
                sys_inst = "Anda adalah Sutradara & Showrunner Serial Profesional. Lakukan script breakdown per adegan (Scene 1-4), naskah dialog TTS, instruksi kamera, serta prompt siap pakai untuk AI Video (Runway Gen-3 / Kling)."
                analysis_prompt = f"Pecah premis ini menjadi naskah 3-4 adegan: {m4_premise}. Karakter: {m4_char}. Genre: {m4_genre}. Format Video: {m4_ratio}. Format output: Scene, Visual Frame, Voiceover/Dialog TTS, BGM/SFX, dan English Prompt siap salin untuk Kling/Luma."
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

            with st.spinner("⚡ Engine sedang merender teks dan visual presisi tinggi..."):
                # A. Eksekusi Naskah dengan 5 Lapis Model Gemini Aktif
                candidate_models = [
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-flash",
                    "gemini-1.5-pro",
                    "gemini-2.0-flash",
                    "gemini-3.6-flash"
                ]

                success = False
                last_error_msg = ""

                for model_name in candidate_models:
                    try:
                        txt_res = client.models.generate_content(
                            model=model_name,
                            contents=payload,
                            config={"system_instruction": sys_inst}
                        )
                        if txt_res and txt_res.text:
                            st.session_state.res_text = txt_res.text
                            success = True
                            break
                    except Exception as err_layer:
                        last_error_msg = str(err_layer)
                        time.sleep(1.0)
                        continue

                if not success:
                    st.error(f"⚠️ Seluruh 5 jalur model Gemini sedang sibuk: {last_error_msg}")

                # B. Render Visual Presisi Tinggi (Imagen 3 -> Fallback Model Flux Photorealism)
                try:
                    img_res = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=img_prompt_raw,
                        config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=target_ratio)
                    )
                    if img_res and hasattr(img_res, 'generated_images'):
                        for g in img_res.generated_images:
                            st.session_state.res_img = g.image.image_bytes
                except Exception:
                    # Fallback ke Engine Flux dengan parameter photorealism
                    try:
                        encoded_prompt = urllib.parse.quote(img_prompt_raw)
                        poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w_px}&height={h_px}&model=flux-realism&nologo=true&enhance=true"
                        req = urllib.request.Request(poll_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=20) as resp:
                            st.session_state.res_img = resp.read()
                    except Exception:
                        pass

        except Exception as e:
            st.error(f"Gagal memproses alur kerja: {e}")

# 7. Area Preview & Ekspor
st.write("")
st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

if st.session_state.res_img or st.session_state.res_text:
    st.markdown(f"### 🎨 PREVIEW HASIL: {st.session_state.active_module_name}")

    if st.session_state.ref_img_preview:
        with st.expander("📷 Lihat Aset Acuan yang Diunggah", expanded=False):
            st.image(st.session_state.ref_img_preview, width=260)

    # Pusat Unduh Naskah
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
    pv1, pv2, pv3 = st.tabs(["🖼️ Preview Visual Langsung", "📱 Storyboard / Naskah Adegan", "✏️ Edit Naskah"])

    with pv1:
        if st.session_state.res_img:
            cv1, cv2 = st.columns([1.8, 1.2], gap="medium")
            with cv1:
                st.image(st.session_state.res_img, caption="Keyframe Visual Presisi (Photorealistic)", use_container_width=True)
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
            st.info("ℹ️ Sedang menyiapkan visual atau visual tidak dapat diakses.")

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
    <div style="border: 1px dashed rgba(0, 229, 255, 0.3); border-radius: 12px; padding: 24px 16px; background: rgba(15, 23, 42, 0.3);">
        <h4 style="color: #00e5ff; margin-bottom: 6px; text-align: center;">⚡ Preview & Pascaproduksi</h4>
        <p style="text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px;">
            Pilih salah satu dari 4 modul kreatif di atas, masukkan parameter atau aset visual, lalu klik tombol <b>Generate</b>.
        </p>
        <div class="preview-card-grid">
            <div class="preview-mini-card">
                <h5>👤 Karakter</h5>
                <p>Preset profil persona & 8 variasi seni visual.</p>
            </div>
            <div class="preview-mini-card">
                <h5>🏷️ Branding</h5>
                <p>Mockup produk, 8 vibe iklan & format kampanye.</p>
            </div>
            <div class="preview-mini-card">
                <h5>🍜 Kuliner</h5>
                <p>Foto menu komersial, 6 sudut kamera & rasio katalog.</p>
            </div>
            <div class="preview-mini-card">
                <h5>🎥 Story Video</h5>
                <p>8 genre naratif & format video bioskop/medsos.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
