from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
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
    description_lower = description.lower()
    for diagnosis in PROBLEM_DIAGNOSES:
        for keyword in diagnosis["keywords"]:
            if keyword in description_lower:
                return diagnosis["cause"], diagnosis["solution"]
    return GENERIC_DIAGNOSIS["cause"], GENERIC_DIAGNOSIS["solution"]


# Initialize the database when the module is imported.
init_db()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "Anonyme").strip()
    city = request.form.get("city", "").strip()
    vehicle_model = request.form.get("vehicle_model", "").strip()
    problem_description = request.form.get("problem_description", "").strip()

    if not city or not problem_description:
        return redirect(url_for("index"))

    cause, solution = diagnose_problem(problem_description)
    created_at = datetime.utcnow().isoformat()

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO reports (name, city, vehicle_model, problem_description, cause, solution, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, city, vehicle_model, problem_description, cause, solution, created_at)
    )
    conn.commit()
    conn.close()

    return render_template(
        "results.html",
        name=name,
        city=city,
        vehicle_model=vehicle_model,
        problem_description=problem_description,
        cause=cause,
        solution=solution
    )


@app.route("/analysis", methods=["GET"])
def analysis():
    conn = get_db_connection()
    reports = conn.execute("SELECT city, problem_description, cause, solution, created_at FROM reports ORDER BY created_at DESC").fetchall()
    city_counts = {}
    for report in reports:
        city_name = report["city"]
        city_counts[city_name] = city_counts.get(city_name, 0) + 1

    total_reports = len(reports)
    conn.close()

    return render_template(
        "analysis.html",
        reports=reports,
        city_counts=city_counts,
        total_reports=total_reports
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
