import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, SessionLocal, engine
from .models import Food
from .routers import analysis, auth, foods, meals

SEED_FOODS = [
    dict(name="Cooked brown rice", category="grain", source="seed", serving_size="100 g", calories_kcal=123, protein_g=2.7, carbohydrates_g=25.6, sugars_g=0.2, fiber_g=1.6, fat_g=1.0, sodium_mg=4, ingredients=["brown rice"], vegetarian=True, vegan=True),
    dict(name="Cooked lentils", category="legume", source="seed", serving_size="100 g", calories_kcal=116, protein_g=9.0, carbohydrates_g=20.1, sugars_g=1.8, fiber_g=7.9, fat_g=0.4, sodium_mg=2, ingredients=["lentils"], vegetarian=True, vegan=True),
    dict(name="Plain low-fat yogurt", category="dairy", source="seed", serving_size="100 g", calories_kcal=63, protein_g=5.3, carbohydrates_g=7.0, sugars_g=7.0, fiber_g=0, fat_g=1.6, saturated_fat_g=1.0, sodium_mg=70, ingredients=["milk", "cultures"], allergens=["milk"], vegetarian=True),
    dict(name="Boiled egg", category="protein", source="seed", serving_size="1 large egg", calories_kcal=78, protein_g=6.3, carbohydrates_g=0.6, sugars_g=0.6, fiber_g=0, fat_g=5.3, saturated_fat_g=1.6, sodium_mg=62, ingredients=["egg"], allergens=["egg"], vegetarian=True),
    dict(name="Apple with skin", category="fruit", source="seed", serving_size="100 g", calories_kcal=52, protein_g=0.3, carbohydrates_g=13.8, sugars_g=10.4, fiber_g=2.4, fat_g=0.2, sodium_mg=1, ingredients=["apple"], vegetarian=True, vegan=True),
    dict(name="Roasted salted peanuts", category="snack", source="seed", serving_size="100 g", calories_kcal=585, protein_g=24.4, carbohydrates_g=21.3, sugars_g=4.9, fiber_g=8.4, fat_g=49.7, saturated_fat_g=7.7, sodium_mg=410, ingredients=["peanuts", "salt"], allergens=["peanuts"], vegetarian=True, vegan=True),
    dict(name="Plain oats, dry", category="grain", source="seed", serving_size="40 g", calories_kcal=152, protein_g=5.1, carbohydrates_g=27.1, sugars_g=0.4, fiber_g=4.1, fat_g=2.8, saturated_fat_g=0.5, sodium_mg=2, ingredients=["oats"], vegetarian=True, vegan=True),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Food).count() == 0:
            db.add_all([Food(**item) for item in SEED_FOODS])
            db.commit()
    yield


app = FastAPI(title="GharPlate API", description="Food catalog, nutrition profiles, meal ideas, and food analysis APIs.", version="1.0.0", lifespan=lifespan)
allowed_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(foods.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(meals.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "gharplate-api", "version": app.version}
