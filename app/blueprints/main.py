from flask import Blueprint, render_template, request, abort, flash, redirect, url_for
from app.models import ReservationManager, PriceManager
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===============================
# CONFIGURAÇÃO DE EMAIL (GMAIL)
# ===============================

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "info@polehotel.com")
CONTACT_PHONE_DISPLAY = os.getenv("CONTACT_PHONE_DISPLAY", "+258 00 000 0000")
CONTACT_PHONE_TEL = os.getenv("CONTACT_PHONE_TEL", "+258000000000")
CONTACT_WHATSAPP_NUMBER = os.getenv("CONTACT_WHATSAPP_NUMBER", "258000000000")
CONTACT_WHATSAPP_URL = f"https://wa.me/{CONTACT_WHATSAPP_NUMBER}"

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "noreply@polehotel.com")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", CONTACT_EMAIL)
EMAIL_DESTINOS = [
    email.strip()
    for email in os.getenv("EMAIL_DESTINOS", EMAIL_DESTINO).split(",")
    if email.strip()
]

bp = Blueprint('main', __name__)

PAGES = ['index','about','rooms','dining','events','gallery','location','contact']

ROOM_CATEGORIES = {
    "casal-economico": {
        "pt": {
            "name": "Casal Económico",
            "desc": "Opção funcional e confortável para estadias práticas.",
            "features": ["Cama de casal", "Ar condicionado", "Wi-Fi", "Casa de banho privativa"],
        },
        "en": {
            "name": "Economy Double",
            "desc": "Functional and comfortable option for practical stays.",
            "features": ["Double bed", "Air conditioning", "Wi-Fi", "Private bathroom"],
        },
        "gallery": ["room1.jpg"],
    },
    "casal-standard": {
        "pt": {
            "name": "Casal Standard",
            "desc": "Conforto equilibrado com design acolhedor.",
            "features": ["Cama de casal", "TV", "Wi-Fi", "Ar condicionado"], 
        },
        "en": {
            "name": "Standard Double",
            "desc": "Balanced comfort with a welcoming design.",
            "features": ["Double bed", "TV", "Wi-Fi", "Air conditioning"],
        },
        "gallery": ["room2.jpg"],
    },
    "duplo-standard": {
        "pt": {
            "name": "Duplo Standard",
            "desc": "Ideal para duas pessoas, com espaço e comodidade.",
            "features": ["Duas camas", "TV", "Wi-Fi", "Ar condicionado"],
        },
        "en": {
            "name": "Standard Twin",
            "desc": "Ideal for two guests with space and comfort.",
            "features": ["Twin beds", "TV", "Wi-Fi", "Air conditioning"],
        },
        "gallery": ["room3.jpg"],
    },
    "executivo-especial": {
        "pt": {
            "name": "Executivo Especial",
            "desc": "Categoria superior com detalhes premium.",
            "features": ["Cama queen", "Mini-bar", "Secretária", "Wi-Fi"],
        },
        "en": {
            "name": "Executive Special",
            "desc": "Premium category with refined details.",
            "features": ["Queen bed", "Mini-bar", "Desk", "Wi-Fi"],
        },
        "gallery": ["room4.jpg"],
    },
    "executivo-junior": {
        "pt": {
            "name": "Executivo Junior",
            "desc": "Ambiente amplo, ideal para estadias prolongadas.",
            "features": ["Área de estar", "Cama queen", "Wi-Fi", "Ar condicionado"],
        },
        "en": {
            "name": "Executive Junior",
            "desc": "Spacious layout, ideal for longer stays.",
            "features": ["Seating area", "Queen bed", "Wi-Fi", "Air conditioning"],
        },
        "gallery": ["room5.jpg"],
    },
    "executivo-master": {
        "pt": {
            "name": "Executivo Master",
            "desc": "Experiência exclusiva com máximo conforto e elegância.",
            "features": ["Suite premium", "Sala de estar", "Mini-bar", "Vista privilegiada"],
        },
        "en": {
            "name": "Executive Master",
            "desc": "Exclusive experience with maximum comfort and elegance.",
            "features": ["Premium suite", "Living area", "Mini-bar", "Premium view"],
        },
        "gallery": ["room6.jpg"],
    }
}

def tpath(page):
    lang = getattr(request, 'lang', 'pt')
    return f"{lang}/{page}.html"

