import sqlite3
from datetime import datetime

DB_PATH = "data.db"

PROBLEM_DIAGNOSES = [
    {
        "keywords": ["batterie", "démarrage", "démarre", "ne démarre", "batterie faible"],
        "cause": "Batterie faible ou connexion corrodée.",
        "solution": "Vérifiez la tension de la batterie, nettoyez les bornes et rechargez ou remplacez la batterie si nécessaire."
    },
    {
        "keywords": ["frein", "freins", "bruit frein", "pédale", "abs"],
        "cause": "Usure des plaquettes ou problème hydraulique du système de freinage.",
        "solution": "Contrôlez les plaquettes, le niveau de liquide de frein et faites un diagnostic dans un garage."
    },
    {
        "keywords": ["pneu", "crevaison", "pression", "gonflage", "roule"],
        "cause": "Pneu sous-gonflé, crevé ou déséquilibré.",
        "solution": "Vérifiez la pression, réparez la crevaison et remplacez le pneu si l'usure est excessive."
    },
    {
        "keywords": ["moteur", "cliquetis", "fume", "perte de puissance", "surchauffe"],
        "cause": "Problème moteur possible (bougies, huile, refroidissement).",
        "solution": "Vérifiez le niveau d'huile, les bougies et le système de refroidissement, puis consultez un mécanicien."
    },
    {
        "keywords": ["clim", "air", "ventilation", "ac", "chauffage"],
        "cause": "Système de climatisation ou de ventilation en panne.",
        "solution": "Contrôlez le filtre d'habitacle et le niveau de gaz réfrigérant, puis faites un entretien."
    },
    {
        "keywords": ["lumière", "phares", "clignotant", "feu"],
        "cause": "Ampoule grillée ou problème électrique du circuit d'éclairage.",
        "solution": "Remplacez l'ampoule défectueuse ou vérifiez les fusibles et les connexions."
    }
]

GENERIC_DIAGNOSIS = {
    "cause": "Les causes peuvent être liées à l'entretien, une pièce usée ou une panne électrique.",
    "solution": "Faites vérifier votre véhicule par un professionnel et fournissez une description précise du problème."
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            city TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            problem_description TEXT,
            cause TEXT,
            solution TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def diagnose_problem(description):
    """Analyse la description du problème et retourne une cause et solution probable."""
    description_lower = description.lower()
    for diagnosis in PROBLEM_DIAGNOSES:
        for keyword in diagnosis["keywords"]:
            if keyword in description_lower:
                return diagnosis["cause"], diagnosis["solution"]
    return GENERIC_DIAGNOSIS["cause"], GENERIC_DIAGNOSIS["solution"]


def save_report(name, city, vehicle_model, vehicle_year, problem_description, cause, solution):
    """Enregistre un rapport de problème dans la base de données."""
    created_at = datetime.utcnow().isoformat()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO reports (name, city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at)
    )
    conn.commit()
    conn.close()


def get_all_reports():
    """Récupère tous les rapports de la base de données."""
    conn = get_db_connection()
    reports = conn.execute("SELECT city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at FROM reports ORDER BY created_at DESC").fetchall()
    conn.close()
    return reports


def get_city_stats():
    """Retourne les statistiques de rapports par ville."""
    conn = get_db_connection()
    reports = conn.execute("SELECT city FROM reports").fetchall()
    conn.close()
    
    city_counts = {}
    for report in reports:
        city_name = report["city"]
        city_counts[city_name] = city_counts.get(city_name, 0) + 1
    
    return city_counts
