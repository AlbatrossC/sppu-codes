from flask import Blueprint, render_template, request, redirect, flash, url_for, send_from_directory, abort
import os
from ..db import save_submission, save_contact
from ..notifications import send_discord_notification
from ..config import BASE_DIR

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/submit", methods=["GET", "POST"])
def submit_code():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        year = request.form.get("year")
        branch = request.form.get("branch")
        subject = request.form.get("subject")
        question = request.form.get("question")
        answer = request.form.get("answer")

        if save_submission(name, year, branch, subject, question, answer):
            flash("Your code has been submitted successfully! It will be reviewed shortly.", "success")
            send_discord_notification("submit", {
                "name": name,
                "year": year,
                "branch": branch,
                "subject": subject
            })
        else:
            flash("An error occurred while saving your submission. Please try again.", "error")

        return redirect(url_for('main.submit_code'))

    return render_template("submit.html")

@main_bp.route("/contact", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if save_contact(name, email, message):
            flash("Your message has been sent successfully!", "success")
            send_discord_notification("contact", {
                "name": name,
                "email": email,
                "message": message
            })
        else:
            flash("An error occurred. Please try again.", "error")

        return redirect(url_for('main.contact_us'))

    return render_template("contact.html")

# Static files and SEO
@main_bp.route("/images/<filename>")
def get_image(filename):
    images_dir = os.path.join(BASE_DIR, "images")
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
    return render_template("sitemap.html")

@main_bp.route("/ads.txt")
def ads_txt():
    return send_from_directory(BASE_DIR, "ads.txt")

@main_bp.route("/3fae365259364fc18250c434fb1477f0.txt")
def bing_site_verification():
    return send_from_directory(BASE_DIR, "3fae365259364fc18250c434fb1477f0.txt")
