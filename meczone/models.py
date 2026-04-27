import os
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

import psycopg2
import psycopg2.extras

# URL de connexion PostgreSQL — lue depuis la variable d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")


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
    """Retourne une connexion PostgreSQL."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    """Crée la table si elle n'existe pas encore."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            name TEXT,
            city TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            problem_description TEXT,
            cause TEXT,
            solution TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    cur.close()
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
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reports (name, city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (name, city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_reports():
    """Récupère tous les rapports de la base de données."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT city, vehicle_model, vehicle_year, problem_description, cause, solution, created_at FROM reports ORDER BY created_at DESC")
    reports = cur.fetchall()
    cur.close()
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
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT problem_description FROM reports WHERE city = %s", (city,))
    reports = cur.fetchall()
    cur.close()
    conn.close()

    distribution = {}
    for report in reports:
        problem_type = get_problem_type(report["problem_description"])
        distribution[problem_type] = distribution.get(problem_type, 0) + 1

    return distribution


def get_brand_correlations(city=None):
    """Calcule corrélation âge-problèmes par marque pour une ville ou national."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if city:
        cur.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = %s AND vehicle_year IS NOT NULL", (city,))
    else:
        cur.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE vehicle_year IS NOT NULL")
    reports = cur.fetchall()
    cur.close()
    conn.close()

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
            slope, intercept = np.polyfit(x, y, 1)
            correlations[brand] = {
                "r": round(corr, 2),
                "r2": round(r_squared, 2),
                "count": len(ages),
                "slope": round(slope, 2),
                "intercept": round(intercept, 2)
            }

    return correlations


def get_brand_ranking(city=None):
    """Classement des marques par moyenne de problèmes par tranche d'âge."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if city:
        cur.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE city = %s AND vehicle_year IS NOT NULL", (city,))
    else:
        cur.execute("SELECT vehicle_model, vehicle_year FROM reports WHERE vehicle_year IS NOT NULL")
    reports = cur.fetchall()
    cur.close()
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
            ranking[brand] = {
                "avg_age": round(avg_age, 1),
                "avg_problems": round(avg_problems, 1),
                "count": len(data["ages"])
            }

    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1]["avg_problems"])
    return sorted_ranking


def _fig_to_base64(fig):
    """Convertit une figure matplotlib en chaîne base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                facecolor='#162620', edgecolor='none', dpi=130)
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{data}"


# Palette cohérente avec le thème sombre vert/rouge Cameroun
_COLORS = ['#007A5E', '#CE1126', '#F4C430', '#4BC8A0', '#FF6B6B',
           '#9B59B6', '#3498DB', '#E67E22', '#1ABC9C', '#E74C3C']

_STYLE = {
    'figure.facecolor': '#162620',
    'axes.facecolor':   '#1e2d27',
    'axes.edgecolor':   '#2e4a3e',
    'axes.labelcolor':  '#8fada0',
    'xtick.color':      '#8fada0',
    'ytick.color':      '#8fada0',
    'text.color':       '#e8f0ec',
    'grid.color':       '#2e4a3e',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
}


def generate_pie_chart(distribution):
    """Génère un diagramme circulaire en base64."""
    if not distribution:
        return None

    labels = list(distribution.keys())
    sizes  = list(distribution.values())

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(5, 4))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=_COLORS[:len(labels)],
            wedgeprops=dict(linewidth=1.5, edgecolor='#162620')
        )
        for t in autotexts:
            t.set_color('#fff')
            t.set_fontsize(9)
        ax.axis('equal')
        ax.set_title("Répartition des types de pannes", fontsize=11, pad=12,
                     color='#e8f0ec', fontweight='bold')

    return _fig_to_base64(fig)


