import streamlit as st
from io import BytesIO
from PIL import Image
import pikepdf
import zipfile

# ---------------- Compress images inside PDF ----------------
def compress_pdf_images(file_bytes, quality=30, max_width=1000, grayscale=False):
    file_bytes.seek(0)
    pdf = pikepdf.open(file_bytes)
    
    for page in pdf.pages:
        if not hasattr(page, "images"):
            continue
        for image_name, image_obj in page.images.items():
            try:
                raw_image = pdf.open_stream(image_obj)
                pil_img = Image.open(BytesIO(raw_image.read_bytes()))

                if pil_img.width > max_width:
                    ratio = max_width / pil_img.width
                    pil_img = pil_img.resize((max_width, int(pil_img.height * ratio)), Image.LANCZOS)

                if grayscale:
                    pil_img = pil_img.convert("L")

                img_bytes = BytesIO()
                pil_img.save(img_bytes, format="JPEG", quality=quality)
                img_bytes.seek(0)

                pdf.replace_image(image_obj, img_bytes.getvalue())
            except:
                continue  

    out_bytes = BytesIO()
    pdf.save(out_bytes)
    out_bytes.seek(0)
    return out_bytes

# ---------------- Compress standalone images ----------------
def compress_image(file_bytes, quality=30, max_width=1000, grayscale=False):
    pil_img = Image.open(file_bytes)

    if pil_img.width > max_width:
        ratio = max_width / pil_img.width
        pil_img = pil_img.resize((max_width, int(pil_img.height * ratio)), Image.LANCZOS)

    if grayscale:
        pil_img = pil_img.convert("L")

    img_bytes = BytesIO()
    pil_img.save(img_bytes, format="JPEG", quality=quality)
    img_bytes.seek(0)
    return img_bytes

# ---------------- Streamlit UI ----------------
st.set_page_config(
    page_title="PDF & Image Compressor",
    page_icon="📘",
    layout="centered"
)

# ---------------- App Header ----------------
st.title("📘 PDF & Image Compression Tool")
st.caption("Compress PDFs and Images quickly with optional grayscale conversion.")

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["📄 PDF Compression", "🖼️ Image Compression"])

# ---------------- TAB 1: PDF Compression ----------------
with tab1:
    st.subheader("📄 Compress PDF Files")

    quality = st.selectbox("Select Compression Level", ["Low (30)", "Medium (50)", "High (70)"], index=1, key="pdf_quality")
    grayscale_option = st.radio("Convert to Grayscale?", ["No", "Yes"], horizontal=True, key="pdf_grayscale")

    uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=['pdf'], key="pdf_upload")

    if uploaded_files:
        compressed_files = []
        q_val = int(quality.split("(")[1].replace(")", ""))

        for file in uploaded_files:
            original_size = round(len(file.getvalue())/1024, 2)
            try:
                compressed_file = compress_pdf_images(file, quality=q_val, grayscale=(grayscale_option=="Yes"))
                filename = f"compressed_{file.name}"

                compressed_size = round(len(compressed_file.getvalue())/1024, 2)
                reduction = round(100*(original_size - compressed_size)/original_size, 2)
                st.success(f"✅ {file.name}: {original_size} KB → {compressed_size} KB | Saved {reduction}%")

                compressed_files.append((filename, compressed_file.getvalue()))
            except Exception as e:
                st.error(f"❌ Failed to process {file.name}: {e}")

        if compressed_files:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for fname, data in compressed_files:
                    zip_file.writestr(fname, data)
            zip_buffer.seek(0)

            st.download_button(
                label="📥 Download All Compressed PDFs (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="compressed_pdfs.zip"
            )

# ---------------- TAB 2: Image Compression ----------------
with tab2:
    st.subheader("🖼️ Compress Images")

    quality = st.selectbox("Select Compression Level", ["Low (30)", "Medium (50)", "High (70)"], index=2, key="img_quality")
    grayscale_option = st.radio("Convert to Grayscale?", ["No", "Yes"], horizontal=True, key="img_grayscale")

    uploaded_imgs = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="img_upload")

    if uploaded_imgs:
        compressed_imgs = []
        q_val = int(quality.split("(")[1].replace(")", ""))

        for img in uploaded_imgs:
            original_size = round(len(img.getvalue())/1024, 2)
            try:
                compressed_img = compress_image(img, quality=q_val, grayscale=(grayscale_option=="Yes"))
                filename = f"compressed_{img.name}"

                compressed_size = round(len(compressed_img.getvalue())/1024, 2)
                reduction = round(100*(original_size - compressed_size)/original_size, 2)
                st.success(f"✅ {img.name}: {original_size} KB → {compressed_size} KB | Saved {reduction}%")

                compressed_imgs.append((filename, compressed_img.getvalue()))
            except Exception as e:
                st.error(f"❌ Failed to process {img.name}: {e}")

        if compressed_imgs:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for fname, data in compressed_imgs:
                    zip_file.writestr(fname, data)
            zip_buffer.seek(0)

            st.download_button(
                label="📥 Download All Compressed Images (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="compressed_images.zip"
            )
