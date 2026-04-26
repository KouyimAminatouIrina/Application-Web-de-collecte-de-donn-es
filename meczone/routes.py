from flask import render_template, request, redirect, url_for
from meczone.models import diagnose_problem, save_report, get_all_reports, get_city_stats, get_city_list, get_city_analytics, get_national_analytics


def register_routes(app):
    """Enregistre toutes les routes de l'application."""

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit():
        name = request.form.get("name", "Anonyme").strip()
        city = request.form.get("city", "").strip()
        vehicle_model = request.form.get("vehicle_model", "").strip()
        vehicle_year = request.form.get("vehicle_year", "").strip()
        problem_description = request.form.get("problem_description", "").strip()

        if not city or not vehicle_year or not problem_description:
            return redirect(url_for("index"))

        cause, solution = diagnose_problem(problem_description)
        save_report(name, city, vehicle_model, vehicle_year, problem_description, cause, solution)

        return render_template(
            "results.html",
            name=name,
            city=city,
            vehicle_model=vehicle_model,
            vehicle_year=vehicle_year,
            problem_description=problem_description,
            cause=cause,
            solution=solution
        )

    @app.route("/analysis", methods=["GET", "POST"])
    def analysis():
        cities = get_city_list()
        selected_city = request.form.get("city") or (cities[0] if cities else None)
        
        if selected_city:
            stats = get_city_analytics(selected_city)
            total_reports = len(get_all_reports())
            city_counts = get_city_stats()
        else:
            stats = None
            total_reports = 0
            city_counts = {}
        
        national_stats = get_national_analytics()
        
        return render_template(
            "analysis.html",
            reports=get_all_reports(),
            city_counts=city_counts,
            total_reports=total_reports,
            cities=cities,
            selected_city=selected_city,
            stats=stats,
            national_stats=national_stats
        )
