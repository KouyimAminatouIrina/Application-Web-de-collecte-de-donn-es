# Application Web de Collecte et Analyse des Problèmes de Véhicules

Ce projet est une application Flask pour collecter les problèmes rencontrés par les utilisateurs de véhicules, localisés par ville, et proposer des causes et solutions.

## Fonctionnalités

- Formulaire de saisie des problèmes de véhicule
- Diagnostic simple basé sur les mots-clés saisis
- Stockage des rapports dans une base SQLite
- Page d'analyse avec répartition par ville et historique des rapports
- Déploiement sur Render avec `gunicorn`

## Installation locale

1. Crée un environnement virtuel Python :
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lance l'application :
   ```bash
   python app.py
   ```
4. Ouvre `http://127.0.0.1:5000`

## Déploiement Render

1. Pousse ce dépôt sur GitHub.
2. Crée un service Web Python sur Render.
3. Configure le `Build Command` :
   ```bash
   pip install -r requirements.txt
   ```
4. Configure le `Start Command` :
   ```bash
   gunicorn app:app
   ```

Render détectera automatiquement le `Procfile`.
