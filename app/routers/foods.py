from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models import Food, User
from ..schemas import CompareRequest, FoodCreate, FoodOut
from ..services.guidance import food_guidance

router = APIRouter(prefix="/foods", tags=["food catalog"])


@router.get("", response_model=list[FoodOut])
def search_foods(q: str | None = None, category: str | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = db.query(Food)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Food.name.ilike(term), Food.brand.ilike(term), Food.category.ilike(term)))
    if category:
        query = query.filter(Food.category.ilike(category))
    return query.order_by(Food.name).offset(offset).limit(limit).all()


@router.get("/{food_id}", response_model=FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


@router.post("", response_model=FoodOut, status_code=201)
def add_food(payload: FoodCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    food = Food(**{**payload.model_dump(), "source": "community"})
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


@router.get("/{food_id}/guidance")
def guidance_for_food(food_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return {"food_id": food.id, "guidance": food_guidance(food, user.profile)}


@router.post("/compare")
def compare_foods(payload: CompareRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    foods = db.query(Food).filter(Food.id.in_(payload.food_ids)).all()
    if len(foods) != len(set(payload.food_ids)):
        raise HTTPException(status_code=404, detail="One or more food IDs were not found")
    profile = user.profile
    return {"foods": [{"food": FoodOut.model_validate(f), "guidance": food_guidance(f, profile)} for f in foods],
            "nutrients_per_serving": ["calories_kcal", "protein_g", "carbohydrates_g", "sugars_g", "fiber_g", "fat_g", "saturated_fat_g", "sodium_mg"],
            "note": "Compare values only when serving sizes are equivalent."}