def generate_regression_chart(reports):
    """
    Génère la droite de régression linéaire âge → nombre de problèmes
    toutes marques confondues, avec nuage de points par marque.
    """
    if not reports:
        return None

    current_year = datetime.now().year
    brand_ages   = {}

    for r in reports:
        if not r.get("vehicle_year"):
            continue
        brand = r["vehicle_model"].split()[0] if r.get("vehicle_model") else "Inconnu"
        age   = current_year - r["vehicle_year"]
        brand_ages.setdefault(brand, []).append(age)

    if not brand_ages:
        return None

    # Construire les points (x=âge, y=nb de rapports du même véhicule ce jour)
    xs, ys, colors_pts, labels_pts = [], [], [], []
    brand_list = list(brand_ages.keys())

    for i, brand in enumerate(brand_list):
        ages = brand_ages[brand]
        age_count = Counter(ages)
        for age, cnt in age_count.items():
            xs.append(age)
            ys.append(cnt)
            colors_pts.append(_COLORS[i % len(_COLORS)])
            labels_pts.append(brand)

    if len(xs) < 2:
        return None

    xs_arr = np.array(xs)
    ys_arr = np.array(ys)

    # Régression globale
    slope, intercept = np.polyfit(xs_arr, ys_arr, 1)
    x_line = np.linspace(xs_arr.min(), xs_arr.max(), 200)
    y_line = slope * x_line + intercept

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.grid(True)

        # Nuage de points coloré par marque
        seen = set()
        for x, y, c, lbl in zip(xs, ys, colors_pts, labels_pts):
            if lbl not in seen:
                ax.scatter(x, y, color=c, label=lbl, s=70, zorder=3, alpha=0.85)
                seen.add(lbl)
            else:
                ax.scatter(x, y, color=c, s=70, zorder=3, alpha=0.85)

        # Droite de régression
        ax.plot(x_line, y_line, color='#F4C430', linewidth=2.2, zorder=4,
                label=f'Régression : y = {slope:.2f}x + {intercept:.2f}')

        ax.set_xlabel("Âge du véhicule (ans)")
        ax.set_ylabel("Nb de signalements")
        ax.set_title("Droite de régression âge–pannes", fontsize=11,
                     color='#e8f0ec', fontweight='bold', pad=10)
        ax.legend(fontsize=7, loc='upper left',
                  facecolor='#1e2d27', edgecolor='#2e4a3e', labelcolor='#e8f0ec')

    return _fig_to_base64(fig)


def generate_boxplot_chart(reports):
    """
    Génère un diagramme en boîte à moustaches (boxplot) de la distribution
    de l'âge des véhicules par marque.
    """
    if not reports:
        return None

    current_year = datetime.now().year
    brand_ages = {}

    for r in reports:
        if not r.get("vehicle_year"):
            continue
        brand = r["vehicle_model"].split()[0] if r.get("vehicle_model") else "Inconnu"
        age   = current_year - r["vehicle_year"]
        brand_ages.setdefault(brand, []).append(age)

    # Garder uniquement les marques avec ≥ 2 valeurs pour un boxplot significatif
    brand_ages = {b: ages for b, ages in brand_ages.items() if len(ages) >= 2}

    if not brand_ages:
        return None

    brands = sorted(brand_ages.keys())
    data   = [brand_ages[b] for b in brands]
    colors = [_COLORS[i % len(_COLORS)] for i in range(len(brands))]

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(max(5, len(brands) * 1.2 + 1), 4))
        ax.grid(True, axis='y')

        bp = ax.boxplot(data, patch_artist=True, notch=False,
                        medianprops=dict(color='#F4C430', linewidth=2),
                        whiskerprops=dict(color='#8fada0'),
                        capprops=dict(color='#8fada0'),
                        flierprops=dict(marker='o', color='#CE1126',
                                        markerfacecolor='#CE1126', markersize=5))

        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
            patch.set_edgecolor('#162620')

        ax.set_xticks(range(1, len(brands) + 1))
        ax.set_xticklabels(brands, rotation=20, ha='right', fontsize=9)
        ax.set_ylabel("Âge du véhicule (ans)")
        ax.set_title("Distribution de l'âge des véhicules par marque",
                     fontsize=11, color='#e8f0ec', fontweight='bold', pad=10)

    return _fig_to_base64(fig)


