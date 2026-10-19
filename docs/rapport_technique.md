# Rapport Technique – FitAI

**Mini-Projet IA for Software Engineering**  
ESPRIT – A.U 2026-2027  
Projet individuel Par Rayen Karouch
---

## 1. Introduction et choix du sujet

**FitAI** est une application web de coaching sportif et nutritionnel personnalisé basée sur l’Intelligence Artificielle.

L’utilisateur renseigne son poids, sa taille, son âge, son objectif (perte de poids, prise de muscle, maintien ou endurance), son lieu d’entraînement (maison ou salle), le nombre de jours d’entraînement par semaine, ainsi que ses habitudes alimentaires et éventuelles allergies.

L’application calcule d’abord les besoins énergétiques (BMR et TDEE), puis utilise un modèle de langage (LLM) pour générer :
- un plan alimentaire adapté
- un programme d’entraînement personnalisé
- un planning hebdomadaire
- des conseils pratiques

Ce sujet s’inscrit parfaitement dans la catégorie **« Application web métier avec module IA »** du cahier des charges du Mini-Projet.

---

## 2. Architecture technique

### 2.1 Vue d’ensemble

```
[ Navigateur (Frontend) ]  ←→  [ API FastAPI (Backend) ]  ←→  [ LLM (Groq / OpenAI) ]
```

### 2.2 Front-end
- HTML5 + Tailwind CSS (via CDN)
- JavaScript vanilla
- Aucun framework lourd → démarrage immédiat
- Interface responsive et moderne

### 2.3 Back-end
- **FastAPI** (Python) : framework moderne, rapide et auto-documenté
- **Pydantic** : validation stricte des données entrantes
- CORS activé pour autoriser les appels depuis le frontend
- Endpoint principal : `POST /generate-plan`

### 2.4 Module d’Intelligence Artificielle
- Prompt system soigneusement conçu (rôle de coach + nutritionniste)
- Appel à un LLM via API compatible OpenAI (Groq ou OpenAI)
- Format de réponse imposé en JSON
- Validation de la structure avant retour au client
- Mode **fallback** intelligent si la clé API est absente ou si l’appel échoue

---

## 3. Calculs scientifiques (avant l’appel IA)

Avant d’envoyer les données au LLM, le backend calcule :

| Indicateur | Formule / Méthode |
|------------|-------------------|
| **BMR** (Métabolisme de base) | Formule de Mifflin-St Jeor |
| **TDEE** (Besoin journalier) | BMR × coefficient d’activité |
| **Calories cibles** | TDEE − 400 (perte) / + 300 (prise de muscle) / = (maintien) |

Ces calculs sont ensuite injectés dans le prompt pour que l’IA génère un plan cohérent.

---

## 4. Prompt Engineering

Le prompt système impose :
- Un rôle clair (« coach sportif et nutritionniste certifié »)
- Une structure de sortie JSON stricte
- L’adaptation au lieu d’entraînement (maison vs salle)
- La prise en compte des allergies et de l’alimentation actuelle
- La langue française
- Des règles de sécurité (ne pas donner de conseils médicaux dangereux)

Exemple de structure attendue :
```json
{
  "diet_plan": "...",
  "training_program": "...",
  "weekly_schedule": ["Lundi: ...", "..."],
  "tips": ["...", "..."]
}
```

---

## 5. Sécurité et bonnes pratiques

| Point du cahier des charges | Implémentation |
|-----------------------------|----------------|
| Jamais de données personnelles brutes envoyées telles quelles | Seules les informations nécessaires sont transmises |
| Sortie validée avant affichage | Fonction `validate_output()` |
| Gestion des erreurs d’API (timeout, quota, clé absente) | Try/except + fallback automatique |
| Validation des entrées | Pydantic (âge, poids, taille, etc.) |

---

## 6. Stack technique utilisée

| Composant | Technologie |
|-----------|-------------|
| Front-end | HTML5 + Tailwind CSS + JavaScript |
| Back-end | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| LLM | Groq (llama-3.3-70b) ou OpenAI (gpt-4o-mini) |
| Fallback | Générateur Python déterministe |

---

## 7. Points forts du projet

- Application web réelle et fonctionnelle (front + back)
- Module IA authentique avec prompt engineering
- Calculs métaboliques scientifiques
- Mode démo sans clé API (fallback)
- Code propre, commenté et facilement extensible
- Respect strict des contraintes du cahier des charges

---

## 8. Perspectives d’évolution

- Historique des plans générés
- Suivi de poids dans le temps
- Export PDF du plan
- Authentification utilisateurs
- Application mobile (PWA)

---

## 9. Conclusion

FitAI démontre la capacité à concevoir une application web complète intégrant un module d’Intelligence Artificielle de manière utile et sécurisée.  
Le projet combine calculs scientifiques, prompt engineering et bonnes pratiques de développement web, tout en restant simple à déployer et à présenter.
