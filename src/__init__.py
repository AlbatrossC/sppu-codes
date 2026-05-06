from flask import Flask, render_template, request, redirect
from flask_compress import Compress
from werkzeug.exceptions import HTTPException

def create_app():
    from .config import SECRET_KEY, MAINTENANCE_MODE, MICROSOFT_CLARITY_ID, GOOGLE_ANALYTICS_ID
    from .async_logger import api_logger
    from .db import init_db
    from .utils import preload_subject_cache

    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = SECRET_KEY
    Compress(app)
    init_db()
    api_logger.start()
    preload_subject_cache()

    @app.context_processor
    def inject_app_config():
        return {
            "microsoft_clarity_id": MICROSOFT_CLARITY_ID,
            "google_analytics_id": GOOGLE_ANALYTICS_ID,
        }

    # Context processors and before_request handlers
    @app.before_request
    def maintenance():
        if MAINTENANCE_MODE:
            if request.path.startswith("/static") or request.path.startswith("/images"):
                return
            return render_template("maintenance.html"), 503

    @app.before_request
    def questionpapers_redirect():
        path = request.path
        if path == "/questionpapers":
            return redirect("/question-papers", code=301)
        if path.startswith("/questionpapers/"):
            return redirect("/question-papers" + path[len("/questionpapers"):], code=301)

    @app.after_request
    def add_asset_cache_headers(response):
        path = request.path
        if path.startswith("/static/fonts/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        path = request.path
        app.logger.info(f"404 Not Found: {path} from {request.remote_addr}")
        return render_template("error.html", error_code=404, requested_path=path), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception(f"500 Internal Server Error at {request.path}")
        error_message = str(e) if app.debug else None
        return render_template("error.html", error_code=500, error_message=error_message), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        code = getattr(e, 'code', 500) or 500
        description = getattr(e, 'description', '')
        app.logger.warning(f"HTTP {code} {e.name} for path {request.path} from {request.remote_addr}")
        return render_template("error.html", error_code=code, error_message=description, requested_path=request.path), code

    # Register blueprints
    from .routes.main import main_bp
    from .routes.question_papers import question_papers_bp
    from .routes.subjects import subjects_bp
    from .routes.api import api_bp, raw_api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(question_papers_bp)
    app.register_blueprint(api_bp)  # /api
    app.register_blueprint(raw_api_bp) # /raw-answers
    app.register_blueprint(subjects_bp)  # Register subjects_bp last because of catch-all /<subject_link>

    return app
