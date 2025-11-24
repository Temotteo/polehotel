# Pole Hotel — Website Template (Flask + Bootstrap)

Minimal, elegant and bilingual (pt/en) hotel website template prepared for:
- Direct bookings (future integration point)
- Events quote form
- Gallery, Dining, Rooms, Location, Contact
- Ready for Render.com deployment

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m flask --app wsgi run --debug
```

Open: http://127.0.0.1:5000/pt/  or  /en/

## Deploy to Render

1. Push this repo to GitHub.
2. Create a new **Web Service** on Render, connect the repo.
3. Render will detect Python. Build & start commands are in `render.yaml`.
4. Set environment vars if needed (e.g., DEFAULT_LANG=pt).

## Structure
- `app/__init__.py`: app factory, language handling
- `app/blueprints/main.py`: routes for all pages
- `app/templates/base.html`: layout with navbar/footer
- `app/templates/pt|en/*.html`: localized pages
- `app/static/css/style.css`: brand colors (cream, brown, terracotta)
- `app/static/js/app.js`: future integrations
- `render.yaml`: Render deploy config
- `wsgi.py`: Gunicorn entrypoint

## Integration Points
- **Bookings**: replace CTA anchors with your booking engine or custom route.
- **Airbnb/Booking.com**: add external links or embed widgets when available.
- **WhatsApp**: set `wa.me` number on Contact page and/or integrate business API (UltraMsg/Meta).
- **Events form**: connect to email/DB in `/events` POST handler.

## Notes
This template intentionally uses a minimal i18n approach (URL + lang). For full i18n, consider Flask-Babel.