def send_booking_confirmation_email(reservation, lang):
    """Envia email de confirmação da reserva ao cliente"""
    try:
        room_name = reservation.get('room_name', 'Quarto')
        
        if lang == 'pt':
            subject = f"Pole Hotel - Confirmação de Reserva #{reservation['id']}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
                    <h2 style="color: #8B6F47; border-bottom: 2px solid #C4A76A; padding-bottom: 10px;">
                        🏨 Pole Hotel - Confirmação de Reserva
                    </h2>
                    
                    <p>Olá <strong>{reservation['guest_name']}</strong>,</p>
                    
                    <p>Agradecemos o seu pedido de reserva! Recebemos a sua solicitação com os seguintes detalhes:</p>
                    
                    <div style="background: #f7f3ea; padding: 15px; border-left: 4px solid #C4A76A; margin: 20px 0;">
                        <p><strong>Número de Reserva:</strong> #{reservation['id']}</p>
                        <p><strong>Quarto:</strong> {room_name}</p>
                        <p><strong>Check-in:</strong> {reservation['check_in']}</p>
                        <p><strong>Check-out:</strong> {reservation['check_out']}</p>
                        <p><strong>Número de Hóspedes:</strong> {reservation['guests_count']}</p>
                        <p><strong>Preço:</strong> €{reservation['price']:.2f}</p>
                        <p><strong>Estado:</strong> <span style="color: #ff9800; font-weight: bold;">PENDENTE</span></p>
                    </div>
                    
                    <p>Em breve receberá uma confirmação final via email. Pode contactar-nos através de:</p>
                    <ul>
                        <li>📧 Email: {CONTACT_EMAIL}</li>
                        <li>📱 WhatsApp: <a href="{CONTACT_WHATSAPP_URL}">{CONTACT_PHONE_DISPLAY}</a></li>
                        <li>🌐 Website: <a href="https://polehotel.onrender.com">polehotel.onrender.com</a></li>
                    </ul>
                    
                    <p>Obrigado por escolher o Pole Hotel!</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        © 2025 Pole Hotel. Todos os direitos reservados.
                    </p>
                </div>
            </body>
            </html>
            """
        else:
            subject = f"Pole Hotel - Booking Confirmation #{reservation['id']}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
                    <h2 style="color: #8B6F47; border-bottom: 2px solid #C4A76A; padding-bottom: 10px;">
                        🏨 Pole Hotel - Booking Confirmation
                    </h2>
                    
                    <p>Hello <strong>{reservation['guest_name']}</strong>,</p>
                    
                    <p>Thank you for your booking request! We have received your application with the following details:</p>
                    
                    <div style="background: #f7f3ea; padding: 15px; border-left: 4px solid #C4A76A; margin: 20px 0;">
                        <p><strong>Booking Number:</strong> #{reservation['id']}</p>
                        <p><strong>Room:</strong> {room_name}</p>
                        <p><strong>Check-in:</strong> {reservation['check_in']}</p>
                        <p><strong>Check-out:</strong> {reservation['check_out']}</p>
                        <p><strong>Number of Guests:</strong> {reservation['guests_count']}</p>
                        <p><strong>Price:</strong> €{reservation['price']:.2f}</p>
                        <p><strong>Status:</strong> <span style="color: #ff9800; font-weight: bold;">PENDING</span></p>
                    </div>
                    
                    <p>You will soon receive a final confirmation via email. You can contact us through:</p>
                    <ul>
                        <li>📧 Email: {CONTACT_EMAIL}</li>
                        <li>📱 WhatsApp: <a href="{CONTACT_WHATSAPP_URL}">{CONTACT_PHONE_DISPLAY}</a></li>
                        <li>🌐 Website: <a href="https://polehotel.onrender.com">polehotel.onrender.com</a></li>
                    </ul>
                    
                    <p>Thank you for choosing Pole Hotel!</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        © 2025 Pole Hotel. All rights reserved.
                    </p>
                </div>
            </body>
            </html>
            """
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = reservation['email']
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
        servidor.send_message(msg)
        servidor.quit()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email de confirmação: {e}")
        return False