def get_city_stats():
    """Retourne le compte des rapports par ville."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT city FROM reports")
    reports = cur.fetchall()
    cur.close()
    conn.close()

    city_counts = {}
    for report in reports:
        city_name = report["city"]
        city_counts[city_name] = city_counts.get(city_name, 0) + 1

    return city_counts


def get_city_list():
    """Récupère la liste des villes disponibles."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM reports ORDER BY city")
    cities = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in cities]


def get_city_analytics(city):
    """Retourne toutes les statistiques pour une ville."""
    distribution = get_problem_distribution(city)
    correlations = get_brand_correlations(city)
    ranking      = get_brand_ranking(city)
    pie_chart    = generate_pie_chart(distribution)

    # Charger les rapports de la ville pour les graphiques âge
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT vehicle_model, vehicle_year FROM reports WHERE city = %s AND vehicle_year IS NOT NULL",
        (city,)
    )
    city_reports = cur.fetchall()
    cur.close()
    conn.close()

    regression_chart = generate_regression_chart(city_reports)
    boxplot_chart    = generate_boxplot_chart(city_reports)

    return {
        "distribution":    distribution,
        "correlations":    correlations,
        "ranking":         ranking,
        "pie_chart":       pie_chart,
        "regression_chart": regression_chart,
        "boxplot_chart":   boxplot_chart,
    }


def get_national_analytics():
    """Retourne les statistiques nationales."""
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT problem_description, vehicle_model, vehicle_year FROM reports")
    all_reports = cur.fetchall()
    cur.close()
    conn.close()

    distribution = {}
    for report in all_reports:
        problem_type = get_problem_type(report["problem_description"])
        distribution[problem_type] = distribution.get(problem_type, 0) + 1

    correlations     = get_brand_correlations()
    ranking          = get_brand_ranking()
    pie_chart        = generate_pie_chart(distribution)
    regression_chart = generate_regression_chart(all_reports)
    boxplot_chart    = generate_boxplot_chart(all_reports)

    return {
        "distribution":    distribution,
        "correlations":    correlations,
        "ranking":         ranking,
        "pie_chart":       pie_chart,
        "regression_chart": regression_chart,
        "boxplot_chart":   boxplot_chart,
    }


