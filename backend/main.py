"""
FitAI - AI Personal Trainer & Diet Coach
Mini-Projet IA for Software Engineering - ESPRIT 2026-2027
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import math

# Always load .env from the backend folder (next to main.py)
load_dotenv(Path(__file__).resolve().parent / ".env")


# Debug: show if API key was loaded at startup
_k = os.getenv("OPENAI_API_KEY")
print(f"[STARTUP] OPENAI_API_KEY loaded: {bool(_k)} ({(_k[:6] + '...') if _k else 'MISSING'})", flush=True)

app = FastAPI(
    title="FitAI API",
    description="AI coach for personalized training programs and diet plans",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Models ----------
class UserProfile(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=14, le=80)
    gender: Literal["homme", "femme"]
    weight_kg: float = Field(..., gt=30, lt=250)
    height_cm: float = Field(..., gt=120, lt=230)
    goal: Literal["perdre_du_poids", "prendre_du_muscle", "maintien", "endurance"]
    activity_level: Literal["sedentaire", "leger", "modere", "intense"]
    training_place: Literal["maison", "salle"]
    days_per_week: int = Field(..., ge=2, le=6)
    food_intake: Optional[str] = Field(None, max_length=500)  # what the user usually eats
    allergies: Optional[str] = Field(None, max_length=200)


class FitResponse(BaseModel):
    bmr: int
    tdee: int
    target_calories: int
    diet_plan: str
    training_program: str
    weekly_schedule: List[str]
    tips: List[str]
    source: str  # "llm" or "fallback"


# ---------- Calculations (science-based) ----------
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> int:
    """Mifflin-St Jeor formula"""
    if gender == "homme":
        return int(10 * weight + 6.25 * height - 5 * age + 5)
    return int(10 * weight + 6.25 * height - 5 * age - 161)


def calculate_tdee(bmr: int, activity: str) -> int:
    multipliers = {
        "sedentaire": 1.2,
        "leger": 1.375,
        "modere": 1.55,
        "intense": 1.725
    }
    return int(bmr * multipliers.get(activity, 1.2))


def calculate_target_calories(tdee: int, goal: str) -> int:
    if goal == "perdre_du_poids":
        return tdee - 400
    elif goal == "prendre_du_muscle":
        return tdee + 300
    return tdee


# ---------- System Prompt ----------
SYSTEM_PROMPT = """Tu es un coach sportif et nutritionniste certifié, expert en entraînement à domicile et en salle.
À partir du profil de l'utilisateur, génère un plan complet, réaliste et sécurisé.

Réponds UNIQUEMENT en JSON valide avec exactement cette structure :
{
  "diet_plan": "plan alimentaire détaillé sur 1 jour type (petit-déj, déjeuner, dîner, collations) avec quantités approximatives",
  "training_program": "programme d'entraînement adapté au lieu (maison ou salle) et au nombre de jours, avec exercices, séries et répétitions",
  "weekly_schedule": ["Lundi: ...", "Mardi: ...", "Mercredi: ...", "Jeudi: ...", "Vendredi: ...", "Samedi: ...", "Dimanche: repos ou mobilité"],
  "tips": ["conseil 1", "conseil 2", "conseil 3", "conseil 4"]
}

Règles strictes :
- Adapte les exercices au lieu (maison = poids du corps / élastiques, salle = machines + free weights)
- Respecte le nombre de jours d'entraînement demandé
- Tiens compte des allergies et de l'alimentation actuelle mentionnée
- Reste réaliste, motivant et en français
- Ne donne jamais de conseils médicaux dangereux
"""


def build_user_prompt(data: UserProfile, bmr: int, tdee: int, target: int) -> str:
    goal_fr = {
        "perdre_du_poids": "perdre du poids",
        "prendre_du_muscle": "prendre du muscle",
        "maintien": "maintenir son poids",
        "endurance": "améliorer son endurance"
    }[data.goal]

    return f"""Profil de l'utilisateur :
- Nom : {data.name}
- Âge : {data.age} ans | Sexe : {data.gender}
- Poids : {data.weight_kg} kg | Taille : {data.height_cm} cm
- Objectif : {goal_fr}
- Niveau d'activité : {data.activity_level}
- Lieu d'entraînement : {data.training_place}
- Jours d'entraînement par semaine : {data.days_per_week}
- Alimentation actuelle : {data.food_intake or "non précisée"}
- Allergies / restrictions : {data.allergies or "aucune"}

Données calculées :
- BMR (métabolisme de base) : {bmr} kcal
- TDEE (besoin journalier) : {tdee} kcal
- Calories cibles recommandées : {target} kcal

