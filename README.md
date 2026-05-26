# Kunsthandel Reboot

Web application for managing an art dealership's inventory. Art objects are recorded with metadata and images, and each record gets a unique QR code that can be attached to the physical object — scanning it opens the corresponding detail page.

## Features

- **Inventory management** for art objects with type, origin, location, size, comment, and multiple images (including a thumbnail).
- **QR codes** per record — printed and attached to the object; scanning opens the matching entry.
- **Role-based access control** with five levels:
  - `External` — no permissions
  - `Visitor` — may scan QR codes
  - `User` — read access to all records
  - `Editor` — write access (create, edit, delete)
  - `Administrator` — additionally manages users
- **Authentication** via Flask-Login with bcrypt password hashing.
- **Internationalization** (German / English) via Flask-Babel.
- **Image upload** with server-side processing through Pillow.
- **SQLite** for development, **MySQL** for production.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Bcrypt, Flask-Babel
- **Frontend:** Jinja2, Bootstrap
- **Database:** SQLite / MySQL
- **Other:** Pillow (image processing), qrcode (QR generation)

## Project Structure

```
kunsthandel/
├── __init__.py          # App factory, extension registration
├── config.py            # Development / production config
├── models.py            # SQLAlchemy models (User, Item, Image, Type, Location, Origin)
├── main/                # Home page, utils (QR, images, decorators)
├── users/               # Login, profile, language preference
├── admin/               # User management
├── items/               # CRUD for inventory items + QR endpoint
├── generic_type/        # Management of Type / Location / Origin
├── images/              # Image endpoints
├── errors/              # Error handlers (404, 403, 500)
├── templates/           # Jinja2 templates
├── static/              # CSS, JS, images, generated QR codes
└── translations/        # gettext translations (de, en)
tests/                   # unittest test suite
```

## Setup

### Requirements

- Python 3.9+
- Optional: MySQL for production use

### Installation

```bash
git clone https://github.com/kosch104/KunsthandelReboot.git
cd KunsthandelReboot
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
```

### Running the application

```bash
python run.py
```

On first launch, an admin account is created automatically with the credentials `admin` / `admin`. **This password should be changed immediately, or the account replaced by a real administrator account.**

The application then runs at `http://localhost:5000`.

## Translations

Translation strings are managed via Flask-Babel. Configuration lives in `babel.cfg`, translation files under `kunsthandel/translations/`. See `Translation Notes.adoc` for details.

## Tests

```bash
python -m unittest discover tests
```

Coverage reports can be generated using `coverage`.

## Deployment

A packaging and deployment guide is available in `Packaging, Distribution and Deployment.adoc`. For Windows deployments, `deploy.bat` is provided.

## License

Private project — see repository.
