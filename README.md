# MOOC Course Catalog | [Live Demo](https://mooc-platform-deploy.vercel.app/)

A clean, scalable MOOC-style course catalog built with Django + PostgreSQL.


## One-Command Local Demo (Docker + Sqlite)

Creates sample deployment with docker and sample data added to test locally faster.

```bash
chmod +x local_run.sh
./local_run.sh
```


## What's included

**Student features**
- Sign up / log in
- Browse course catalog
- View course details and lesson list
- Enroll in courses
- Watch lessons with YouTube (privacy-enhanced) or direct video support
- Lesson progress tracking (visited/unwatched indicator in sidebar)
- "My Courses" page

**Staff / Admin features**
- Staff web UI at `/manage/` — no Django admin knowledge required
- Full Course CRUD (create, edit, delete)
- Full Lesson CRUD with live YouTube preview while pasting URL
- Lessons support: YouTube (any URL format), direct video (.mp4/.webm), or text-only
- Django Admin CRUD with inline lesson editor and video preview
- Staff nav link visible to `is_staff` users automatically


## Architecture

```
mooc/
├── config/                  # Django project settings (split by env)
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Dev overrides (SQLite)
│   │   └── production.py    # Prod overrides (PostgreSQL)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/            # Auth: signup, login, logout
│   ├── courses/             # Course & Lesson models, student views,
│   │   │                    # staff management views, admin, forms
│   │   ├── forms.py         # CourseForm + LessonForm with validation
│   │   └── views.py         # Student views + staff /manage/ views
│   ├── enrollments/         # Enrollment model + service
│   └── progress/            # LessonProgress model + service
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── courses/
│   │   ├── course_list.html
│   │   ├── course_detail.html
│   │   ├── lesson_detail.html   ← renders YouTube/video/text
│   │   ├── my_courses.html
│   │   └── manage/              ← Staff management UI
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── course_form.html
│   │       ├── course_detail.html
│   │       ├── course_confirm_delete.html
│   │       ├── lesson_form.html  ← live YouTube preview JS
│   │       └── lesson_confirm_delete.html
├── static/css/main.css      # All styles including video player
└── fixtures/sample_data.json
```

## Video / YouTube implementation

- Staff pastes any YouTube URL format (watch, short, embed, youtu.be) into the lesson form
- A **live preview** renders immediately in the form via vanilla JS — no page reload
- The model's `save()` auto-classifies `video_type` (youtube / direct / none)
- `youtube_embed_url` property returns a `youtube-nocookie.com` embed URL — this is YouTube's **privacy-enhanced mode**: no cookies are set, no tracking until the user clicks play. Standard practice for MOOC/educational platforms.
- Extra embed params: `rel=0` (no unrelated recommendations), `modestbranding=1`
- Direct video URLs render via `<video controls>` HTML5 player
- The responsive 16:9 container works on all screen sizes

## Design Decisions

- **Service Layer**: Business logic (enroll, track progress) lives in `services.py` per app — not in views or models.
- **Staff views vs Django Admin**: Both exist. Staff UI (`/manage/`) is a clean, purpose-built interface. Admin is the power tool. Neither replaces the other.
- **`@staff_member_required`**: Django's built-in decorator — redirects to admin login (not 403). Any user with `is_staff=True` gets access.
- **`video_type` is non-editable**: Set automatically in `save()` to stay consistent with `video_url`. Staff only sees `video_url`.
- **N+1 prevention**: `select_related` / `prefetch_related` in every view that touches related objects.
- **Form validation**: `LessonForm.clean_video_url()` rejects YouTube URLs that don't contain a valid 11-char video ID.

## Quick Start (Docker)

```bash
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py createsuperuser
# Visit http://localhost:8000
# Staff UI: http://localhost:8000/manage/
# Admin:    http://localhost:8000/admin/
```

## Quick Start (Local / SQLite)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt

export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/sample_data.json   # optional sample data
python manage.py runserver
```

## Making a user staff

In the Django admin, edit a user and check `Staff status`. Or via shell:

```python
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='yourname').update(is_staff=True)
```

## Running Tests

```bash
python manage.py test apps --verbosity=2
```

Tests cover: video URL classification, YouTube ID extraction, nocookie embed URL, enrollment idempotency, progress tracking, access control, staff CRUD, YouTube form validation.

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | True/False |
| `DATABASE_URL` | Postgres URL (production) |
| `ALLOWED_HOSTS` | Comma-separated hosts |


## Scaling Considerations

- **Database**: PostgreSQL with connection pooling (pgBouncer) for high concurrency.
- **Caching**: Django cache framework ready — add Redis cache backend for course list.
- **Progress tracking**: `LessonProgress` uses `get_or_create` — idempotent, safe under concurrent requests.
- **Media files**: Lesson video/content URLs stored as fields — actual storage delegated to S3/CDN via django-storages.
- **Async**: Django 4.1+ async views can be adopted incrementally for IO-heavy lesson streaming.
- **API-ready**: Service layer can be exposed as DRF endpoints without changing business logic.