Génère le plan personnalisé.
"""



def _parse_json_content(content: str) -> Optional[dict]:
    if not content:
        return None
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _call_gemini_native(api_key: str, system: str, user: str) -> Optional[dict]:
    """Native Gemini API via the google-genai SDK."""
    try:
        from google import genai
        from google.genai import types

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        print(f"[LLM] Native Gemini model={model_name}", flush=True)

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.5,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )
        return _parse_json_content(response.text)
    except Exception as e:
        print(f"[LLM] Native Gemini failed: {type(e).__name__}: {e}", flush=True)
        return None


def _call_openai_compatible(api_key: str, system: str, user: str) -> Optional[dict]:
    """OpenAI / Groq / Gemini OpenAI-compatible endpoint."""
    try:
        from openai import OpenAI

        base_url = os.getenv("OPENAI_BASE_URL")
        if not base_url and api_key.startswith(("AIza", "AQ.")):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        if base_url and "generativelanguage" in base_url:
            model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        else:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        print(f"[LLM] OpenAI-compat model={model} base_url={base_url or 'default'}", flush=True)

        client = (
            OpenAI(api_key=api_key, base_url=base_url)
            if base_url
            else OpenAI(api_key=api_key)
        )
        kwargs = dict(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.5,
            max_tokens=4096,
        )
        try:
            response = client.chat.completions.create(
                **kwargs, response_format={"type": "json_object"}
            )
        except Exception as e1:
            print(f"[LLM] response_format skipped: {e1}", flush=True)
            response = client.chat.completions.create(**kwargs)

        return _parse_json_content(response.choices[0].message.content)
    except Exception as e:
        print(f"[LLM] OpenAI-compat failed: {type(e).__name__}: {e}", flush=True)
        return None

def call_llm(system: str, user: str) -> Optional[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[LLM] No OPENAI_API_KEY in .env", flush=True)
        return None

    print(f"[LLM] Key loaded (starts with {api_key[:6]}..., length={len(api_key)})", flush=True)

    base_url = (os.getenv("OPENAI_BASE_URL") or "").lower()
    if "generativelanguage.googleapis.com" in base_url or api_key.startswith(("AIza", "AQ.")):
        result = _call_gemini_native(api_key, system, user)
        if result is not None:
            return result
        print("[LLM] Falling back to OpenAI-compatible client...", flush=True)

    return _call_openai_compatible(api_key, system, user)



def fallback_generator(data: UserProfile, target: int) -> dict:
    """High-quality fallback so the demo always works"""

    if data.training_place == "maison":
        program = f"""Programme à domicile ({data.days_per_week} jours/semaine) – Objectif : {data.goal}

Échauffement (5 min) : jumping jacks, arm circles, bodyweight squats

Circuit (3-4 tours) :
1. Squats – 15 reps
2. Pompes (ou pompes genoux) – 10-12 reps
3. Fentes alternées – 10 par jambe
4. Planche – 30-45 secondes
5. Mountain climbers – 20 reps
6. Bird-dog – 10 par côté

Finisher : 2 minutes de burpees ou shadow boxing
Récupération : 60-90 secondes entre les tours

Progression : augmente les reps ou réduis le temps de repos chaque semaine."""
    else:
        program = f"""Programme en salle ({data.days_per_week} jours/semaine)

Jour A – Haut du corps :
- Développé couché 4×8-10
- Tirage vertical 4×10
- Développé militaire 3×10
- Rowing haltère 3×10
- Curl biceps + Extension triceps 3×12

Jour B – Bas du corps :
- Squat barre 4×8
- Leg press 3×12
- Fentes marchées 3×10
- Leg curl 3×12
- Mollets 4×15

Jour C – Full body / cardio (si 3+ jours)
Alterner A/B et ajouter 20 min de cardio modéré."""

    diet = f"""Plan alimentaire type (~{target} kcal)

Petit-déjeuner :
- 2 œufs + 40g flocons d'avoine + 1 fruit
- ou yaourt grec + miel + amandes

Déjeuner :
- 150g poulet / thon / tofu
- 80g riz ou quinoa (poids cru)
- Légumes à volonté + 1 c.à.s d'huile d'olive

Collation :
- 1 fruit + 20g de noix
- ou shake protéiné si objectif muscle

Dîner :
- Poisson ou viande maigre 150g
- Légumes vapeur + pomme de terre ou patate douce
- Salade verte

Hydratation : 2,5 à 3,5 L d'eau / jour
Ajuste les quantités selon ta faim et tes résultats."""

    schedule = []
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    training_days = data.days_per_week
    for i, day in enumerate(days):
        if i < training_days:
            schedule.append(f"{day}: Entraînement + marche 20-30 min")
        elif i == 6:
            schedule.append(f"{day}: Repos complet ou mobilité douce")
        else:
            schedule.append(f"{day}: Repos actif (marche / étirements)")

    tips = [
        "Dors 7-8 heures par nuit – c'est là que tu progresses vraiment.",
        "Pesée 1 fois par semaine le matin à jeun pour suivre l'évolution.",
        "Si tu stagnes 2 semaines, ajuste les calories de ±150 kcal.",
        "La régularité bat l'intensité : mieux vaut 3 séances correctes que 1 séance parfaite."
    ]

    return {
        "diet_plan": diet,
        "training_program": program,
        "weekly_schedule": schedule,
        "tips": tips
    }


def validate_output(raw: dict) -> bool:
    required = ["diet_plan", "training_program", "weekly_schedule", "tips"]
    return all(k in raw for k in required) and len(raw["tips"]) >= 2


@app.get("/")
def root():
    return {"message": "FitAI API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.post("/generate-plan", response_model=FitResponse)
def generate_plan(data: UserProfile):
    bmr = calculate_bmr(data.weight_kg, data.height_cm, data.age, data.gender)
    tdee = calculate_tdee(bmr, data.activity_level)
    target = calculate_target_calories(tdee, data.goal)

    system = SYSTEM_PROMPT
    user = build_user_prompt(data, bmr, tdee, target)

    llm_result = call_llm(system, user)
    source = "llm"

    if llm_result is None or not validate_output(llm_result):
        llm_result = fallback_generator(data, target)
        source = "fallback"

    return FitResponse(
        bmr=bmr,
        tdee=tdee,
        target_calories=target,
        diet_plan=llm_result["diet_plan"],
        training_program=llm_result["training_program"],
        weekly_schedule=llm_result["weekly_schedule"],
        tips=llm_result["tips"],
        source=source
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
