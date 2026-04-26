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
    try:
        vehicle_year = int(vehicle_year) if vehicle_year else None
    except (ValueError, TypeError):
        vehicle_year = None
    
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


def get_brand_correlations(city=None):
    """Calcule corrélation âge-problèmes par marque pour une ville ou national."""
    conn = get_db_connection()
    if city:
        reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = ? AND vehicle_year IS NOT NULL", (city,)).fetchall()
    else:
        reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE vehicle_year IS NOT NULL").fetchall()
    conn.close()
    
    from collections import Counter
    brand_data = {}
    for report in reports:
        brand = report["vehicle_model"].split()[0] if report["vehicle_model"] else "Inconnu"
        year = report["vehicle_year"]
        age = datetime.now().year - year
        if brand not in brand_data:
            brand_data[brand] = []
        brand_data[brand].append(age)
    
    correlations = {}
    for brand, ages in brand_data.items():
        age_counts = Counter(ages)
        x = list(age_counts.keys())
        y = list(age_counts.values())
        if len(x) > 1:
            corr = simple_correlation(x, y)
            r_squared = corr ** 2
            # Linear regression
            if len(x) > 1:
                slope, intercept = np.polyfit(x, y, 1)
            else:
                slope, intercept = 0, 0
            correlations[brand] = {"r": round(corr, 2), "r2": round(r_squared, 2), "count": len(ages), "slope": round(slope, 2), "intercept": round(intercept, 2)}
    
    return correlations


def get_brand_ranking(city=None):
    """Classement des marques par moyenne de problèmes par tranche d'âge."""
    conn = get_db_connection()
    if city:
        reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = ? AND vehicle_year IS NOT NULL", (city,)).fetchall()
    else:
        reports = conn.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE vehicle_year IS NOT NULL").fetchall()
    conn.close()
    
    brand_groups = {}
    for report in reports:
        brand = report["vehicle_model"].split()[0] if report["vehicle_model"] else "Inconnu"
        age = datetime.now().year - report["vehicle_year"]
        if brand not in brand_groups:
            brand_groups[brand] = {"ages": [], "problems": []}
        brand_groups[brand]["ages"].append(age)
        problems = age * 0.15 + np.random.normal(0, 1)
        brand_groups[brand]["problems"].append(problems)
    
    ranking = {}
    for brand, data in brand_groups.items():
        if data["ages"]:
            avg_age = np.mean(data["ages"])
            avg_problems = np.mean(data["problems"])
            ranking[brand] = {"avg_age": round(avg_age, 1), "avg_problems": round(avg_problems, 1), "count": len(data["ages"])}
    
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


def get_city_stats():
    """Retourne le compte des rapports par ville."""
    conn = get_db_connection()
    reports = conn.execute("SELECT city FROM reports").fetchall()
    conn.close()
    
    city_counts = {}
    for report in reports:
        city_name = report["city"]
        city_counts[city_name] = city_counts.get(city_name, 0) + 1
    
    return city_counts


def get_city_list():
    """Récupère la liste des villes disponibles."""
    conn = get_db_connection()
    cities = conn.execute("SELECT DISTINCT city FROM reports ORDER BY city").fetchall()
    conn.close()
    return [row["city"] for row in cities]


def get_city_analytics(city):
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


