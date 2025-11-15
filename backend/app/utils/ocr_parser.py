# This is a simplified OCR parser that uses EasyOCR or Pillow + pytesseract.
# For production you will tune bbox detection per template (region-of-interest).
import easyocr
import re
from PIL import Image
from io import BytesIO

reader = easyocr.Reader(['en'])  # instantiate once

def ocr_image_bytes(image_bytes: bytes) -> str:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    results = reader.readtext(np.array(image))
    # results -> list of (bbox, text, conf)
    # join text for now; downstream we'll implement region splits
    text = "\n".join([r[1] for r in results])
    return text

def parse_report_text(text: str) -> dict:
    # Very simple parser (improve with coordinates)
    data = {}
    # examples of regex to extract fields; you will refine for robustness
    m = re.search(r"Fried Item[:\s]*([A-Za-z0-9\s]+)", text, re.IGNORECASE)
    if m: data["fried_item"] = m.group(1).strip()
    m = re.search(r"LOT[#:]?\s*([A-Za-z0-9-]+)", text, re.IGNORECASE)
    if m: data["lot_number"] = m.group(1).strip()
    # time/date etc...
    return data
