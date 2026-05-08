import os

from flask import Blueprint, abort, render_template, send_from_directory

from ..config import BASE_DIR, CODES_SITE_URL, SITE_URL

main_bp = Blueprint("main", __name__)


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
