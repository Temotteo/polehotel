import json
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
BEDS24_SETTINGS_FILE = DATA_DIR / 'beds24_settings.json'
OPERATIONS_FILE = DATA_DIR / 'operations.json'
OPERATIONS_ARTICLES_FILE = DATA_DIR / 'operations_articles.json'
OPERATIONS_ORDERS_FILE = DATA_DIR / 'operations_orders.json'
PRICE_VERSION = '2026-09-01-published-rates'

# Default prices
DEFAULT_PRICES = {
    "casal-economico": 6000.00,
    "casal-standard": 6400.00,
    "duplo-standard": 5800.00,
    "executivo-especial": 12000.00,
    "executivo-junior": 8500.00,
    "executivo-master": 12000.00
}

ROOM_NAMES = {
    "casal-economico": {"pt": "Casal Económico", "en": "Economy Double"},
    "casal-standard": {"pt": "Casal Standard", "en": "Standard Double"},
    "duplo-standard": {"pt": "Duplo Standard", "en": "Standard Twin"},
    "executivo-especial": {"pt": "Executivo Especial", "en": "Executive Special"},
    "executivo-junior": {"pt": "Executivo Junior", "en": "Executive Junior"},
    "executivo-master": {"pt": "Executivo Master", "en": "Executive Master"}
}

BEDS24_DEFAULT_SETTINGS = {
    'enabled': False,
    'api_base_url': 'https://api.beds24.com/v2',
    'long_life_token': '',
    'refresh_token': '',
    'access_token': '',
    'access_token_expires_at': '',
    'property_id': '',
    'webhook_secret': '',
    'room_mappings': {slug: '' for slug in ROOM_NAMES},
    'last_test_at': '',
    'last_test_status': '',
    'last_test_message': '',
}

OPERATIONS_SERVICES = {
    'restauracao-bar': {'pt': 'Restauração e Bar', 'en': 'Restaurant and Bar'},
    'salao-cabeleireiro': {'pt': 'Salão de Cabeleireiro', 'en': 'Hair Salon'},
    'sauna': {'pt': 'Sauna', 'en': 'Sauna'},
    'salas-conferencia': {'pt': 'Salas de Conferência', 'en': 'Conference Rooms'},
    'salao-eventos': {'pt': 'Salão de Eventos', 'en': 'Events Hall'},
    'transfer': {'pt': 'Serviços de Transfer', 'en': 'Transfer Services'},
}

OPERATIONS_STATUSES = ['operacional', 'limitado', 'manutencao', 'indisponivel']
OPERATIONS_STATUS_LABELS = {
    'pt': {
        'operacional': 'Operacional',
        'limitado': 'Serviço limitado',
        'manutencao': 'Em manutenção',
        'indisponivel': 'Indisponível',
    },
    'en': {
        'operacional': 'Operational',
        'limitado': 'Limited service',
        'manutencao': 'Under maintenance',
        'indisponivel': 'Unavailable',
    },
}

