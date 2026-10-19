# FitAI – Coach sportif & nutrition par Intelligence Artificielle

**Mini-Projet IA for Software Engineering – ESPRIT A.U 2026-2027**  
Projet individuel

Application web complète qui calcule ton métabolisme et génère un **plan alimentaire + programme d’entraînement personnalisé** grâce à l’IA, en fonction de ton poids, taille, objectif, lieu d’entraînement et habitudes alimentaires.

---

## Fonctionnalités

- Calcul scientifique du BMR (Mifflin-St Jeor) et du TDEE
- Calories cibles selon l’objectif (perte de poids / prise de muscle / maintien)
- Programme d’entraînement adapté **maison** ou **salle**
- Plan alimentaire réaliste qui tient compte de ce que tu manges déjà + allergies
- Planning hebdomadaire + conseils du coach
- Mode **fallback** intelligent → la démo fonctionne même sans clé OpenAI

---

## Architecture

```
FitAI/
├── backend/          # FastAPI (Python)
│   ├── main.py
│   └── requirements.txt
├── frontend/         # HTML + Tailwind + JS
│   ├── index.html
│   └── app.js
├── docs/
│   └── rapport_technique.md
└── README.md
```

| Couche     | Techno              | Rôle                          |
|------------|---------------------|-------------------------------|
| Front-end  | HTML / Tailwind / JS| Interface utilisateur         |
| Back-end   | FastAPI + Pydantic  | API + calculs + validation     |
| Module IA  | OpenAI (gpt-4o-mini)| Génération du plan            |
| Fallback   | Générateur Python   | Démo sans clé API             |

---

## Lancement rapide (2 min)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
Ouvre simplement `frontend/index.html` dans ton navigateur  
(ou `python -m http.server 5500` dans le dossier frontend).

---

## Prompt système (extrait)

```
Tu es un coach sportif et nutritionniste certifié...
Réponds UNIQUEMENT en JSON valide avec :
{
  "diet_plan": "...",
  "training_program": "...",
  "weekly_schedule": [...],
  "tips": [...]
}
```

---

## Démonstration

1. Remplis le formulaire (pré-rempli)
2. Clique sur **Générer mon plan IA**
3. Tu obtiens : calories cibles + régime + programme + planning + conseils

Badge vert = vrai LLM | Badge orange = mode fallback
