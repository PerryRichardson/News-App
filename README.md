# Django News App

A small, educational news publishing project built with Django. It demonstrates a complete
flow: user auth with roles, reader subscriptions (publishers + journalists), journalist
article submission, editor review (approve/reject), subscriber notifications, and a REST
API (DRF). Also includes optional X (Twitter) posting on approval (feature-flagged).

This project was developed as part of a learning track to practice Django models, views,
templates, permissions, REST APIs, database migration, and unit testing.

---

## Features

### Core App (core/)
- **Authentication:** Register, Login, Logout
- **Custom user model with roles:** Reader, Journalist, Editor
- **Reader subscriptions**
  - Subscribe/unsubscribe to **Publishers**
  - Follow/unfollow **Journalists**
  - "My Subscriptions" page showing current subscriptions
- **Journalist area**
  - Journalist dashboard (`/journalist/`)
  - Create article (`/journalist/new/`) → saved as **PENDING**
- **Editor area**
  - Editor review queue (`/editor/`)
  - Approve/reject articles (reject can include a reason)
  - Create publishers (`/publishers/new/`)
- **Notifications**
  - On approval: email author (console backend in dev)
  - On approval: email subscribed readers of the publisher (console backend in dev)

---

## REST API (via Django REST Framework)

Reader-only endpoints (must be logged in as a **Reader**):

| Endpoint | Description |
|---|---|
| `GET /api/articles/feed/` | Union of subscribed publishers + followed journalists |
| `GET /api/articles/publishers/` | Articles from subscribed publishers only |
| `GET /api/articles/journalists/` | Articles from followed journalists only |

Behavior:
- Logged out → 401/403
- Logged in as Journalist or Editor → 403 (reader-only)
- Returns **APPROVED** articles only

---

## Optional X (Twitter) Integration

Fire-and-forget posting to X when an editor approves an article (off by default).

Toggle in `config/settings.py`:
```python
X_POST_ENABLED = False  # set True when credentials are configured
X_BEARER_TOKEN = ""
X_API_URL = "https://api.x.com/2/tweets"
```

---

## Technologies Used

- Python 3.12.x
- Django 6.0.x
- Django REST Framework
- MariaDB / MySQL (local dev) on port 3306
- mysqlclient 2.2.x
- HTML & CSS via Django templates
- Sphinx (documentation)
- Docker (containerisation)

---

## Getting Started — Option A: Virtual Environment (venv)

These instructions assume **Windows + PowerShell**.

### 1) Clone the repository
```powershell
git clone https://github.com/PerryRichardson/News-App.git
cd News-App
```

### 2) Create and activate a virtual environment
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3) Install dependencies
```powershell
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file in the project root with the following content:
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=your-database-password-here
DB_HOST=127.0.0.1
DB_PORT=3306
EDITOR_INVITE_CODE=your-invite-code-here
X_BEARER_TOKEN=
```

> **Never commit your `.env` file to GitHub.** It is already listed in `.gitignore`.

### 5) Database setup

**5.1)** Ensure your MySQL/MariaDB server is running locally.

**5.2)** Open a terminal and log in to MySQL as root:
```bash
mysql -u root -p
```

**5.3)** Run the following SQL commands:
```sql
CREATE DATABASE IF NOT EXISTS news_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'news_user'@'localhost'
  IDENTIFIED BY 'your-password-here';

GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

> Use the same password you set in your `.env` file for `DB_PASSWORD`.

### 6) Run migrations and start the server
```powershell
python manage.py migrate
python manage.py runserver
```

### 7) Register your first accounts

Visit `http://127.0.0.1:8000/accounts/register/` to create accounts.

| Role | Invite Code Required? | Notes |
|---|---|---|
| Reader | No | Default role |
| Journalist | No | Can submit articles |
| Editor | Yes — see `.env` | Can approve/reject articles and create publishers |

> The editor invite code is set via `EDITOR_INVITE_CODE` in your `.env` file.

### 8) Recommended first-time setup flow

1. Register an **Editor** account using the invite code from your `.env`
2. Log in as Editor and create at least one **Publisher** at `/publishers/new/`
3. Register a **Journalist** account and submit an article at `/journalist/new/`
4. Log back in as **Editor** and approve the article at `/editor/`
5. Register a **Reader** account, subscribe to the publisher, and view the feed

### 9) Run tests
```powershell
python manage.py test -v 2
```

If tests fail with database permission errors, grant the test database permissions:
```sql
mysql -u root -p

GRANT CREATE, DROP ON *.* TO 'news_user'@'localhost';
GRANT ALL PRIVILEGES ON `test\_%`.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

---

## Getting Started — Option B: Docker

These instructions assume you have **Docker Desktop** installed and running.

### 1) Clone the repository
```bash
git clone https://github.com/PerryRichardson/News-App.git
cd News-App
```

### 2) Configure environment variables

Create a `.env` file in the project root (same as Option A above).

### 3) Build the Docker image
```bash
docker build -t news-app .
```

### 4) Run the container
```bash
docker run --env-file .env -p 8000:8000 news-app
```

> This maps port 8000 on your machine to port 8000 inside the container.

### 5) Access the app

Visit `http://localhost:8000` in your browser.

> **Note:** The Docker setup connects to your local MySQL database.
> Ensure your database is running and `DB_HOST` in your `.env` is set
> to `host.docker.internal` instead of `127.0.0.1` when running via Docker.

---

## Documentation

This project uses Sphinx for documentation. The generated HTML docs are located in
`docs/_build/html/`. Open `docs/_build/html/index.html` in your browser to view them.

---

## Available URLs

| URL | Description | Role |
|---|---|---|
| `/` | Home — approved articles | All |
| `/accounts/login/` | Login | All |
| `/accounts/register/` | Register | All |
| `/publishers/` | Publisher list + subscribe | Authenticated |
| `/publishers/new/` | Create a publisher | Editor |
| `/journalists/` | Journalist list + follow | Reader |
| `/me/subscriptions/` | My subscriptions | Authenticated |
| `/journalist/` | Journalist dashboard | Journalist |
| `/journalist/new/` | Submit new article | Journalist |
| `/editor/` | Editor review queue | Editor |
| `/admin/` | Django admin panel | Superuser |
| `/api/articles/feed/` | API: combined feed | Reader |
| `/api/articles/publishers/` | API: publisher feed | Reader |
| `/api/articles/journalists/` | API: journalist feed | Reader |
