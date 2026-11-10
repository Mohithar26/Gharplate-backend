"""Best-effort local OCR for packaged labels; it does not identify a dish from a photo."""
import re

NUTRIENTS = {
    "calories_kcal": r"(?:calories|energy)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    "protein_g": r"protein\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "carbohydrates_g": r"(?:total\s+)?carbohydrates?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "sugars_g": r"(?:total\s+)?sugars?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "fiber_g": r"(?:dietary\s+)?fibre?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "fat_g": r"(?:total\s+)?fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "saturated_fat_g": r"saturated\s+fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "sodium_mg": r"sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg?",
}


def scan_label(image_bytes: bytes) -> dict:
    try:
        from PIL import Image
        import pytesseract
        from io import BytesIO
        text = pytesseract.image_to_string(Image.open(BytesIO(image_bytes)))
    except (ImportError, OSError, RuntimeError) as exc:
        return {"ocr_available": False, "message": f"Label OCR is unavailable ({type(exc).__name__}). Install Tesseract OCR and the Python extras to enable it."}
    normalized = re.sub(r"\s+", " ", text).strip()
    parsed = {}
    for field, pattern in NUTRIENTS.items():
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            parsed[field] = float(match.group(1))
    ingredient_match = re.search(r"ingredients?\s*[:\-]\s*(.*?)(?=\b(?:allergen|contains|nutrition|nutrition facts|per serving)\b|$)", normalized, re.IGNORECASE)
    ingredients = [part.strip(" .;") for part in ingredient_match.group(1).split(",") if part.strip(" .;")] if ingredient_match else []
    return {"ocr_available": True, "extracted_text": normalized[:12000], "nutrition_candidates": parsed,
            "ingredients_candidates": ingredients, "status": "needs_review",
            "message": "OCR candidates may contain errors. Confirm serving size, units, ingredients, and nutrition values against the package before saving."}
