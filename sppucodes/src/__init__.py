from flask import Flask, render_template, request, redirect
from flask_compress import Compress
from werkzeug.exceptions import HTTPException


def create_app():
    from .config import SECRET_KEY, MAINTENANCE_MODE, QUESTION_PAPERS_SITE_URL
    from .async_logger import api_logger
    from .db import init_db
    from .utils import preload_subject_cache

    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = SECRET_KEY
    Compress(app)
    init_db()
    api_logger.start()
    preload_subject_cache()

    @app.before_request
    def maintenance():
        if MAINTENANCE_MODE:
            if request.path.startswith("/static") or request.path.startswith("/images"):
                return None
            return render_template("maintenance.html"), 503
        return None

    @app.before_request
    def questionpapers_redirect():
        path = request.path.rstrip("/")
        if path in {"/questionpapers", "/question-papers"}:
            return redirect(f"{QUESTION_PAPERS_SITE_URL}/", code=301)
        if request.path.startswith("/questionpapers/"):
            slug = request.path[len("/questionpapers/"):]
            return redirect(f"{QUESTION_PAPERS_SITE_URL}/{slug}", code=301)
        if request.path.startswith("/question-papers/"):
            slug = request.path[len("/question-papers/"):]
            return redirect(f"{QUESTION_PAPERS_SITE_URL}/{slug}", code=301)
        return None

    @app.after_request
    def add_asset_cache_headers(response):
        if request.path.startswith("/static/fonts/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        path = request.path
        app.logger.info(f"404 Not Found: {path} from {request.remote_addr}")
        return render_template("error.html", error_code=404, requested_path=path), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception(f"500 Internal Server Error at {request.path}")
        error_message = str(error) if app.debug else None
        return render_template("error.html", error_code=500, error_message=error_message), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        code = getattr(error, "code", 500) or 500
        description = getattr(error, "description", "")
        app.logger.warning(f"HTTP {code} {error.name} for path {request.path} from {request.remote_addr}")
        return render_template(
            "error.html",
            error_code=code,
            error_message=description,
            requested_path=request.path,
        ), code

    from .routes.main import main_bp
    from .routes.subjects import subjects_bp
    from .routes.api import api_bp, raw_api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(raw_api_bp)
    app.register_blueprint(subjects_bp)

    return app
