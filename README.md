# GharPlate backend

Backend API for **GharPlate - Smart Food Intelligence and Personalized Nutrition Assistant**. This project assigns the complete backend implementation to one developer (you). It is a standalone FastAPI service using SQLite by default and SQLAlchemy for data access.

## Included features

- Account registration, password hashing, bearer-token login, and profile management.
- Nutrition profiles for dietary pattern, goals, allergies, ingredients to avoid, conditions, and optional calorie target.
- Searchable food catalog with sample foods and per-serving nutrient fields.
- Personalized food flags and allergen/avoid-list warnings, including food comparison.
- Ingredient search against catalog foods.
- Profile-filtered food ideas and saved meal plans.
- Image upload with validation, optional local OCR for packaged nutrition labels, ingredient candidates, and analysis history.
- OpenAPI documentation at `/docs` and a health endpoint at `/health`.

## Run locally

Requires Python 3.10 or newer.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Change `SECRET_KEY` in `.env` before using accounts beyond local development. Start the server:

```powershell
uvicorn app.main:app --reload
```

The API starts at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`. The SQLite database is created as `gharplate.db` on first start and seeded with a small demonstration catalog. Set `DATABASE_URL` for another SQLAlchemy-supported database. Set `CORS_ORIGINS` to the frontend origin(s), comma-separated.

## API overview

All application routes use `/api/v1`.

| Method | Route | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register` | No | Create an account and empty nutrition profile |
| POST | `/auth/token` | No | Log in; send form fields `username` (email) and `password` |
| GET | `/auth/me` | Yes | Current account |
| GET / PUT | `/auth/profile` | Yes | Read/update nutrition preferences |
| GET | `/foods?q=&category=` | No | Search catalog |
| GET | `/foods/{id}` | No | Food nutrition details |
| GET | `/foods/{id}/guidance` | Yes | Personalized flags and warnings |
| POST | `/foods` | Yes | Add a catalog food |
| POST | `/foods/compare` | Yes | Compare 2-5 foods against profile |
| POST | `/analysis/ingredients` | Yes | Match ingredient names against catalog |
| POST | `/analysis/image` | Yes | Upload a JPEG, PNG, or WebP label image (max 8 MB); returns OCR candidates when Tesseract is available |
| GET | `/analysis/history` | Yes | Recent analysis records for current account |
| GET | `/meals/suggestions` | Yes | Food ideas filtered for preferences |
| GET / POST | `/meals/plans` | Yes | List/save meal plans |
| DELETE | `/meals/plans/{id}` | Yes | Delete own meal plan |

For protected routes, send `Authorization: Bearer <access_token>`. Registration example:

```json
{"email":"you@example.com","full_name":"Your Name","password":"choose-a-password"}
```

Profile example:

```json
{"dietary_pattern":"vegetarian","conditions":["hypertension"],"allergies":["peanuts"],"goals":["balanced eating"]}
```

Supported condition flag keys currently include `diabetes`, `hypertension`, `heart_disease`, `high_cholesterol`, and `kidney_disease`. These are transparent nutrient screening rules, not medical assessment.

## Important implementation boundaries

- Uploaded pictures are stored under `uploads/` and recorded as `needs_review`. Packaged label OCR uses the Python extras plus the Tesseract OCR application installed on the machine. OCR values are candidates that need a person to confirm; they are not automatically added to the catalog. A trained food-recognition model for identifying homemade dishes and barcode lookup still need a provider integration.
- Ingredient lookup returns matching catalog records; it does not calculate recipe nutrition without ingredient quantities and serving counts.
- The demonstration catalog is small and is not a verified national food database. Expand it with a trusted source and retain source/provenance for each record.
- Guidance is general education only. Users with medical conditions should follow advice from their qualified clinician.
- Before public deployment, configure a strong secret, HTTPS, production database, private object storage, upload scanning and retention controls, backups, migrations, and appropriate account/email recovery. Do not deploy the development secret.
