# Script de présentation – Soutenance FitAI 

---

### 1. Introduction 

« Bonjour, je m’appelle Rayen Karouch.  
Mon mini-projet s’appelle **FitAI**, une application web de coaching sportif et nutritionnel personnalisé basée sur l’Intelligence Artificielle.

Le problème que je résous : beaucoup de personnes veulent s’entraîner à la maison ou en salle, mais ne savent pas quoi manger ni quel programme suivre selon leur poids, leur taille et leur objectif.

FitAI calcule d’abord les besoins énergétiques de l’utilisateur, puis utilise un modèle de langage pour générer un plan alimentaire + un programme d’entraînement adaptés. »

---

### 2. Démonstration live 

1. Ouvrir l’application
2. Montrer le formulaire (poids, taille, objectif, lieu d’entraînement, alimentation actuelle…)
3. Cliquer sur **« Générer mon plan IA »**
4. Montrer le résultat :
   - BMR / TDEE / Calories cibles
   - Plan alimentaire
   - Programme d’entraînement (maison ou salle)
   - Planning de la semaine
   - Conseils du coach
5. Souligner le badge vert « Généré par LLM » (preuve que c’est bien de l’IA réelle)

---

### 3. Architecture technique 

« L’architecture est simple et moderne :

- **Front-end** : HTML + Tailwind + JavaScript (léger et rapide)
- **Back-end** : FastAPI (Python)
- **Module IA** : appel à un LLM (Groq ou OpenAI) avec un prompt système soigneusement conçu

Avant d’appeler l’IA, je calcule le BMR avec la formule de Mifflin-St Jeor et le TDEE.  
Ces valeurs sont injectées dans le prompt pour que le plan soit cohérent.

J’ai aussi mis en place un mode fallback : si la clé API est absente ou si l’appel échoue, l’application continue de fonctionner avec un générateur intelligent. »

---

### 4. Prompt Engineering & Sécurité 

« Le prompt système impose un format JSON strict et des règles claires :  
adapter le programme au lieu (maison/salle), tenir compte des allergies, rester en français, ne pas inventer de données.

J’ai également validé les entrées avec Pydantic et validé la sortie du LLM avant de l’afficher. »

---

### 5. Conclusion & Perspectives 

« FitAI est une application web complète qui combine calculs scientifiques et Intelligence Artificielle de manière utile.

Perspectives :
- Historique des plans
- Suivi de poids
- Export PDF
- Version mobile

Merci pour votre attention. Je suis prêt pour vos questions. »

---

