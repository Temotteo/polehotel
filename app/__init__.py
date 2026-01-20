import os
from flask import Flask, redirect, request, url_for
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['DEFAULT_LANG'] = os.getenv('DEFAULT_LANG', 'pt')

    # Blueprints
    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Simple language switch via query param ?lang=pt|en
    @app.before_request
    def detect_lang():
        lang = request.args.get('lang')
        if lang in ('pt', 'en'):
            request.lang = lang
        else:
            request.lang = app.config['DEFAULT_LANG']

    # Helper to reverse with lang
    def inject_globals():
        def with_lang(endpoint, **values):
            # copia os argumentos atuais da rota (ex: slug)
            args = {}
            if request.view_args:
                args.update(request.view_args)

            # força idioma
            args['lang'] = values.get('lang', args.get('lang'))

            return url_for(endpoint, **args)
        return dict(with_lang=with_lang)
    return app
