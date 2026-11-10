from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models import Food, MealPlan, User
from ..schemas import FoodOut, MealPlanCreate
from ..services.guidance import food_guidance

router = APIRouter(prefix="/meals", tags=["meal planning"])


@router.get("/suggestions")
def suggestions(limit: int = 5, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if limit < 1 or limit > 20:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 20")
    profile = user.profile
    foods = db.query(Food).order_by(Food.protein_g.desc(), Food.fiber_g.desc()).limit(100).all()
    rejected = {x.casefold() for x in (profile.allergies or []) + (profile.avoid_ingredients or [])} if profile else set()
    results = []
    for food in foods:
        food_terms = {x.casefold() for x in (food.allergens or []) + (food.ingredients or [])}
        if rejected & food_terms:
            continue
        if profile and profile.dietary_pattern == "vegan" and not food.vegan:
            continue
        if profile and profile.dietary_pattern == "vegetarian" and not food.vegetarian:
            continue
        results.append({"food": FoodOut.model_validate(food), "guidance": food_guidance(food, profile), "reason": "Selected from catalog using your saved diet preferences; review the nutrition values and guidance."})
        if len(results) >= limit:
            break
    return {"suggestions": results, "disclaimer": "Suggestions are general food ideas, not a prescribed meal plan or treatment."}


@router.get("/plans")
def list_plans(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(MealPlan).filter(MealPlan.user_id == user.id).order_by(MealPlan.created_at.desc()).all()


@router.post("/plans", status_code=201)
def create_plan(payload: MealPlanCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = MealPlan(user_id=user.id, **payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id, MealPlan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    db.delete(plan)
    db.commit()