def send_booking_notification_to_admin(reservation, lang):
    """Envia notificação para o admin sobre nova reserva"""
    try:
        room_name = reservation.get('room_name', 'Room')
        
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="color: #8B6F47; border-bottom: 2px solid #C4A76A; padding-bottom: 10px;">
                    🔔 NOVA RESERVA - Pole Hotel
                </h2>
                
                <div style="background: #f7f3ea; padding: 15px; border-left: 4px solid #C4A76A; margin: 20px 0;">
                    <p><strong>Número da Reserva:</strong> #{reservation['id']}</p>
                    <p><strong>Hóspede:</strong> {reservation['guest_name']}</p>
                    <p><strong>Email:</strong> {reservation['email']}</p>
                    <p><strong>Telefone:</strong> {reservation['phone']}</p>
                    <p><strong>Quarto:</strong> {room_name}</p>
                    <p><strong>Check-in:</strong> {reservation['check_in']}</p>
                    <p><strong>Check-out:</strong> {reservation['check_out']}</p>
                    <p><strong>Número de Hóspedes:</strong> {reservation['guests_count']}</p>
                    <p><strong>Preço:</strong> €{reservation['price']:.2f}</p>
                </div>
                
                <p><a href="https://polehotel.onrender.com/pt/admin/reservations/{reservation['id']}" style="background: #8B6F47; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Ver detalhes da reserva
                </a></p>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        if isinstance(EMAIL_DESTINOS, list):
            msg["To"] = ", ".join(EMAIL_DESTINOS)
        else:
            msg["To"] = EMAIL_DESTINO
        msg["Subject"] = f"Pole Hotel - Nova Reserva #{reservation['id']}"
        msg.attach(MIMEText(corpo_html, "html"))
        
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
        servidor.send_message(msg)
        servidor.quit()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar notificação admin: {e}")
        return False

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
    room = ROOM_CATEGORIES.get(slug)
    if not room:
        abort(404)
    content = dict(room.get(lang, room["pt"]))
    content["gallery"] = room.get("gallery", [])
    return render_template(f"{lang}/room_detail.html", room=content, slug=slug)

@bp.route('/')
def home_redirect():
    from flask import current_app, redirect, url_for
    return redirect(url_for('main.index', lang=current_app.config.get('DEFAULT_LANG','pt')))

@bp.route('/<lang>/', methods=['GET','POST'])
def home(lang):
    if request.method == "POST":
        email = request.form.get("email")
        interesses = request.form.getlist("interesse")

        try:
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
    if request.method == "POST":
        try:
            # Captura de dados do formulário
            guest_name = request.form.get("guest_name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            room_slug = request.form.get("room_category")
            check_in = request.form.get("check_in")
            check_out = request.form.get("check_out")
            guests_count = request.form.get("guests_count")
            special_requests = request.form.get("special_requests", "")
            
            # Validações
            if not all([guest_name, email, phone, room_slug, check_in, check_out, guests_count]):
                flash("Por favor, preencha todos os campos obrigatórios." if lang == "pt" else "Please fill all required fields.", "danger")
                return redirect(request.url)
            
            # Criar reserva
            reservation = ReservationManager.create_reservation(
                guest_name=guest_name,
                email=email,
                phone=phone,
                room_slug=room_slug,
                check_in=check_in,
                check_out=check_out,
                guests_count=int(guests_count),
                special_requests=special_requests
            )
            
            # Enviar emails
            send_booking_confirmation_email(reservation, lang)
            send_booking_notification_to_admin(reservation, lang)
            
            if lang == "pt":
                flash(f"Reserva criada com sucesso! Número da reserva: #{reservation['id']}", "success")
            else:
                flash(f"Booking created successfully! Booking number: #{reservation['id']}", "success")
            
            return redirect(request.url)
            
        except Exception as e:
            print(f"Erro ao processar reserva: {e}")
            flash("Erro ao processar a reserva. Tente novamente." if lang == "pt" else "Error processing booking. Please try again.", "danger")
            return redirect(request.url)
    
    # GET - mostrar formulário
    prices = PriceManager.load_prices()
    room_categories = {k: v[lang] for k, v in ROOM_CATEGORIES.items()}
    
    selected_room = request.args.get("room_category", "")

    return render_template(
        tpath('booking'),
        room_categories=room_categories,
        prices=prices,
        selected_room=selected_room,
        all_room_categories=ROOM_CATEGORIES
    )

@bp.route('/<lang>/gallery')
def gallery(lang):
    return render_template(tpath('gallery'))
