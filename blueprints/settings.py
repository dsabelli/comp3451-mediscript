# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.settings import get_settings, save_settings

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
def settings():
    """View and update application settings."""
    if request.method == "POST":
        current_settings = get_settings()

        # Update theme
        theme = request.form.get("theme", "light")
        current_settings["theme"] = theme

        if save_settings(current_settings):
            flash("Settings saved successfully!", "success")
        else:
            flash("Failed to save settings.", "error")

        return redirect(url_for(".settings"))  # Use relative URL for blueprint

    # GET request
    settings_data = get_settings()
    return render_template("settings/settings.html", settings=settings_data)


# make the theme available in all templates within this blueprint (or the app if registered)
@settings_bp.context_processor
def inject_settings():
    """Inject the 'theme' setting into all templates."""
    settings_data = get_settings()
    return dict(theme=settings_data.get("theme", "light"))  # Use .get() for safety
