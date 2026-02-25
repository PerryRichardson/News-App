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
- MariaDB 12.x (local dev) on port 3307 (chosen because 3306 was already in use)
- mysqlclient 2.2.x
- HTML & CSS via Django templates
---

## Getting Started (Step-by-step)

These instructions assume **Windows + PowerShell**.

### 1) Clone the repository
```powershell
git clone <REPO_URL>
cd News-App
```
### 2) Activate virtual environment
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
 4.1) Ensure **MySQL/MariaDB** is running (default port is usually 3306)
 4.2) Create the database and user:
```
  CREATE DATABASE news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

  CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'strong_password_here';

  GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';

  FLUSH PRIVILEGES;
```
 4.3) Create the database and user:
```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_db",
        "USER": "news_user",
        "PASSWORD": "strong_password_here",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
```
### 5) Run the project:
  #### 5.1) Apply migrations
```
cd src
python manage.py migrate
```
  #### 5.2) Create admin user/superuser
```
python manage.py createsuperuser
```
  #### 5.3) Start server
```
python manage.py runserver
```
### 6) First-time Setup in the Admin Site:
1) Go to `/admin/`
2) Add Groups - Journalists/Editors/Readers/Publishers
3) Create users for each role/group
   -In /admim/, create users and set their role:
     - Reader: subscribe + API access
     - Journalist: Submit articles (PENDING)
     - Editor: Approve/reject articles

### 7) Run tests:
- Run from `src` root
```
python manage.py test -v 2
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