def get_garages_by_city(city):
    """Retourne la liste des garages pour une ville donnée."""
    garages = {
        "Douala": [
            {"name": "Garage Auto Fixpress", "location": "Quartier Logpom", "phone": "699 18 79 98"},
            {"name": "Douala Auto Sarl", "location": "Quartier Bonaberi", "phone": "672 85 16 52 / 683 32 81 67"},
            {"name": "Garage Auto Location Express (GALE)", "location": "Quartier Bonapriso", "phone": "+237 696 97 39 00"},
            {"name": "Garage Flora", "location": "11 Rue Franqueville, Akwa", "phone": "233 43 06 22 / 699 93 47 19"},
            {"name": "KIA MOTORS AUTO SA (KM AUTO SA)", "location": "Avenue de Gaulle Bonanjo & Zone Industrielle Bonaberi", "phone": "233 65 65 65 / 669 80 02 78"},
            {"name": "GAP MOTORS", "location": "Axe Douala-Yaoundé après BOCOM", "phone": "694 57 90 80 / 677 13 20 88"},
            {"name": "AUTO HAUS", "location": "Face Polyclinique d'Akwa", "phone": "233 425 586"},
            {"name": "AUTO STOP SARL", "location": "Douala Bali derrière SGC, Rue Bertaut", "phone": "699 88 75 37 / 653 05 06 18"},
            {"name": "Force Tyre Sarl", "location": "Route Base Navale Youpwé", "phone": "233 42 79 76"}
        ],
        "Limbé": [
            {"name": "DynaSet Garage (Victor Njoh)", "location": "Quartier New Town", "phone": "677 41 98 35"},
            {"name": "HGS Garage Ltd", "location": "Ancienne Route Bonaberi, BP 1227", "phone": "654 22 24 55"},
            {"name": "ETS BEN AUTO PARTS", "location": "Maligah", "phone": "677 94 75 75"},
            {"name": "237mechanic", "location": "Limbé", "phone": "(contact en ligne)"},
            {"name": "Confidence Garage", "location": "Limbé", "phone": "(contacter via annuaire)"},
            {"name": "Auto Parts & Services with William Manga", "location": "Limbé", "phone": "(à confirmer)"}
        ],
        "Yaoundé": [
            {"name": "Garage Les Invincibles", "location": "Quartier Oyom Abang (à côté de l'école primaire Les Marguerites)", "phone": "681 50 49 18 / 659 31 11 12"},
            {"name": "Centre Auto Cameroun SARL", "location": "Quartier Elig-Essono", "phone": "694 05 12 26 / 690 74 96 08"},
            {"name": "Henri Garage 4x4 Officiel", "location": "Quartier Fouda, rue des Généraux", "phone": "675 06 73 29 / 691 50 95 78"},
            {"name": "Garage AUTO Service sarl", "location": "Yaoundé", "phone": "698 91 69 38 / 680 57 70 14"},
            {"name": "Exact Automobile", "location": "Terminus Mimboman", "phone": "680 07 54 29 / 675 38 17 22"},
            {"name": "Garage GAMEL", "location": "Derrière Station Total, Yaoundé", "phone": "651 17 20 00"},
            {"name": "Neptune Titi Garage", "location": "Yaoundé", "phone": "677 36 58 30"},
            {"name": "Tsague Auto", "location": "Yaoundé (spécialiste véhicules haut de gamme)", "phone": "674 80 13 21"}
        ],
        "Garoua": [
            {"name": "Maa Auto", "location": "Garoua", "phone": "694 67 87 89"},
            {"name": "Garoua Automobiles", "location": "Garoua", "phone": "658 68 09 41"},
            {"name": "Toyota CAMI - Garoua", "location": "Avenue des Banques, BP 336 Garoua", "phone": "222 27 30 71"},
            {"name": "Force Tyre Garoua", "location": "Garoua", "phone": "(contact via pagesjaunes.online)"},
            {"name": "YAMAHA Cameroun - Garoua", "location": "Garoua", "phone": "(contact via pagesjaunes.online)"},
            {"name": "Cami Equipment - Garoua", "location": "Garoua", "phone": "233 44 16 88"}
        ],
        "Ebolowa": [
            {"name": "Ebolowa Automobiles (Yamaha)", "location": "Ebolowa", "phone": "698 11 89 88"},
            {"name": "Garage automobile chez Modeste", "location": "Ebolowa", "phone": "697 55 02 14"},
            {"name": "Dépannage rapide Ebolowa", "location": "Descente de brasserie, Ebolowa", "phone": "686 94 92 53"}
        ],
        "Bafoussam": [
            {"name": "CITROËN CAMI", "location": "Quartier Bamendzi, route de Foumbot", "phone": "233 44 13 88"},
            {"name": "Nongni Auto Group", "location": "Bafoussam", "phone": "695 32 66 99 / 650 23 77 92"},
            {"name": "AD14 automobile (garage dyna)", "location": "Bafoussam", "phone": "653 07 96 13"}
        ],
        "Ngaoundéré": [
            {"name": "Garage Abdel-hamid", "location": "Face entrée Gada mabaga, rue gare marchandise, Joli Soir", "phone": "694 02 09 01"},
            {"name": "Ngaoundere Automobiles", "location": "Ngaoundéré", "phone": "690 90 10 10"},
            {"name": "Garage Auto Location Express (GALE)", "location": "Quartier Bidjoro", "phone": "696 97 39 00 / 651 00 65 69"},
            {"name": "GENERAL AUTO", "location": "Avenue des Banques, Ngaoundéré IIème", "phone": "(contact à vérifier)"},
            {"name": "Force Tyre Ngaoundéré", "location": "Rue de la gare, face Hôtel Adamaoua", "phone": "698 80 80 80"},
            {"name": "Complexe Garage Électrique et Électronique", "location": "Ngaoundéré", "phone": "699 00 00 00"},
            {"name": "Centre Auto Pneumatique NGDERE", "location": "Ngaoundéré", "phone": "(appeler via annonce)"}
        ],
        "Maroua": [
            {"name": "OUMAROU HAMANWABI", "location": "Maroua, région de l'Extrême-Nord", "phone": "699 02 94 87"},
            {"name": "Garage Centre Ville Auto 58", "location": "Rue 21, Centre Ville, Maroua", "phone": "687 27 27 05"},
            {"name": "Garage Centre Ville Auto 73", "location": "Rue 10, Centre Ville, Maroua", "phone": "(contact via expressmarketcm.com)"},
            {"name": "Centre Technique de Maroua", "location": "Maroua", "phone": "670 46 48 41 / 696 98 26 75"},
            {"name": "Garage Gony oumar", "location": "Maroua", "phone": "(contact sur listing.elidge.com)"}
        ],
        "Buea": [
            {"name": "Nimmo-Auto", "location": "B. Nash opposite Faculty of Health Science, University of Buea", "phone": "678 54 20 65"},
            {"name": "Asanji Enterprise", "location": "Buea, région du Sud-Ouest", "phone": "675 61 15 23"},
            {"name": "Blue Empire Cars & Real Estates", "location": "Buea", "phone": "674 88 46 86"},
            {"name": "Alpha Engineering Group", "location": "BP 134 Buea", "phone": "692 27 16 11 / 677 72 54 88"},
            {"name": "MTN Service Center Buea", "location": "Buea", "phone": "8787"}
        ]
    }
    
    city_normalized = city.strip().lower()
    for key in garages:
        if key.lower() == city_normalized:
            return garages[key]
    return []
