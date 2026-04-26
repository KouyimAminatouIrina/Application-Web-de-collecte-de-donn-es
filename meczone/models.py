import sqlite3
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

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


def get_problem_type(description):
    """Catégorise le type de problème basé sur la description."""
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in ["moteur", "cliquetis", "fume", "perte de puissance", "surchauffe"]):
        return "Moteur"
    elif any(kw in desc_lower for kw in ["batterie", "lumière", "phares", "clignotant", "feu", "électrique"]):
        return "Électrique"
    elif any(kw in desc_lower for kw in ["frein", "freins", "bruit frein", "pédale", "abs"]):
        return "Freins"
    elif any(kw in desc_lower for kw in ["pneu", "crevaison", "pression", "gonflage", "roule"]):
        return "Pneumatiques"
    elif any(kw in desc_lower for kw in ["clim", "air", "ventilation", "ac", "chauffage"]):
        return "Climatisation"
    else:
        return "Autre"


def simple_correlation(x, y):
    """Calcule une corrélation simple (Pearson) sans scipy."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_y2 = sum(yi ** 2 for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
    
    if denominator == 0:
        return 0.0
    return numerator / denominator


def get_problem_distribution(city):
    """Retourne la distribution des types de problèmes pour une ville."""
    conn = get_db_connection()
    reports = conn.execute("SELECT problem_description FROM reports WHERE city = ?", (city,)).fetchall()
    conn.close()
    
    distribution = {}
    for report in reports:
        problem_type = get_problem_type(report["problem_description"])
        distribution[problem_type] = distribution.get(problem_type, 0) + 1
    
    return distribution


def get_brand_correlations(city):
    """Calcule corrélation âge-problèmes par marque pour une ville."""
    conn = get_db_connection()
    reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = ? AND vehicle_year IS NOT NULL", (city,)).fetchall()
    conn.close()
    
    brand_data = {}
    for report in reports:
        brand = report["vehicle_model"].split()[0] if report["vehicle_model"] else "Inconnu"
        year = report["vehicle_year"]
        if brand not in brand_data:
            brand_data[brand] = []
        brand_data[brand].append(year)
    
    correlations = {}
    for brand, years in brand_data.items():
        if len(years) > 1:
            # Simuler nombre de problèmes par âge (plus vieux = plus de problèmes)
            ages = [datetime.now().year - y for y in years]
            problems = [age * 0.1 + np.random.normal(0, 0.5) for age in ages]  # Simulation simple
            if len(ages) > 1:
                corr, p_value = stats.pearsonr(ages, problems)
                r_squared = corr ** 2
                correlations[brand] = {"r": round(corr, 2), "r2": round(r_squared, 2), "count": len(years)}
    
    return correlations


def get_brand_ranking(city):
    """Classement des marques par moyenne de problèmes par tranche d'âge."""
    conn = get_db_connection()
    reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = ? AND vehicle_year IS NOT NULL", (city,)).fetchall()
    conn.close()
    
    brand_groups = {}
    for report in reports:
        brand = report["vehicle_model"].split()[0] if report["vehicle_model"] else "Inconnu"
        age = datetime.now().year - report["vehicle_year"]
        if brand not in brand_groups:
            brand_groups[brand] = {"ages": [], "problems": []}
        brand_groups[brand]["ages"].append(age)
        # Simulation: problèmes = âge * facteur + bruit
        problems = age * 0.15 + np.random.normal(0, 1)
        brand_groups[brand]["problems"].append(problems)
    
    ranking = {}
    for brand, data in brand_groups.items():
        if data["ages"]:
            avg_age = np.mean(data["ages"])
            avg_problems = np.mean(data["problems"])
            ranking[brand] = {"avg_age": round(avg_age, 1), "avg_problems": round(avg_problems, 1), "count": len(data["ages"])}
    
    # Trier par moyenne de problèmes croissante
    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1]["avg_problems"])
    return sorted_ranking


def generate_pie_chart(distribution):
    """Génère un diagramme circulaire en base64."""
    if not distribution:
        return None
    
    labels = list(distribution.keys())
    sizes = list(distribution.values())
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def get_city_stats(city):
    """Retourne toutes les statistiques pour une ville."""
    distribution = get_problem_distribution(city)
    correlations = get_brand_correlations(city)
    ranking = get_brand_ranking(city)
    pie_chart = generate_pie_chart(distribution)
    
    return {
        "distribution": distribution,
        "correlations": correlations,
        "ranking": ranking,
        "pie_chart": pie_chart
    }


def get_city_list():
    """Récupère la liste des villes disponibles."""
    conn = get_db_connection()
    cities = conn.execute("SELECT DISTINCT city FROM reports ORDER BY city").fetchall()
    conn.close()
    return [row["city"] for row in cities]
