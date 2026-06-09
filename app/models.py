import json
import os
from datetime import datetime
from pathlib import Path

# Database file paths
try:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    DATA_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"Erro ao criar diretório de dados: {e}")
    BASE_DIR = Path('.')
    DATA_DIR = BASE_DIR / 'data'
    DATA_DIR.mkdir(exist_ok=True)

PRICES_FILE = DATA_DIR / 'prices.json'
RESERVATIONS_FILE = DATA_DIR / 'reservations.json'

# Default prices
DEFAULT_PRICES = {
    "casal-economico": 50.00,
    "casal-standard": 75.00,
    "duplo-standard": 80.00,
    "executivo-especial": 120.00,
    "executivo-junior": 130.00,
    "executivo-master": 180.00
}

ROOM_NAMES = {
    "casal-economico": {"pt": "Casal Económico", "en": "Economy Double"},
    "casal-standard": {"pt": "Casal Standard", "en": "Standard Double"},
    "duplo-standard": {"pt": "Duplo Standard", "en": "Standard Twin"},
    "executivo-especial": {"pt": "Executivo Especial", "en": "Executive Special"},
    "executivo-junior": {"pt": "Executivo Junior", "en": "Executive Junior"},
    "executivo-master": {"pt": "Executivo Master", "en": "Executive Master"}
}

# Initialize prices file if it doesn't exist
try:
    if not PRICES_FILE.exists():
        with open(PRICES_FILE, 'w') as f:
            json.dump(DEFAULT_PRICES, f, indent=2)
except Exception as e:
    print(f"Erro ao inicializar arquivo de preços: {e}")

# Initialize reservations file if it doesn't exist
try:
    if not RESERVATIONS_FILE.exists():
        with open(RESERVATIONS_FILE, 'w') as f:
            json.dump([], f, indent=2)
except Exception as e:
    print(f"Erro ao inicializar arquivo de reservas: {e}")


class PriceManager:
    @staticmethod
    def load_prices():
        try:
            if PRICES_FILE.exists():
                with open(PRICES_FILE, 'r') as f:
                    return json.load(f)
            return DEFAULT_PRICES.copy()
        except Exception as e:
            print(f"Erro ao carregar preços: {e}")
            return DEFAULT_PRICES.copy()

    @staticmethod
    def save_prices(prices):
        try:
            with open(PRICES_FILE, 'w') as f:
                json.dump(prices, f, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao guardar preços: {e}")
            return False

    @staticmethod
    def get_price(room_slug):
        prices = PriceManager.load_prices()
        return prices.get(room_slug, DEFAULT_PRICES.get(room_slug, 0))

    @staticmethod
    def update_price(room_slug, price):
        prices = PriceManager.load_prices()
        prices[room_slug] = float(price)
        PriceManager.save_prices(prices)
        return prices


class ReservationManager:
    STATUSES = ['pendente', 'confirmada', 'cancelada', 'finalizada']
    STATUS_LABELS = {
        'pt': {
            'pendente': 'Pendente',
            'confirmada': 'Confirmada',
            'cancelada': 'Cancelada',
            'finalizada': 'Finalizada'
        },
        'en': {
            'pendente': 'Pending',
            'confirmada': 'Confirmed',
            'cancelada': 'Cancelled',
            'finalizada': 'Completed'
        }
    }

    @staticmethod
    def load_reservations():
        try:
            if RESERVATIONS_FILE.exists():
                with open(RESERVATIONS_FILE, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Erro ao carregar reservas: {e}")
            return []

    @staticmethod
    def save_reservations(reservations):
        try:
            with open(RESERVATIONS_FILE, 'w') as f:
                json.dump(reservations, f, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao guardar reservas: {e}")
            return False

    @staticmethod
    def create_reservation(guest_name, email, phone, room_slug, check_in, check_out, guests_count, special_requests=None):
        try:
            reservations = ReservationManager.load_reservations()
            
            # Encontrar o próximo ID
            if reservations:
                next_id = max([r['id'] for r in reservations]) + 1
            else:
                next_id = 1
            
            reservation = {
                'id': next_id,
                'guest_name': guest_name,
                'email': email,
                'phone': phone,
                'room_slug': room_slug,
                'room_name': ROOM_NAMES.get(room_slug, {}).get('pt', room_slug),
                'check_in': check_in,
                'check_out': check_out,
                'guests_count': int(guests_count),
                'special_requests': special_requests or '',
                'status': 'pendente',
                'created_at': datetime.now().isoformat(),
                'price': PriceManager.get_price(room_slug)
            }
            reservations.append(reservation)
            ReservationManager.save_reservations(reservations)
            return reservation
        except Exception as e:
            print(f"Erro ao criar reserva: {e}")
            raise

    @staticmethod
    def get_all_reservations():
        return ReservationManager.load_reservations()

    @staticmethod
    def get_reservation(res_id):
        try:
            reservations = ReservationManager.load_reservations()
            for res in reservations:
                if res['id'] == res_id:
                    return res
            return None
        except Exception as e:
            print(f"Erro ao obter reserva: {e}")
            return None

    @staticmethod
    def update_status(res_id, status):
        try:
            if status not in ReservationManager.STATUSES:
                return None
            reservations = ReservationManager.load_reservations()
            for res in reservations:
                if res['id'] == res_id:
                    res['status'] = status
                    ReservationManager.save_reservations(reservations)
                    return res
            return None
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return None

    @staticmethod
    def delete_reservation(res_id):
        try:
            reservations = ReservationManager.load_reservations()
            reservations = [r for r in reservations if r['id'] != res_id]
            ReservationManager.save_reservations(reservations)
            return True
        except Exception as e:
            print(f"Erro ao deletar reserva: {e}")
            return False
