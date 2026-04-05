from flask import current_app, jsonify, render_template, request

from app.models import insert_reports, fetch_recent_alerts
from app.services import (
    collect_disaster_data,
    load_sources,
    classify_reports,
    calculate_risk_summary,
    filter_by_location,
    generate_alerts,
    detect_information_gaps,
)
from app.utils import load_json_file, parse_location_input


def register_routes(app):
    @app.route("/")
    def index():
        # show user's permanent location if available (default_user used for now)
        from app.services.permanent_location import get_permanent_location

        permanent = get_permanent_location("default_user")
        return render_template("index.html", permanent_location=permanent)

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        location = _get_location_from_request()
        # pass permanent location as well so template can render button state or info
        from app.services.permanent_location import get_permanent_location
        permanent = get_permanent_location("default_user")

        # Only run the heavy data collection pipeline when we actually have
        # a location to analyze. This keeps the initial dashboard page load
        # fast and defers remote API calls until the user asks for analysis.
        if location:
            context = _build_dashboard_context(location, persist_alerts=True)
        else:
            context = {
                "location": None,
                "risk_summary": None,
                "alerts": [],
                "gaps": [],
                "reports": [],
            }
        context["permanent_location"] = permanent
        return render_template("dashboard.html", **context)

    @app.route("/guidance")
    def guidance():
        guidance_path = current_app.config["DATA_DIR"] / "guidance" / "precautions.json"
        precautions = load_json_file(guidance_path, default={"types": {}}).get("types", {})
        return render_template("guidance.html", precautions=precautions)

    @app.route("/alerts")
    def alerts():
        stored_alerts = fetch_recent_alerts(current_app.config["DB_PATH"], limit=50)
        return render_template("alerts.html", alerts=stored_alerts)

    @app.route("/help")
    def help_page():
        """Render a list of emergency contact numbers.

        Contacts are defined in a JSON file under :data:`DATA_DIR` (``contacts.json``).
        If the file is missing or empty we fall back to a small hard‑coded list of
        Pakistan emergency numbers so the page is still useful even in tests or
        freshly cloned repositories.
        """
        contacts_path = current_app.config["DATA_DIR"] / "contacts.json"
        data = load_json_file(contacts_path, default={"contacts": []})
        contacts = data.get("contacts", [])
        return render_template("help.html", contacts=contacts)

    @app.route("/api/risk", methods=["GET"])
    def api_risk():
        location = request.args.get("location")
        context = _build_dashboard_context(location, persist_alerts=False)
        return jsonify(
            {
                "location": location,
                "risk_summary": context.get("risk_summary"),
                "alerts": context.get("alerts"),
                "gaps": context.get("gaps"),
            }
        )

    # permanent location CRUD API
    @app.route("/api/permanent-location", methods=["GET"])
    def api_get_permanent_location():
        user_id = request.args.get("user_id")
        from app.services.permanent_location import get_permanent_location

        loc = get_permanent_location(user_id or "default_user")
        if loc:
            return jsonify(loc)
        return jsonify({}), 404

    @app.route("/api/permanent-location", methods=["POST"])
    def api_set_permanent_location():
        data = request.get_json() or {}
        user_id = data.get("user_id", "default_user")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        name = data.get("location_name", "")
        from app.services.permanent_location import set_permanent_location

        try:
            set_permanent_location(user_id, float(latitude), float(longitude), name)
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/permanent-location", methods=["DELETE"])
    def api_delete_permanent_location():
        data = request.get_json() or {}
        user_id = data.get("user_id", "default_user")
        from app.services.permanent_location import delete_permanent_location

        delete_permanent_location(user_id)
        return jsonify({"status": "deleted"})


def _get_location_from_request():
    if request.method == "POST":
        location = request.form.get("location")
    else:
        location = request.args.get("location")

    parsed = parse_location_input(location)
    return parsed.get("text")


def _build_dashboard_context(location, persist_alerts=False):
    if current_app.config.get("DISABLE_REMOTE_FETCH"):
        sources = []
    else:
        sources_path = current_app.config["DATA_DIR"] / "sources" / "data_sources.json"
        sources = load_sources(sources_path)

    collected = collect_disaster_data(
        sources, user_agent=current_app.config.get("NWS_USER_AGENT")
    )
    classified = classify_reports(collected)
    filtered = filter_by_location(classified, location)

    insert_reports(current_app.config["DB_PATH"], filtered)

    risk_summary = calculate_risk_summary(
        filtered,
        window_days=current_app.config["RISK_WINDOW_DAYS"],
        risk_points_per_report=current_app.config["RISK_POINTS_PER_REPORT"],
        medium_threshold=current_app.config["MEDIUM_RISK_THRESHOLD"],
        high_threshold=current_app.config["HIGH_RISK_THRESHOLD"],
        half_life_days=current_app.config["RISK_HALF_LIFE_DAYS"],
        severity_weights=current_app.config["SEVERITY_WEIGHTS"],
    )

    alerts = generate_alerts(
        risk_summary,
        location=location,
        persist=persist_alerts,
        db_path=current_app.config["DB_PATH"],
        dedupe_hours=current_app.config["ALERT_DEDUPE_HOURS"],
    )
    gaps = detect_information_gaps(filtered, min_reports=current_app.config["DIGD_MIN_REPORTS"])

    return {
        "location": location,
        "risk_summary": risk_summary,
        "alerts": alerts,
        "gaps": gaps,
        "reports": filtered,
    }
