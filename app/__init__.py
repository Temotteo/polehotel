import os
from flask import Flask, request, url_for
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['DEFAULT_LANG'] = os.getenv('DEFAULT_LANG', 'pt')

    # 🔹 Register blueprints
    from .blueprints.main import bp as main_bp
    from .blueprints.admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # 🔹 Detect language
    @app.before_request
    def detect_lang():
        lang = request.view_args.get('lang') if request.view_args else None
        if lang in ('pt', 'en'):
            request.lang = lang
        else:
            request.lang = app.config['DEFAULT_LANG']

    # 🔹 Inject helpers into Jinja (THIS WAS MISSING / WRONG)
    @app.context_processor
    def inject_globals():
        def with_lang(endpoint, **values):
            args = {}

            # 1️⃣ args atuais da rota (ex: lang)
            if request.view_args:
                args.update(request.view_args)

            # 2️⃣ args explícitos passados no template (ex: slug)
            args.update(values)

            # 3️⃣ garantir que lang existe
            if 'lang' not in args:
                args['lang'] = getattr(request, 'lang', 'pt')

            return url_for(endpoint, **args)

        return dict(with_lang=with_lang)

    return app
