import os

from flask import Blueprint, abort, render_template, request, redirect, flash, url_for, send_from_directory, jsonify

from ..config import BASE_DIR, CODES_SITE_URL, SITE_URL
from ..db import save_contact
from ..notifications import send_discord_notification_async

main_bp = Blueprint("main", __name__)


def _is_ajax_request():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _notification_request_context():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (request.remote_addr or "Unknown")
    return {
        "ip_address": ip_address,
        "source_url": request.url,
        "user_agent": request.headers.get("User-Agent", "Unknown")
    }


@main_bp.route("/contact", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if save_contact(name, email, message):
            success_message = "Your message has been sent successfully!"
            flash(success_message, "success")
            send_discord_notification_async("contact", {
                "name": name,
                "email": email,
                "message": message,
                **_notification_request_context()
            })
            if _is_ajax_request():
                return jsonify({"ok": True, "message": success_message}), 200
        else:
            error_message = "An error occurred. Please try again."
            flash(error_message, "error")
            if _is_ajax_request():
                return jsonify({"ok": False, "message": error_message}), 500

        return redirect(url_for('main.contact_us'))

    return render_template("contact.html")


@main_bp.route("/images/<filename>")
def get_image(filename):
    images_dir = os.path.join(BASE_DIR, "static", "images")
    if not os.path.exists(os.path.join(images_dir, filename)):
        abort(404)
    return send_from_directory(images_dir, filename)


@main_bp.route("/robots.txt")
def robots():
    return send_from_directory(BASE_DIR, "robots.txt")


@main_bp.route("/sitemap.xml")
def sitemap():
    return send_from_directory(BASE_DIR, "sitemap.xml")


@main_bp.route("/sitemap")
def sitemap_html():
    return render_template("sitemap.html", site_url=SITE_URL, codes_site_url=CODES_SITE_URL)


@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.route("/terms")
def terms():
    return render_template("terms.html")


@main_bp.route("/ads.txt")
def ads_txt():
    return send_from_directory(BASE_DIR, "ads.txt")


@main_bp.route("/3fae365259364fc18250c434fb1477f0.txt")
def bing_site_verification():
    return send_from_directory(BASE_DIR, "3fae365259364fc18250c434fb1477f0.txt")
