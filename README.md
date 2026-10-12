# My Site Django Blog

My Site is a Django blog application with user accounts, profiles, posts, tags, comments, image uploads, RSS feeds, a sitemap, and a Django REST Framework API.

## Features

- User registration, authentication, profiles, and username changes
- Post creation, publishing, deletion, search, tags, and pagination
- Comments with optional image uploads
- Content validation and profanity protection
- RSS feeds and XML sitemap support
- Django REST Framework API
- OpenAPI 3 documentation with drf-spectacular, Swagger UI, and ReDoc
- Static and media file support
- Docker and Docker Compose configuration
- Ruff, djLint, mypy, django-stubs, and DRF stubs

## Technology Stack

- Python 3.12+
- Django 6
- Django REST Framework
- SQLite for local development
- django-taggit, django-filter, and django-markdownx
- drf-spectacular
- Gunicorn and Docker

## Project Structure

```text
blog/                    Blog models, views, APIs, templates, and migrations
users/                   User features, templates, and static files
images/                  Image-related features
my_site/                 Django settings, URLs, ASGI, and WSGI modules
static/                  Project-level static files
manage.py                Django management entry point
requirements.txt         Python dependencies
Makefile                 Common development commands
Dockerfile               Docker image configuration
docker-compose.yml       Docker Compose configuration
```

## Local Development

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .pwsh
.\.pwsh\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Or use Make:

```bash
make install
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

The `.env` file is ignored by Git. Use a new random `SECRET_KEY`, set `DEBUG=False`, and configure production hosts before deployment.

### 4. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Or:

```bash
make migrate
make run
```

Open the application at:

```text
http://127.0.0.1:8000/
```

## API Documentation

Start the development server and open one of these URLs:

```text
Swagger UI: http://127.0.0.1:8000/api/docs/
ReDoc:      http://127.0.0.1:8000/api/redoc/
OpenAPI 3:  http://127.0.0.1:8000/api/schema/
```

The main API endpoints are under `/blog/api/`:

```text
/blog/api/posts/
/blog/api/posts/<id>/
/blog/api/comments/
/blog/api/comments/<id>/
/blog/api/tags/
/blog/api/tags/<slug>/
```

## Make Commands

```bash
make help
make install
make run
make migrate
make makemigrations
make shell
make test
make check
make deploy-check
make typecheck
make schema
make format
make lint
make html-check
```

If Make is not installed on Windows, use Git Bash or WSL, install GNU Make, or run the equivalent `python manage.py` and `python -m ...` commands directly.

## Docker

```bash
docker compose up --build
```

The current Docker configuration starts Django with the development server. For production, use Gunicorn behind an HTTPS reverse proxy, persistent media storage, a dedicated database, and regular backups.

## Quality Checks

```bash
python manage.py check
python manage.py test
python -m mypy blog users my_site
python -m ruff check .
python -m djlint blog/templates users/templates --check
python manage.py spectacular --file schema.yml --validate
```

Migration commands:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

Do not delete migrations that have already been applied to a shared database. Create and commit a new migration when models change.

## Security Notes

- Never commit `.env`, database files, logs, or uploaded media.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` for the real deployment domains.
- Enable HTTPS, secure cookies, CSRF cookie protection, and HSTS in production.
- Use a dedicated production database and regular backups.
- Review API authentication and permissions before exposing write endpoints publicly.

## License

No formal license has been selected for this project yet.
