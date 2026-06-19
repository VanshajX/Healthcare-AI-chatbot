"""
Report extraction utility.

Supports:
  - PDF  → PyMuPDF (fitz) — text extraction
  - Image (PNG / JPG) → pytesseract OCR
  - Plain text (.txt)
"""

from __future__ import annotations
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        doc.close()
        text = "\n".join(pages).strip()
        if not text:
            return "[PDF contained no extractable text. It may be a scanned image PDF.]"
        return text
    except ImportError:
        return "[PyMuPDF not installed. Run: pip install pymupdf]"
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract OCR."""
    try:
        from PIL import Image
        import pytesseract

        image = Image.open(io.BytesIO(file_bytes))
        text  = pytesseract.image_to_string(image)
        text  = text.strip()
        if not text:
            return "[No text detected in image. Please upload a clearer scan.]"
        return text
    except ImportError:
        return (
            "[OCR libraries not installed. Run:\n"
            "  pip install pytesseract pillow\n"
            "  sudo apt-get install tesseract-ocr  (Linux)\n"
            "  brew install tesseract              (macOS)]"
        )
    except Exception as e:
        return f"[Image OCR error: {e}]"


def extract_text(uploaded_file) -> tuple[str, str]:
    """
    Given a Streamlit UploadedFile, return (extracted_text, mime_type_label).
    mime_type_label is a short human-readable string like 'PDF', 'Image', 'Text'.
    """
    file_bytes = uploaded_file.read()
    name       = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes), "PDF"

    if name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        return extract_text_from_image(file_bytes), "Image"

    if name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8", errors="replace").strip(), "Text"
        except Exception as e:
            return f"[Text decode error: {e}]", "Text"

    return "[Unsupported file type. Please upload a PDF, image, or .txt file.]", "Unknown"
