from flask import Blueprint, render_template, request, abort, flash, redirect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===============================
# CONFIGURAÇÃO DE EMAIL (GMAIL)
# ===============================

EMAIL_REMETENTE = "noreplythisemail100@gmail.com"
EMAIL_SENHA = "cpjxewnfvescnghy"
EMAIL_DESTINO = "amilcarfernandes1967@gmail.com"
EMAIL_DESTINOS = ["amilcarfernandes1967@gmail.com", "dmicasmouse01@gmail.com"]

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
                "features": ["Cama queen", "Mini-bar", "Secretária", "Wi-Fi"],
                "gallery": ["10.jpg", "11.jpg", "12.jpg"]
            },
            "en": {
                "name": "Executive Special",
                "desc": "Premium category with refined details.",
                "features": ["Queen bed", "Mini-bar", "Desk", "Wi-Fi"],
                "gallery": ["10.jpg", "11.jpg", "12.jpg"]
            },
            "img": "room4.jpg"
        },

        "executivo-junior": {
            "pt": {
                "name": "Executivo Junior",
                "desc": "Ambiente amplo, ideal para estadias prolongadas.",
                "features": ["Área de estar", "Cama queen", "Wi-Fi", "Ar condicionado"],
                "gallery": ["13.jpg", "14.jpg", "15.jpg"]
            },
            "en": {
                "name": "Executive Junior",
                "desc": "Spacious layout, ideal for longer stays.",
                "features": ["Seating area", "Queen bed", "Wi-Fi", "Air conditioning"],
                "gallery": ["13.jpg", "14.jpg", "15.jpg"]
            },
            "img": "room5.jpg"
        },

        "executivo-master": {
            "pt": {
                "name": "Executivo Master",
                "desc": "Experiência exclusiva com máximo conforto e elegância.",
                "features": ["Suite premium", "Sala de estar", "Mini-bar", "Vista privilegiada"],
                "gallery": ["16.jpg", "17.jpg", "18.jpg"]
            },
            "en": {
                "name": "Executive Master",
                "desc": "Exclusive experience with maximum comfort and elegance.",
                "features": ["Premium suite", "Living area", "Mini-bar", "Premium view"],
                "gallery": ["16.jpg", "17.jpg", "18.jpg"]
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


@bp.route('/<lang>/', methods=['GET','POST'])  # ou a rota correta da home
def home(lang):
    if request.method == "POST":
        # Captura do email
        email = request.form.get("email")
        
        # Captura dos interesses (lista)
        interesses = request.form.getlist("interesse")  # getlist para múltiplos checkbox

        try:
            # Corpo do email em HTML
            corpo_html = f"""
            <html>
            <body>
                <p><b>POLE HOTEL - Novo email de Interesse</b><br>
                <b>Email:</b> {email}<br>
                <b>Interesses selecionados:</b> {', '.join(interesses) if interesses else 'Nenhum'}</p>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg["From"] = EMAIL_REMETENTE
            if isinstance(EMAIL_DESTINOS, list):
                msg["To"] = ", ".join(EMAIL_DESTINOS)
            else:
                msg["To"] = EMAIL_DESTINO

            msg["Subject"] = "POLE HOTEL - Novo email de Interesse"
            msg.attach(MIMEText(corpo_html, "html"))

            # Envio via SMTP
            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(msg)
            servidor.quit()

            flash("Email de interesse enviado com sucesso!") if lang=="pt" else flash("Interest email sent successfully!")
            return redirect(request.url)

        except Exception as e:
            print("Erro ao enviar email de interesse:", e)
            flash("Erro ao enviar email. Tente novamente.") if lang=="pt" else flash("Error sending email. Please try again.")
            return redirect(request.url)

    return render_template(f"{lang}/index.html")

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

    if request.method == "POST":

        nome = request.form.get("name")
        email = request.form.get("email")
        tipo = request.form.get("type")
        convidados = request.form.get("guests")
        data = request.form.get("date")
        detalhes = request.form.get("details")

        try:
            corpo_html = f"""
            <html>
            <body>
		<p style="margin:0;"><b>POLY HOTEL</b></p>
                <p style="margin:0;"><b>Novo pedido de orçamento - Eventos</b></p>
                <br>
                <p style="margin:0;"><b>Nome:</b> {nome}</p>
                <p style="margin:0;"><b>Email:</b> {email}</p>
                <p style="margin:0;"><b>Tipo de evento:</b> {tipo}</p>
                <p style="margin:0;"><b>Nº de convidados:</b> {convidados}</p>
                <p style="margin:0;"><b>Data pretendida:</b> {data}</p>
                <p style="margin:0;"><b>Detalhes:</b><br>{detalhes}</p>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg["From"] = EMAIL_REMETENTE

            if isinstance(EMAIL_DESTINOS, list):
                msg["To"] = ", ".join(EMAIL_DESTINOS)
            else:
                msg["To"] = EMAIL_DESTINO

            msg["Subject"] = "Poly Hotel - Novo pedido de orçamento (Eventos) "
            msg.attach(MIMEText(corpo_html, "html"))

            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(msg)
            servidor.quit()

            if lang == "en":
                flash("Request sent successfully!")
            else:
                flash("Pedido enviado com sucesso!")

            return redirect(request.url)

        except Exception as e:
            print("Erro ao enviar email:", e)

            if lang == "en":
                flash("Error sending request. Please try again.")
            else:
                flash("Erro ao enviar pedido. Tente novamente.")

            return redirect(request.url)

    return render_template(tpath('events'))

#@bp.route('/<lang>/gallery')
#def gallery(lang):
#    return render_template(tpath('gallery'))

@bp.route('/<lang>/location')
def location(lang):
    return render_template(tpath('location'))

@bp.route('/<lang>/contact', methods=['GET','POST'])
def contact(lang):

    if request.method == "POST":

        nome = request.form.get("name")
        email = request.form.get("email")
        mensagem = request.form.get("message")

        try:
            corpo_html = f"""
            <html>
            <body>
 		<p style="margin:0;"><b>POLY HOTEL</b></p>
                <p style="margin:0;"><b>Nova mensagem de contacto recebida do site PolyHotel:</b></p>
                <p style="margin:0;"><b>Nome:</b> {nome}</p>
                <p style="margin:0;"><b>Email:</b> {email}</p>
                <p style="margin:0;"><b>Mensagem:</b><br>{mensagem}</p>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg["From"] = EMAIL_REMETENTE

            if isinstance(EMAIL_DESTINOS, list):
                msg["To"] = ", ".join(EMAIL_DESTINOS)
            else:
                msg["To"] = EMAIL_DESTINO

            msg["Subject"] = "Poly Hotel - Nova mensagem de contacto"
            msg.attach(MIMEText(corpo_html, "html"))

            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(msg)
            servidor.quit()

            if lang == "en":
                flash("Message sent successfully!")
            else:
                flash("Mensagem enviada com sucesso!")

            return redirect(request.url)

        except Exception as e:
            print("Erro ao enviar email:", e)

            if lang == "en":
                flash("Error sending message. Please try again.")
            else:
                flash("Erro ao enviar mensagem. Tente novamente.")

            return redirect(request.url)

    return render_template(tpath('contact'))

@bp.route('/<lang>/private-lounge')
def private_lounge(lang):
    return render_template(tpath('private_lounge'))

@bp.route('/<lang>/booking', methods=['GET','POST'])
def booking(lang):
    return render_template(tpath('booking'))

@bp.route('/<lang>/gallery')
def gallery(lang):
    return render_template(tpath('gallery'))
