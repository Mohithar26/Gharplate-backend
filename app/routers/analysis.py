from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models import Food, FoodAnalysis, User
from ..schemas import FoodOut, IngredientAnalysisRequest
from ..services.guidance import food_guidance
from ..services.image_scan import scan_label

router = APIRouter(prefix="/analysis", tags=["food analysis"])
UPLOAD_DIR = Path("uploads")
MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/history")
def analysis_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(FoodAnalysis).filter(FoodAnalysis.user_id == user.id).order_by(FoodAnalysis.created_at.desc()).limit(100).all()
    return [{"id": r.id, "input_type": r.input_type, "status": r.status, "submitted_text": r.submitted_text,
             "result": r.result, "created_at": r.created_at} for r in records]


@router.post("/image", status_code=202)
async def analyze_image(image: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image")
    content = await image.read(MAX_IMAGE_BYTES + 1)
    if not content or len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be between 1 byte and 8 MB")
    try:
        from PIL import Image
        from io import BytesIO
        with Image.open(BytesIO(content)) as decoded:
            decoded.verify()
    except (ImportError, OSError, ValueError):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid supported image")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[image.content_type]
    path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    path.write_bytes(content)
    result = scan_label(content)
    record = FoodAnalysis(user_id=user.id, input_type="image", image_path=str(path), status="needs_review", result=result)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"analysis_id": record.id, "status": record.status, "food_recognition": "not_configured", **record.result}


@router.post("/ingredients")
def analyze_ingredients(payload: IngredientAnalysisRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    foods = db.query(Food).all()
    requested = [part.strip() for part in payload.ingredients if part.strip()]
    matches, unknown = [], []
    for item in requested:
        found = next((f for f in foods if item.casefold() in f.name.casefold() or any(item.casefold() in str(x).casefold() for x in (f.ingredients or []))), None)
        if found:
            matches.append({"query": item, "food": FoodOut.model_validate(found), "guidance": food_guidance(found, user.profile)})
        else:
            unknown.append(item)
    record = FoodAnalysis(user_id=user.id, input_type="ingredients", submitted_text=", ".join(requested), status="completed",
                          result={"matched_count": len(matches), "unknown_count": len(unknown)})
    db.add(record)
    db.commit()
    return {"analysis_id": record.id, "name": payload.name, "serving_size": payload.serving_size, "matches": matches,
            "unknown_ingredients": unknown,
            "note": "Matched catalog entries are references, not a calculated recipe nutrient total. Add amounts for each ingredient to calculate a serving accurately."}
