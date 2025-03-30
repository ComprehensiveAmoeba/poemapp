
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

st.set_page_config(page_title="Creador de Poemas", layout="centered")

backgrounds = {
    "Fondo 1": "https://cataluz.click/wp-content/uploads/2025/03/fondo1.png",
    "Fondo 2": "https://cataluz.click/wp-content/uploads/2025/03/fondo2.png",
    "Fondo 3": "https://cataluz.click/wp-content/uploads/2025/03/fondo3.png",
    "Fondo 4": "https://cataluz.click/wp-content/uploads/2025/03/fondo-4.png",
}
fonts = {
    "Arial": "fonts/Arial.ttf",
    "Máquina de escribir": "fonts/Courier.ttf",
    "Manuscrita": "fonts/DancingScript-Regular.ttf",
}
watermark_url = "https://cataluz.click/wp-content/uploads/2025/03/Feliz__1_-removebg-preview-1024x171-1-10-2-2-1-2-1-1-2-1-1-2-1-1-1-2-1-3-2-3-2-2-2-2-2-2-2-1-1-1-1-2-1-1-1-2-1-4-2-2-2-2-2-1-2-2-3-1-2-1-2-1-2-2-2-1-1-2-1-1-1-1.webp"

st.title("🖋️ Creador de Poemas con Estilo")

texto = st.text_area("✏️ Escribe tu texto aquí:", height=200)
background_choice = st.selectbox("📄 Elige un fondo:", list(backgrounds.keys()))
font_choice = st.selectbox("🔤 Elige la tipografía:", list(fonts.keys()))
alignment = st.selectbox("📐 Alineación del texto:", ["Izquierda", "Centro", "Derecha", "Justificado"])
spacing_option = st.selectbox("📏 Espaciado de líneas:", ["Apretado", "Normal", "Separado"])
signature = st.text_input("✍️ Añade tu firma (opcional):")
add_watermark = st.checkbox("🎄 Añadir 'Feliz Navidad' al pie")

alignment_map = {
    "Izquierda": "left",
    "Centro": "center",
    "Derecha": "right",
    "Justificado": "left",
}
spacing_map = {
    "Apretado": 5,
    "Normal": 10,
    "Separado": 20,
}

def create_image():
    bg_response = requests.get(backgrounds[background_choice])
    background = Image.open(BytesIO(bg_response.content)).convert("RGBA")
    draw = ImageDraw.Draw(background)

    margin_x = int(background.width * 0.15)
    margin_y = int(background.height * 0.12)
    max_width = background.width - 2 * margin_x
    max_height = background.height - 3 * margin_y

    try:
        font = ImageFont.truetype(fonts[font_choice], 60)
    except:
        font = ImageFont.load_default()

    line_spacing = spacing_map[spacing_option]

    # Auto font size considering width and height
    font_size = 60
    while font_size > 20:
        font = ImageFont.truetype(fonts[font_choice], font_size)
        wrapper = textwrap.TextWrapper(width=100)
        wrapped_lines = []
        for line in texto.split("\n"):
            estimated_chars = int(max_width / font.getlength("A"))  # approx
            wrapper.width = estimated_chars
            wrapped_lines.extend(wrapper.wrap(line) or [""])
        wrapped_text = "\n".join(wrapped_lines)
        lines = wrapped_text.split("\n")
        max_line_width = max(draw.textlength(line, font=font) for line in lines)
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=line_spacing)
        if max_line_width <= max_width and (text_bbox[3] - text_bbox[1]) <= max_height:
            break
        font_size -= 2

    # Final text position
    text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=line_spacing)
    x = (background.width - (text_bbox[2] - text_bbox[0])) // 2
    y = (background.height - (text_bbox[3] - text_bbox[1])) // 2

    draw.multiline_text((x, y), wrapped_text, font=font, fill="black", spacing=line_spacing, align=alignment_map[alignment])

    # Add signature
    if signature:
        sig_font = ImageFont.truetype(fonts.get("Arial"), font_size, layout_engine=ImageFont.Layout.BASIC)
        sig_text = f"- {signature}"
        sig_bbox = draw.textbbox((0, 0), sig_text, font=sig_font)
        sig_width = sig_bbox[2] - sig_bbox[0]
        sig_height = sig_bbox[3] - sig_bbox[1]
        sig_x = background.width - sig_width - margin_x
        sig_y = background.height - sig_height - margin_y
        draw.text((sig_x, sig_y), sig_text, font=sig_font, fill="black")

    # Add watermark
    if add_watermark:
        wm_response = requests.get(watermark_url)
        watermark = Image.open(BytesIO(wm_response.content)).convert("RGBA")
        wm_ratio = background.width / watermark.width * 0.5
        wm_size = (int(watermark.width * wm_ratio), int(watermark.height * wm_ratio))
        watermark = watermark.resize(wm_size, Image.LANCZOS)
        wm_x = (background.width - watermark.width) // 2
        wm_y = background.height - watermark.height - 30
        background.alpha_composite(watermark, (wm_x, wm_y))

    return background.convert("RGB")

if st.button("👁️ Vista Previa"):
    if texto:
        result = create_image()
        st.image(result, caption="Vista previa", use_column_width=True)
    else:
        st.warning("Por favor, escribe un texto.")

if st.button("⬇️ Descargar Imagen"):
    if texto:
        result = create_image()
        buf = BytesIO()
        result.save(buf, format="PNG")
        st.download_button(label="Descargar", data=buf.getvalue(), file_name="poema.png", mime="image/png")
    else:
        st.warning("Por favor, escribe un texto.")
