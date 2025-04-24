# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

from datetime import datetime
from collections import OrderedDict

from flask import Blueprint, render_template, jsonify, request

from models.appointments import (
    get_all_appointments,
    get_appointment,
    save_appointment,
    update_appointment,
    delete_appointment,
)

# Create the blueprint
appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


# Use appointment_bp.route instead of app.route
@appointment_bp.route("/")
def appointments():
    """Render the appointments page, displaying appointments grouped by month."""
    # Fetch appointments from your database
    appointments = get_all_appointments()

    # Group appointments by month
    appointments_by_month = {}

    for appointment in appointments:
        date_str = appointment["date"]
        date_obj = datetime.strptime(date_str, "%a, %b %d, %Y, %I:%M %p")
        month_year = date_obj.strftime("%B %Y")  # "April 2025"

        if month_year not in appointments_by_month:
            appointments_by_month[month_year] = []

        appointments_by_month[month_year].append(appointment)

    # Sort the months chronologically
    sorted_appointments = OrderedDict()

    # Get list of (month_year, date_obj) tuples for sorting
    month_dates = []
    for month_year in appointments_by_month:
        # Extract first date of month for sorting
        first_date = datetime.strptime(month_year, "%B %Y")
        month_dates.append((month_year, first_date))

    # Sort by date
    sorted_month_dates = sorted(month_dates, key=lambda x: x[1])

    # Create ordered dictionary
    for month_year, _ in sorted_month_dates:
        sorted_appointments[month_year] = appointments_by_month[month_year]

    return render_template(
        "appointments/appointments.html", appointments_by_month=sorted_appointments
    )


# API endpoint to save appointment - use the blueprint decorator
@appointment_bp.route("/save", methods=["POST"])
def save_appointment_endpoint():
    """API endpoint to save a new appointment."""
    data = request.json
    title = data.get("title")
    date = data.get("date")
    description = data.get("description", "")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not date:
        return jsonify({"error": "Date is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    appointment_id = save_appointment(
        title=title, date=date, description=description, user=user
    )

    return jsonify(
        {
            "success": True,
            "id": appointment_id,
            "title": title,
            "date": date,
            "description": description,
            "user": user,
        }
    )


@appointment_bp.route("/view/<appointment_id>")
def view_appointment(appointment_id):
    """Render a page to view a single appointment."""
    appointment = get_appointment(appointment_id)
    if not appointment:
        return "Appointment not found", 404
    return render_template(
        "appointments/view_appointment.html", appointment=appointment
    )


@appointment_bp.route("/delete/<appointment_id>", methods=["DELETE"])
def delete_appointment_endpoint(appointment_id):
    """API endpoint to delete an appointment."""
    success = delete_appointment(appointment_id)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Appointment not found"}), 404


@appointment_bp.route("/update/<appointment_id>", methods=["PUT"])
def update_appointment_endpoint(appointment_id):
    """API endpoint to update an existing appointment."""
    data = request.json
    title = data.get("title")
    date = data.get("date")
    description = data.get("description", "")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not date:
        return jsonify({"error": "Date is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    success, result = update_appointment(
        appointment_id=appointment_id,
        title=title,
        date=date,
        description=description,
        user=user,
    )

    if success:
        return jsonify({"success": True, "appointment": result})
    else:
        return jsonify({"success": False, "error": result}), 404
