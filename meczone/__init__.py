import os
from flask import Flask
from meczone.models import init_db
from meczone.routes import register_routes


def create_app():
    """Factory pour créer et configurer l'application Flask."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Initialiser la base de données
    init_db()

    # Enregistrer les routes
    register_routes(app)

    return app


# Créer l'instance de l'app pour usage par gunicorn et le point d'entrée
app = create_app()