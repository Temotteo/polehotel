from flask import Blueprint, render_template, request

bp = Blueprint('main', __name__)

PAGES = ['index','about','rooms','dining','events','gallery','location','contact']

def tpath(page):
    lang = getattr(request, 'lang', 'pt')
    return f"{lang}/{page}.html"

@bp.route('/')
def home_redirect():
    # Redirect to default language home
    from flask import current_app, redirect, url_for
    return redirect(url_for('main.index', lang=current_app.config.get('DEFAULT_LANG','pt')))

@bp.route('/<lang>/')
def index(lang):
    return render_template(tpath('index'))

@bp.route('/<lang>/about')
def about(lang):
    return render_template(tpath('about'))

@bp.route('/<lang>/rooms')
def rooms(lang):
    return render_template(tpath('rooms'))

@bp.route('/<lang>/dining')
def dining(lang):
    return render_template(tpath('dining'))

@bp.route('/<lang>/events', methods=['GET','POST'])
def events(lang):
    # TODO: handle budget request form submission (email/db)
    return render_template(tpath('events'))

@bp.route('/<lang>/gallery')
def gallery(lang):
    return render_template(tpath('gallery'))

@bp.route('/<lang>/location')
def location(lang):
    return render_template(tpath('location'))

@bp.route('/<lang>/contact', methods=['GET','POST'])
def contact(lang):
    # TODO: handle contact form submission (email/WhatsApp)
    return render_template(tpath('contact'))
