# Django News App

A small, educational news publishing project built with Django. It demonstrates a complete flow: user auth with roles, reader subscriptions (publishers + journalists), journalist article submission, editor review (approve/reject), subscriber notifications, and a REST API (DRF). Also includes optional X (Twitter) posting on approval (feature-flagged).

This project was developed as part of a learning track to practice Django models, views, templates, permissions, REST APIs, database migration, and unit testing.

---

## Features

### Core App (core/)
- **Authentication:** Register, Login, Logout
- **Custom user model with roles:** Reader, Journalist, Editor
- **Reader subscriptions**
  - Subscribe/unsubscribe to **Publishers**
  - Follow/unfollow **Journalists**
  - “My Subscriptions” page showing current subscriptions
- **Journalist area**
  - Journalist dashboard (`/journalist/`)
  - Create article (`/journalist/new/`) → saved as **PENDING**
- **Editor area**
  - Editor review queue (`/editor/`)
  - Approve/reject articles (reject can include a reason)
- **Notifications**
  - On approval: email author (console backend in dev)
  - On approval: email subscribed readers of the publisher (console backend in dev; excludes author)

---

## REST API (api/ via Django REST Framework)

Reader-only endpoints (must be logged in as a **Reader**):
- **Feed (union of subscribed publishers + followed journalists)**
  - `GET /api/articles/feed/`
- **Publisher subscriptions feed**
  - `GET /api/articles/publishers/`
- **Followed journalists feed**
  - `GET /api/articles/journalists/`

Behavior:
- Logged out → 401/403 (depending on auth settings)
- Logged in as Journalist/Editor → 403 (reader-only permission)
- Returns **APPROVED** articles only
---
## Optional Tweet (X) Integration

Fire-and-forget posting to X when an editor approves an article (off by default / safe by design).

Toggle in `config/settings.py`:
```python
X_POST_ENABLED = False  # set True when configured
X_BEARER_TOKEN = ""
X_API_URL = "https://api.x.com/2/tweets"
```
---
## Technologies Used

- Python 3.12.x (required for smooth mysqlclient on Windows)
- Django 6.0.x
- Django REST Framework
- MariaDB 12.x (local dev) on port 3306
- mysqlclient 2.2.x
- HTML & CSS via Django templates
---

## Getting Started (Step-by-step)

These instructions assume **Windows + PowerShell**.

### 1) Clone the repository
```powershell
git clone https://github.com/PerryRichardson/News-App.git
cd News-App
```
### 2) Create + activate a virtual environment:
```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```
### 3) Install dependencies
```
pip install -r requirements.txt
```
### 4) Database setup
 4.1) Ensure your **MySQL/MariaDB** server is running locally
 4.2) Create the database and user

Run the following in MySQL Workbench (or another SQL client):
```
CREATE DATABASE IF NOT EXISTS news_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'news_user'@'localhost'
  IDENTIFIED BY 'StrongPassword123!'; -- example password (change for your machine)

GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```
 4.3) Update `settings.py`:
```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_db",
        "USER": "news_user",
        "PASSWORD": "StrongPassword123!",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
```
### 5) Run the project:
```
cd src
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
### 6) First-time Setup (in the app):
- Login as an **Editor** to approve/reject articles at `/editor/`.
- Editors can create publishers in-app at `/publishers/new/`.
- Journalists can submit articles at `/journalist/new/` (saved as **PENDING** until approved).
  
**Editor registration:** If your project uses an invite code, set `EDITOR_INVITE_CODE` in `src/config/settings.py` and enter it during registration when selecting the Editor role.

### Test Accounts & Registration

To register as an Editor, use the invite code: newsapp-editor-2026

### 7) Run tests:
- Run from `src` folder
```
python manage.py test -v 2
```
- If tests fail with database permission errors, ensure the DB user can create/drop the test DB:
```
GRANT CREATE, DROP ON *.* TO 'news_user'@'localhost';
GRANT ALL PRIVILEGES ON `test\_%`.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```
---

## Once installed, view apps at:
- http://127.0.0.1:8000/ → Home (approved articles)
- http://127.0.0.1:8000/accounts/login/ → Login
- http://127.0.0.1:8000/accounts/register/ → Register
- http://127.0.0.1:8000/publishers/ → Publisher subscriptions (Reader)
- http://127.0.0.1:8000/journalists/ → Journalist follows (Reader)
- http://127.0.0.1:8000/me/subscriptions/ → My Subscriptions (Reader)
- http://127.0.0.1:8000/journalist/ → Journalist dashboard
- http://127.0.0.1:8000/journalist/new/ → Add article (Journalist)
- http://127.0.0.1:8000/editor/ → Editor review queue
- http://127.0.0.1:8000/admin/ → Django admin
- http://127.0.0.1:8000/api/articles/feed/ → API: Reader feed
- http://127.0.0.1:8000/api/articles/publishers/ → API: Publisher feed
- http://127.0.0.1:8000/api/articles/journalists/ → API: Journalist feed

