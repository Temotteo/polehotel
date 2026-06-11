from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from app.models import PriceManager, ReservationManager, ROOM_NAMES

bp = Blueprint('admin', __name__, url_prefix='/<lang>/admin')

# Simple password protection
ADMIN_PASSWORD = 'pole2024'  # Change this to a secure password!

def check_admin_auth():
    """Check if admin is authenticated"""
    return session.get('admin_authenticated', False)

def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin_auth():
            flash('Acesso não autorizado. Por favor faça login.', 'danger')
            return redirect(url_for('admin.login', lang=request.view_args.get('lang', 'pt')))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login(lang):
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            flash('Login realizado com sucesso!' if lang == 'pt' else 'Login successful!', 'success')
            return redirect(url_for('admin.dashboard', lang=lang))
        else:
            flash('Senha incorreta!' if lang == 'pt' else 'Incorrect password!', 'danger')
    
    return render_template(f"{lang}/admin_login.html")

@bp.route('/logout')
def logout(lang):
    session.pop('admin_authenticated', None)
    flash('Logout realizado com sucesso!' if lang == 'pt' else 'Logout successful!', 'success')
    return redirect(url_for('main.index', lang=lang))

@bp.route('/')
@bp.route('/dashboard')
@require_admin
def dashboard(lang):
    reservations = ReservationManager.get_all_reservations()
    prices = PriceManager.load_prices()
    
    # Statistics
    stats = {
        'total_reservations': len(reservations),
        'confirmed': len([r for r in reservations if r['status'] == 'confirmada']),
        'pending': len([r for r in reservations if r['status'] == 'pendente']),
        'cancelled': len([r for r in reservations if r['status'] == 'cancelada']),
        'completed': len([r for r in reservations if r['status'] == 'finalizada'])
    }
    
    return render_template(f"{lang}/admin_dashboard.html", 
                         reservations=reservations, 
                         prices=prices,
                         stats=stats,
                         room_names=ROOM_NAMES)

@bp.route('/pricing')
@require_admin
def pricing(lang):
    prices = PriceManager.load_prices()
    return render_template(f"{lang}/admin_pricing.html", 
                         prices=prices,
                         room_names=ROOM_NAMES)

@bp.route('/pricing/update', methods=['POST'])
@require_admin
def update_pricing(lang):
    try:
        data = request.get_json()
        room_slug = data.get('room_slug')
        new_price = float(data.get('price', 0))
        
        if new_price < 0:
            return jsonify({'success': False, 'message': 'Preço não pode ser negativo'}), 400
        
        prices = PriceManager.load_prices()
        prices[room_slug] = new_price
        PriceManager.save_prices(prices)
        
        message = f"Preço de {ROOM_NAMES.get(room_slug, {}).get('pt', room_slug)} atualizado para MZN {new_price:.2f}"
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/reservations')
@require_admin
def reservations(lang):
    reservations = ReservationManager.get_all_reservations()
    return render_template(f"{lang}/admin_reservations.html", 
                         reservations=reservations,
                         room_names=ROOM_NAMES,
                         statuses=ReservationManager.STATUSES,
                         status_labels=ReservationManager.STATUS_LABELS.get(lang))

@bp.route('/reservations/<int:res_id>/status', methods=['POST'])
@require_admin
def update_reservation_status(lang, res_id):
    try:
        status = request.get_json().get('status')
        result = ReservationManager.update_status(res_id, status)
        if result:
            return jsonify({'success': True, 'message': 'Status atualizado com sucesso'})
        return jsonify({'success': False, 'message': 'Reserva não encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/reservations/<int:res_id>/delete', methods=['POST'])
@require_admin
def delete_reservation(lang, res_id):
    try:
        ReservationManager.delete_reservation(res_id)
        flash('Reserva deletada com sucesso!' if lang == 'pt' else 'Reservation deleted successfully!', 'success')
        return redirect(url_for('admin.reservations', lang=lang))
    except Exception as e:
        flash(f'Erro ao deletar reserva: {str(e)}' if lang == 'pt' else f'Error deleting reservation: {str(e)}', 'danger')
        return redirect(url_for('admin.reservations', lang=lang))

@bp.route('/reservations/<int:res_id>')
@require_admin
def reservation_detail(lang, res_id):
    reservation = ReservationManager.get_reservation(res_id)
    if not reservation:
        flash('Reserva não encontrada!' if lang == 'pt' else 'Reservation not found!', 'danger')
        return redirect(url_for('admin.reservations', lang=lang))
    
    return render_template(f"{lang}/admin_reservation_detail.html", 
                         reservation=reservation,
                         statuses=ReservationManager.STATUSES,
                         status_labels=ReservationManager.STATUS_LABELS.get(lang))
