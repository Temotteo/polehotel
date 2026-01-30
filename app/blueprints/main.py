from flask import Blueprint, render_template, request, abort

bp = Blueprint('main', __name__)

PAGES = ['index','about','rooms','dining','events','gallery','location','contact']

def tpath(page):
    lang = getattr(request, 'lang', 'pt')
    return f"{lang}/{page}.html"

@bp.route('/<lang>/quartos/<slug>')
@bp.route('/<lang>/rooms/<slug>')
def room_detail(lang, slug):

    SLUG_ALIAS = {
        "economy-double": "casal-economico",
        "standard-double": "casal-standard",
        "standard-twin": "duplo-standard",
        "executive-special": "executivo-especial",
        "executive-junior": "executivo-junior",
        "executive-master": "executivo-master",
    }

    slug = SLUG_ALIAS.get(slug, slug)

    rooms = {
        "casal-economico": {
            "pt": {
                "name": "Casal Económico",
                "desc": "Opção funcional e confortável para estadias práticas.",
                "features": ["Cama de casal", "Ar condicionado", "Wi-Fi", "Casa de banho privativa"],
                "gallery": ["E1.jpg", "E2.jpg", "E3.jpg"]
            },
            "en": {
                "name": "Economy Double",
                "desc": "Functional and comfortable option for practical stays.",
                "features": ["Double bed", "Air conditioning", "Wi-Fi", "Private bathroom"],
                "gallery": ["E1.jpg", "E2.jpg", "E3.jpg"]
            },
            "img": "room1.jpg"
        },

        "casal-standard": {
            "pt": {
                "name": "Casal Standard",
                "desc": "Conforto equilibrado com design acolhedor.",
                "features": ["Cama de casal", "TV", "Wi-Fi", "Ar condicionado"], 
                "gallery": ["4.jpg", "5.jpg", "6.jpg"]
            },
            "en": {
                "name": "Standard Double",
                "desc": "Balanced comfort with a welcoming design.",
                "features": ["Double bed", "TV", "Wi-Fi", "Air conditioning"],
                "gallery": ["4.jpg", "5.jpg", "6.jpg"]
            },
            "img": "room2.jpg"
        },

        "duplo-standard": {
            "pt": {
                "name": "Duplo Standard",
                "desc": "Ideal para duas pessoas, com espaço e comodidade.",
                "features": ["Duas camas", "TV", "Wi-Fi", "Ar condicionado"],
                "gallery": ["7.jpg", "8.jpg", "9.jpg"]
            },
            "en": {
                "name": "Standard Twin",
                "desc": "Ideal for two guests with space and comfort.",
                "features": ["Twin beds", "TV", "Wi-Fi", "Air conditioning"],
                "gallery": ["7.jpg", "8.jpg", "9.jpg"]
            },
            "img": "room3.jpg"
        },

        "executivo-especial": {
            "pt": {
                "name": "Executivo Especial",
                "desc": "Categoria superior com detalhes premium.",
                "features": ["Cama queen", "Mini-bar", "Secretária", "Wi-Fi"]
            },
            "en": {
                "name": "Executive Special",
                "desc": "Premium category with refined details.",
                "features": ["Queen bed", "Mini-bar", "Desk", "Wi-Fi"]
            },
            "img": "room4.jpg"
        },

        "executivo-junior": {
            "pt": {
                "name": "Executivo Junior",
                "desc": "Ambiente amplo, ideal para estadias prolongadas.",
                "features": ["Área de estar", "Cama queen", "Wi-Fi", "Ar condicionado"]
            },
            "en": {
                "name": "Executive Junior",
                "desc": "Spacious layout, ideal for longer stays.",
                "features": ["Seating area", "Queen bed", "Wi-Fi", "Air conditioning"]
            },
            "img": "room5.jpg"
        },

        "executivo-master": {
            "pt": {
                "name": "Executivo Master",
                "desc": "Experiência exclusiva com máximo conforto e elegância.",
                "features": ["Suite premium", "Sala de estar", "Mini-bar", "Vista privilegiada"]
            },
            "en": {
                "name": "Executive Master",
                "desc": "Exclusive experience with maximum comfort and elegance.",
                "features": ["Premium suite", "Living area", "Mini-bar", "Premium view"]
            },
            "img": "room6.jpg"
        }
    }

    room = rooms.get(slug)
    if not room:
        abort(404)

    content = room.get(lang, room["pt"])
    return render_template(
        f"{lang}/room_detail.html",
        room=content,
        img=room["img"]
    )


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

#@bp.route('/<lang>/rooms')
#def rooms(lang):
#    return render_template(tpath('rooms'))

@bp.route('/<lang>/rooms')
@bp.route('/<lang>/rooms/')
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

@bp.route('/<lang>/private-lounge')
def private_lounge(lang):
    return render_template(tpath('private_lounge'))

@bp.route('/<lang>/booking', methods=['GET','POST'])
def booking(lang):
    return render_template(tpath('booking'))
