from flask import Blueprint, jsonify, redirect, render_template, url_for, flash, request

from models.transcripts import get_all_transcripts

# Create the blueprint with no URL prefix since this is the main area of the site
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def root():
    # Redirect the root URL to the login page
    return redirect(url_for("main.login"))


@main_bp.route("/home")
def index():
    # For the home page, you might want to show some overview data
    # You can import and use your appointment functions here
    from models.appointments import get_all_appointments

    # Fetch all appointments
    appointments = get_all_appointments()

    # Get the next upcoming appointment
    next_appointment = None
    if appointments:
        next_appointment = appointments[0]

    return render_template("main/index.html", next_appointment=next_appointment)


@main_bp.route("/login")
def login():
    return render_template("main/login.html")


@main_bp.route("/search")
def search():
    return render_template("main/search.html")


# If you have search functionality in your main blueprint
@main_bp.route("/api/search")
def search_endpoint():
    keyword = request.args.get("keyword", "")

    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    # Import here to avoid circular imports
    from services.search import search_transcripts

    results = search_transcripts(keyword)

    return jsonify({"transcripts": results})
