from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserOut(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool


class ProfileUpdate(BaseModel):
    age: int | None = Field(default=None, ge=1, le=120)
    dietary_pattern: str | None = Field(default=None, max_length=40)
    goals: list[str] | None = None
    conditions: list[str] | None = None
    allergies: list[str] | None = None
    avoid_ingredients: list[str] | None = None
    daily_calorie_target: int | None = Field(default=None, ge=500, le=10000)


class ProfileOut(ORMModel):
    id: int
    user_id: int
    age: int | None
    dietary_pattern: str
    goals: list[str]
    conditions: list[str]
    allergies: list[str]
    avoid_ingredients: list[str]
    daily_calorie_target: int | None


class FoodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    brand: str | None = None
    category: str = "other"
    source: str = "community"
    serving_size: str = "100 g"
    calories_kcal: float = Field(default=0, ge=0)
    protein_g: float = Field(default=0, ge=0)
    carbohydrates_g: float = Field(default=0, ge=0)
    sugars_g: float = Field(default=0, ge=0)
    fiber_g: float = Field(default=0, ge=0)
    fat_g: float = Field(default=0, ge=0)
    saturated_fat_g: float = Field(default=0, ge=0)
    sodium_mg: float = Field(default=0, ge=0)
    ingredients: list[str] = []
    allergens: list[str] = []
    vegetarian: bool = True
    vegan: bool = False
    notes: str | None = None


class FoodOut(ORMModel):
    id: int
    name: str
    brand: str | None
    category: str
    source: str
    serving_size: str
    calories_kcal: float
    protein_g: float
    carbohydrates_g: float
    sugars_g: float
    fiber_g: float
    fat_g: float
    saturated_fat_g: float
    sodium_mg: float
    ingredients: list[str]
    allergens: list[str]
    vegetarian: bool
    vegan: bool
    notes: str | None


class IngredientAnalysisRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1, max_length=100)
    name: str = "Homemade food"
    serving_size: str = "1 serving"


class CompareRequest(BaseModel):
    food_ids: list[int] = Field(min_length=2, max_length=5)


class MealPlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    date: str | None = None
    meals: list[dict] = []
