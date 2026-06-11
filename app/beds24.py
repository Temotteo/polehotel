import json
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class Beds24Error(Exception):
    pass


class Beds24Client:
    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.get('api_base_url', '').rstrip('/') or 'https://api.beds24.com/v2'

    def refresh_access_token(self):
        refresh_token = self.settings.get('refresh_token')
        if not refresh_token:
            raise Beds24Error('Refresh token não configurado.')

        data, _headers = self._raw_request(
            '/authentication/token',
            headers={'refreshToken': refresh_token},
            auth=False,
        )
        token = data.get('token')
        if not token:
            raise Beds24Error('Resposta Beds24 sem token.')

        expires_in = int(data.get('expiresIn', 86400))
        expires_at = datetime.utcnow() + timedelta(seconds=max(expires_in - 300, 60))
        return {
            'access_token': token,
            'access_token_expires_at': expires_at.isoformat(),
        }

    def token(self):
        long_life_token = self.settings.get('long_life_token')
        if long_life_token:
            return long_life_token

        access_token = self.settings.get('access_token')
        expires_at = self.settings.get('access_token_expires_at')
        if access_token and expires_at:
            try:
                if datetime.fromisoformat(expires_at) > datetime.utcnow():
                    return access_token
            except ValueError:
                pass

        refreshed = self.refresh_access_token()
        self.settings.update(refreshed)
        return refreshed['access_token']

    def get_properties(self):
        return self.get('/properties', params={'includePriceRules': 'true'})

    def get_bookings(self, params=None):
        return self.get('/bookings', params=params)

    def create_booking(self, booking):
        return self.post('/bookings', [booking])

    def get_room_availability(self, params=None):
        return self.get('/inventory/rooms/availability', params=params)

    def get_room_calendar(self, params=None):
        return self.get('/inventory/rooms/calendar', params=params)

    def update_room_calendar(self, calendar_items):
        return self.post('/inventory/rooms/calendar', calendar_items)

    def get(self, path, params=None):
        query = f"?{urlencode(params)}" if params else ''
        data, headers = self._raw_request(f"{path}{query}")
        return {'data': data, 'headers': headers}

    def post(self, path, payload):
        data, headers = self._raw_request(path, method='POST', payload=payload)
        return {'data': data, 'headers': headers}

    def _raw_request(self, path, headers=None, auth=True, method='GET', payload=None):
        request_headers = {'accept': 'application/json'}
        body = None
        if payload is not None:
            request_headers['content-type'] = 'application/json'
            body = json.dumps(payload).encode('utf-8')
        if headers:
            request_headers.update(headers)
        if auth:
            request_headers['token'] = self.token()

        request = Request(f"{self.base_url}{path}", data=body, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=20) as response:
                body = response.read().decode('utf-8')
                data = json.loads(body) if body else {}
                return data, dict(response.headers.items())
        except HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            raise Beds24Error(f"Beds24 HTTP {e.code}: {body[:400]}")
        except URLError as e:
            raise Beds24Error(f"Erro de ligação Beds24: {e.reason}")
        except json.JSONDecodeError as e:
            raise Beds24Error(f"Resposta Beds24 inválida: {e}")
