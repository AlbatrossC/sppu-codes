from flask import Blueprint, render_template, request, redirect, flash, url_for, send_from_directory, abort, jsonify, make_response
import os
from ..db import save_submission, save_contact
from ..notifications import send_discord_notification_async
from ..config import BASE_DIR, SITE_URL, QUESTIONS_DIR
from ..utils import load_subject_data

main_bp = Blueprint('main', __name__)


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

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/submit", methods=["GET", "POST"])
def submit_code():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject")
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer") or request.form.get("code")

        if save_submission(name, email, subject, question, answer):
            flash("Your code has been submitted successfully! It will be reviewed shortly.", "success")
            send_discord_notification_async("submit", {
                "name": name,
                "email": email or "Not provided",
                "subject": subject,
                "question": question,
                "code_length": len(answer or ""),
                **_notification_request_context()
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

# Static files and SEO
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
    """Generate dynamic XML sitemap with all subjects and questions."""
    urls = []
    
    # Home page - highest priority
    urls.append({
        "loc": f"{SITE_URL}/",
        "priority": "1.0",
        "changefreq": "weekly"
    })
    
    # Static pages
    urls.append({
        "loc": f"{SITE_URL}/submit",
        "priority": "0.8",
        "changefreq": "monthly"
    })
    urls.append({
        "loc": f"{SITE_URL}/contact",
        "priority": "0.8",
        "changefreq": "monthly"
    })
    
    # Get all subject JSON files
    if os.path.exists(QUESTIONS_DIR):
        for filename in os.listdir(QUESTIONS_DIR):
            if filename.endswith(".json"):
                subject_code = filename[:-5]  # Remove .json extension
                subject_data = load_subject_data(subject_code)
                
                if subject_data:
                    # Subject listing page - high priority
                    urls.append({
                        "loc": f"{SITE_URL}/{subject_code}",
                        "priority": "0.9",
                        "changefreq": "weekly"
                    })
                    
                    # Individual question pages - top priority
                    questions = subject_data.get("questions", [])
                    for question in questions:
                        question_id = question.get("id")
                        if question_id:
                            urls.append({
                                "loc": f"{SITE_URL}/{subject_code}/{question_id}",
                                "priority": "1.0",
                                "changefreq": "monthly"
                            })
    
    # Build XML
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url['loc']}</loc>")
        xml_lines.append(f"    <lastmod>2026-05-09</lastmod>")
        xml_lines.append(f"    <priority>{url['priority']}</priority>")
        xml_lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        xml_lines.append("  </url>")
    
    xml_lines.append("</urlset>")
    
    response = make_response("\n".join(xml_lines))
    response.headers["Content-Type"] = "application/xml"
    return response

@main_bp.route("/sw.js")
def service_worker():
    response = send_from_directory(BASE_DIR, "sw.js")
    response.headers['Cache-Control'] = 'no-cache'
    return response

@main_bp.route("/sitemap")
def sitemap_html():
    return render_template("sitemap.html")

@main_bp.route("/ads.txt")
def ads_txt():
    return send_from_directory(BASE_DIR, "ads.txt")

@main_bp.route("/3fae365259364fc18250c434fb1477f0.txt")
def bing_site_verification():
    return send_from_directory(BASE_DIR, "3fae365259364fc18250c434fb1477f0.txt")
