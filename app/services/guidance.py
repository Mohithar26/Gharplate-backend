"""Transparent, rule-based food flags. This is educational guidance, not diagnosis."""
RULES = {
    "diabetes": [("sugars_g", 10, "Higher sugar per listed serving; consider portion size and total carbohydrates."),
                 ("carbohydrates_g", 30, "Higher carbohydrate per listed serving; check your personal plan." )],
    "hypertension": [("sodium_mg", 600, "High sodium per listed serving; compare lower-sodium options." )],
    "heart_disease": [("saturated_fat_g", 5, "Higher saturated fat per listed serving; consider overall dietary guidance." )],
    "high_cholesterol": [("saturated_fat_g", 5, "Higher saturated fat per listed serving; compare options." )],
    "kidney_disease": [("sodium_mg", 400, "Sodium may matter for some kidney care plans; ask your clinician about your limits." )],
}


def food_guidance(food, profile=None):
    flags, warnings = [], []
    conditions = {str(x).lower().replace(" ", "_") for x in (profile.conditions if profile else [])}
    allergens = {str(x).lower() for x in (profile.allergies if profile else [])}
    avoid = {str(x).lower() for x in (profile.avoid_ingredients if profile else [])}
    food_allergens = {str(x).lower() for x in (food.allergens or [])}
    ingredients = {str(x).lower() for x in (food.ingredients or [])}
    for allergen in sorted(allergens & food_allergens):
        warnings.append(f"Allergen match: {allergen}.")
    for item in sorted(avoid & ingredients):
        warnings.append(f"Avoid-list ingredient match: {item}.")
    for condition in conditions:
        for nutrient, limit, message in RULES.get(condition, []):
            if getattr(food, nutrient, 0) >= limit:
                flags.append({"condition": condition, "nutrient": nutrient, "value": getattr(food, nutrient), "threshold": limit, "message": message})
    return {"flags": flags, "warnings": warnings,
            "disclaimer": "General educational information only. Nutrient thresholds are screening flags, not personalized medical advice. Check the label and follow your clinician's plan."}