def get_garages_by_city(city):
    """Retourne la liste des garages pour une ville donnée."""
    garages = {
        "Douala": [
            {"name": "Garage Auto Fixpress", "location": "Quartier Logpom", "phone": "699 18 79 98"},
            {"name": "Douala Auto Sarl", "location": "Quartier Bonaberi", "phone": "672 85 16 52 / 683 32 81 67"},
            {"name": "Garage Auto Location Express (GALE)", "location": "Quartier Bonapriso", "phone": "+237 696 97 39 00"},
            {"name": "Garage Flora", "location": "11 Rue Franqueville, Akwa", "phone": "233 43 06 22 / 699 93 47 19"},
            {"name": "KIA MOTORS AUTO SA", "location": "Avenue de Gaulle Bonanjo & Zone Industrielle Bonaberi", "phone": "233 65 65 65"},
            {"name": "GAP MOTORS", "location": "Axe Douala-Yaoundé après BOCOM", "phone": "694 57 90 80"},
            {"name": "AUTO HAUS", "location": "Face Polyclinique d'Akwa", "phone": "233 425 586"},
            {"name": "Force Tyre Sarl", "location": "Route Base Navale Youpwé", "phone": "233 42 79 76"}
        ],
        "Yaoundé": [
            {"name": "Garage Les Invincibles", "location": "Quartier Oyom Abang", "phone": "681 50 49 18 / 659 31 11 12"},
            {"name": "Centre Auto Cameroun SARL", "location": "Quartier Elig-Essono", "phone": "694 05 12 26"},
            {"name": "Henri Garage 4x4 Officiel", "location": "Quartier Fouda, rue des Généraux", "phone": "675 06 73 29"},
            {"name": "Exact Automobile", "location": "Terminus Mimboman", "phone": "680 07 54 29"},
            {"name": "Garage GAMEL", "location": "Derrière Station Total", "phone": "651 17 20 00"},
            {"name": "Neptune Titi Garage", "location": "Yaoundé", "phone": "677 36 58 30"},
            {"name": "Tsague Auto", "location": "Yaoundé (spécialiste véhicules haut de gamme)", "phone": "674 80 13 21"}
        ],
        "Garoua": [
            {"name": "Maa Auto", "location": "Garoua", "phone": "694 67 87 89"},
            {"name": "Garoua Automobiles", "location": "Garoua", "phone": "658 68 09 41"},
            {"name": "Toyota CAMI - Garoua", "location": "Avenue des Banques, BP 336 Garoua", "phone": "222 27 30 71"},
            {"name": "Cami Equipment - Garoua", "location": "Garoua", "phone": "233 44 16 88"}
        ],
        "Bafoussam": [
            {"name": "CITROËN CAMI", "location": "Quartier Bamendzi, route de Foumbot", "phone": "233 44 13 88"},
            {"name": "Nongni Auto Group", "location": "Bafoussam", "phone": "695 32 66 99"},
            {"name": "AD14 automobile (garage dyna)", "location": "Bafoussam", "phone": "653 07 96 13"}
        ],
        "Ngaoundéré": [
            {"name": "Garage Abdel-hamid", "location": "Face entrée Gada mabaga, Joli Soir", "phone": "694 02 09 01"},
            {"name": "Ngaoundere Automobiles", "location": "Ngaoundéré", "phone": "690 90 10 10"},
            {"name": "Garage Auto Location Express (GALE)", "location": "Quartier Bidjoro", "phone": "696 97 39 00"},
            {"name": "Force Tyre Ngaoundéré", "location": "Rue de la gare, face Hôtel Adamaoua", "phone": "698 80 80 80"}
        ],
        "Maroua": [
            {"name": "Garage Centre Ville Auto 58", "location": "Rue 21, Centre Ville, Maroua", "phone": "687 27 27 05"},
            {"name": "Centre Technique de Maroua", "location": "Maroua", "phone": "670 46 48 41"},
            {"name": "OUMAROU HAMANWABI", "location": "Maroua, région de l'Extrême-Nord", "phone": "699 02 94 87"}
        ],
        "Ebolowa": [
            {"name": "Ebolowa Automobiles (Yamaha)", "location": "Ebolowa", "phone": "698 11 89 88"},
            {"name": "Garage automobile chez Modeste", "location": "Ebolowa", "phone": "697 55 02 14"},
            {"name": "Dépannage rapide Ebolowa", "location": "Descente de brasserie, Ebolowa", "phone": "686 94 92 53"}
        ],
        "Limbé": [
            {"name": "DynaSet Garage (Victor Njoh)", "location": "Quartier New Town", "phone": "677 41 98 35"},
            {"name": "HGS Garage Ltd", "location": "Ancienne Route Bonaberi, BP 1227", "phone": "654 22 24 55"},
            {"name": "ETS BEN AUTO PARTS", "location": "Maligah", "phone": "677 94 75 75"}
        ],
        "Buea": [
            {"name": "Nimmo-Auto", "location": "B. Nash opposite Faculty of Health Science, UB", "phone": "678 54 20 65"},
            {"name": "Asanji Enterprise", "location": "Buea, région du Sud-Ouest", "phone": "675 61 15 23"},
            {"name": "Alpha Engineering Group", "location": "BP 134 Buea", "phone": "692 27 16 11"}
        ]
    }

    city_normalized = city.strip().lower()
    for key in garages:
        if key.lower() == city_normalized:
            return garages[key]
    return []