OPERATIONS_ORDER_STATUSES = ['novo', 'em_preparacao', 'concluido', 'cancelado']
OPERATIONS_ORDER_STATUS_LABELS = {
    'pt': {
        'novo': 'Novo pedido',
        'em_preparacao': 'Em preparação',
        'concluido': 'Concluído',
        'cancelado': 'Cancelado',
    },
    'en': {
        'novo': 'New request',
        'em_preparacao': 'In progress',
        'concluido': 'Completed',
        'cancelado': 'Cancelled',
    },
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
            prices = {}
            if PRICES_FILE.exists():
                with open(PRICES_FILE, 'r') as f:
                    prices = json.load(f)

            if not isinstance(prices, dict) or prices.get('_version') != PRICE_VERSION:
                prices = DEFAULT_PRICES.copy()
                prices['_version'] = PRICE_VERSION
                PriceManager.save_prices(prices)
                return prices

            changed = False
            for room_slug, price in DEFAULT_PRICES.items():
                if room_slug not in prices:
                    prices[room_slug] = price
                    changed = True
            if changed:
                PriceManager.save_prices(prices)
            return prices
        except Exception as e:
            print(f"Erro ao carregar preços: {e}")
            prices = DEFAULT_PRICES.copy()
            prices['_version'] = PRICE_VERSION
            return prices

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


class Beds24SettingsManager:
    @staticmethod
    def default_settings():
        settings = BEDS24_DEFAULT_SETTINGS.copy()
        settings['room_mappings'] = BEDS24_DEFAULT_SETTINGS['room_mappings'].copy()
        return settings

    @staticmethod
    def load_settings():
        try:
            settings = Beds24SettingsManager.default_settings()
            if BEDS24_SETTINGS_FILE.exists():
                with open(BEDS24_SETTINGS_FILE, 'r') as f:
                    saved = json.load(f)
                settings.update(saved)
                mappings = BEDS24_DEFAULT_SETTINGS['room_mappings'].copy()
                mappings.update(saved.get('room_mappings', {}))
                settings['room_mappings'] = mappings
            return settings
        except Exception as e:
            print(f"Erro ao carregar configurações Beds24: {e}")
            return Beds24SettingsManager.default_settings()

    @staticmethod
    def save_settings(settings):
        try:
            current = Beds24SettingsManager.load_settings()
            current.update(settings)
            mappings = BEDS24_DEFAULT_SETTINGS['room_mappings'].copy()
            mappings.update(current.get('room_mappings', {}))
            current['room_mappings'] = mappings
            with open(BEDS24_SETTINGS_FILE, 'w') as f:
                json.dump(current, f, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao guardar configurações Beds24: {e}")
            return False

    @staticmethod
    def mask_secret(value):
        if not value:
            return ''
        if len(value) <= 8:
            return '****'
        return f"{value[:4]}****{value[-4:]}"


class OperationsManager:
    @staticmethod
    def default_services():
        return {
            slug: {
                'status': 'operacional',
                'responsible': '',
                'hours': '',
                'capacity': '',
                'internal_contact': '',
                'notes': '',
                'updated_at': '',
            }
            for slug in OPERATIONS_SERVICES
        }

    @staticmethod
    def load_services():
        services = OperationsManager.default_services()
        try:
            if OPERATIONS_FILE.exists():
                with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                if isinstance(saved, dict):
                    for slug in services:
                        if isinstance(saved.get(slug), dict):
                            services[slug].update(saved[slug])
                            if services[slug].get('status') not in OPERATIONS_STATUSES:
                                services[slug]['status'] = 'operacional'
        except Exception as e:
            print(f"Erro ao carregar operações internas: {e}")
        return services

    @staticmethod
    def save_services(services):
        try:
            with open(OPERATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(services, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao guardar operações internas: {e}")
            return False


class OperationsArticleManager:
    @staticmethod
    def normalize_article(article):
        if not isinstance(article, dict) or article.get('area_slug') not in OPERATIONS_SERVICES:
            return None
        try:
            price = max(0, float(article.get('price', 0)))
            article_id = int(article.get('id', 0))
        except (TypeError, ValueError):
            return None
        if article_id <= 0 or not str(article.get('name', '')).strip():
            return None
        return {
            'id': article_id,
            'area_slug': article['area_slug'],
            'name': str(article.get('name', '')).strip(),
            'description': str(article.get('description', '')).strip(),
            'price': price,
            'active': bool(article.get('active', True)),
            'created_at': str(article.get('created_at', '')),
            'updated_at': str(article.get('updated_at', '')),
        }

    @staticmethod
    def load_articles():
        try:
            if OPERATIONS_ARTICLES_FILE.exists():
                with open(OPERATIONS_ARTICLES_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                if isinstance(saved, list):
                    return [article for item in saved if (article := OperationsArticleManager.normalize_article(item))]
        except Exception as e:
            print(f"Erro ao carregar artigos das operações: {e}")
        return []

    @staticmethod
    def save_articles(articles):
        try:
            with open(OPERATIONS_ARTICLES_FILE, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao guardar artigos das operações: {e}")
            return False

    @staticmethod
    def get_article(article_id):
        for article in OperationsArticleManager.load_articles():
            if article['id'] == article_id:
                return article
        return None

    @staticmethod
    def articles_for_area(area_slug, active_only=False):
        articles = [article for article in OperationsArticleManager.load_articles() if article['area_slug'] == area_slug]
        if active_only:
            articles = [article for article in articles if article['active']]
        return sorted(articles, key=lambda article: article['name'].lower())

    @staticmethod
    def create_article(area_slug, name, description, price, active=True):
        if area_slug not in OPERATIONS_SERVICES or not str(name).strip():
            return None
        try:
            price = max(0, float(price))
        except (TypeError, ValueError):
            return None
        articles = OperationsArticleManager.load_articles()
        article = {
            'id': max((item['id'] for item in articles), default=0) + 1,
            'area_slug': area_slug,
            'name': str(name).strip(),
            'description': str(description or '').strip(),
            'price': price,
            'active': bool(active),
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'updated_at': datetime.now().isoformat(timespec='seconds'),
        }
        articles.append(article)
        return article if OperationsArticleManager.save_articles(articles) else None

    @staticmethod
    def update_article(article_id, area_slug, name, description, price, active):
        try:
            price = max(0, float(price))
        except (TypeError, ValueError):
            return None
        articles = OperationsArticleManager.load_articles()
        for article in articles:
            if article['id'] == article_id and article['area_slug'] == area_slug:
                article.update({
                    'name': str(name).strip(),
                    'description': str(description or '').strip(),
                    'price': price,
                    'active': bool(active),
                    'updated_at': datetime.now().isoformat(timespec='seconds'),
                })
                if not article['name']:
                    return None
                return article if OperationsArticleManager.save_articles(articles) else None
        return None

    @staticmethod
    def delete_article(article_id, area_slug):
        articles = OperationsArticleManager.load_articles()
        filtered = [article for article in articles if not (article['id'] == article_id and article['area_slug'] == area_slug)]
        if len(filtered) == len(articles):
            return False
        return OperationsArticleManager.save_articles(filtered)


class OperationsOrderManager:
    @staticmethod
    def normalize_order(order):
        if not isinstance(order, dict) or order.get('area_slug') not in OPERATIONS_SERVICES:
            return None
        try:
            order_id = int(order.get('id', 0))
            quantity = max(1, int(order.get('quantity', 1)))
            unit_price = max(0, float(order.get('unit_price', 0)))
        except (TypeError, ValueError):
            return None
        if order_id <= 0 or not str(order.get('customer_name', '')).strip():
            return None
        status = order.get('status', 'novo')
        return {
            'id': order_id,
            'area_slug': order['area_slug'],
            'article_id': order.get('article_id'),
            'article_name': str(order.get('article_name', '')).strip() or 'Artigo removido',
            'quantity': quantity,
            'unit_price': unit_price,
            'total': round(quantity * unit_price, 2),
            'customer_name': str(order.get('customer_name', '')).strip(),
            'customer_contact': str(order.get('customer_contact', '')).strip(),
            'reservation_id': order.get('reservation_id') or '',
            'status': status if status in OPERATIONS_ORDER_STATUSES else 'novo',
            'notes': str(order.get('notes', '')).strip(),
            'created_at': str(order.get('created_at', '')),
            'updated_at': str(order.get('updated_at', '')),
        }

    @staticmethod
    def load_orders():
        try:
            if OPERATIONS_ORDERS_FILE.exists():
                with open(OPERATIONS_ORDERS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                if isinstance(saved, list):
                    return [order for item in saved if (order := OperationsOrderManager.normalize_order(item))]
        except Exception as e:
            print(f"Erro ao carregar pedidos das operações: {e}")
        return []

    @staticmethod
    def save_orders(orders):
        try:
            with open(OPERATIONS_ORDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(orders, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao guardar pedidos das operações: {e}")
            return False

    @staticmethod
    def orders_for_area(area_slug):
        return sorted(
            [order for order in OperationsOrderManager.load_orders() if order['area_slug'] == area_slug],
            key=lambda order: order.get('created_at', ''),
            reverse=True,
        )

    @staticmethod
    def create_order(area_slug, article_id, quantity, customer_name, customer_contact, reservation_id='', notes=''):
        if area_slug not in OPERATIONS_SERVICES or not str(customer_name).strip():
            return None
        try:
            article_id = int(article_id)
            quantity = max(1, int(quantity))
        except (TypeError, ValueError):
            return None
        article = OperationsArticleManager.get_article(article_id)
        if not article or article['area_slug'] != area_slug or not article['active']:
            return None
        orders = OperationsOrderManager.load_orders()
        order = {
            'id': max((item['id'] for item in orders), default=0) + 1,
            'area_slug': area_slug,
            'article_id': article['id'],
            'article_name': article['name'],
            'quantity': quantity,
            'unit_price': article['price'],
            'total': round(quantity * article['price'], 2),
            'customer_name': str(customer_name).strip(),
            'customer_contact': str(customer_contact or '').strip(),
            'reservation_id': str(reservation_id or '').strip(),
            'status': 'novo',
            'notes': str(notes or '').strip(),
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'updated_at': datetime.now().isoformat(timespec='seconds'),
        }
        orders.append(order)
        return order if OperationsOrderManager.save_orders(orders) else None

    @staticmethod
    def update_status(order_id, area_slug, status):
        if status not in OPERATIONS_ORDER_STATUSES:
            return None
        orders = OperationsOrderManager.load_orders()
        for order in orders:
            if order['id'] == order_id and order['area_slug'] == area_slug:
                order['status'] = status
                order['updated_at'] = datetime.now().isoformat(timespec='seconds')
                return order if OperationsOrderManager.save_orders(orders) else None
        return None

    @staticmethod
    def summary_by_area():
        summary = {slug: {'total': 0, 'open': 0} for slug in OPERATIONS_SERVICES}
        for order in OperationsOrderManager.load_orders():
            summary[order['area_slug']]['total'] += 1
            if order['status'] in ('novo', 'em_preparacao'):
                summary[order['area_slug']]['open'] += 1
        return summary


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
    def normalize_reservation(reservation):
        if not isinstance(reservation, dict):
            return {}

        room_slug = reservation.get('room_slug', '')
        normalized = reservation.copy()
        normalized.setdefault('id', 0)
        normalized.setdefault('guest_name', '')
        normalized.setdefault('email', '')
        normalized.setdefault('phone', '')
        normalized.setdefault('room_slug', room_slug)
        normalized.setdefault('room_name', ROOM_NAMES.get(room_slug, {}).get('pt', room_slug))
        normalized.setdefault('check_in', '')
        normalized.setdefault('check_out', '')
        normalized.setdefault('guests_count', 0)
        normalized.setdefault('special_requests', '')
        normalized.setdefault('status', 'pendente')
        normalized.setdefault('created_at', '')
        normalized.setdefault('price', PriceManager.get_price(room_slug) if room_slug else 0)
        return normalized

    @staticmethod
    def load_reservations():
        try:
            if RESERVATIONS_FILE.exists():
                with open(RESERVATIONS_FILE, 'r') as f:
                    reservations = json.load(f)
                if isinstance(reservations, list):
                    return [ReservationManager.normalize_reservation(r) for r in reservations]
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
