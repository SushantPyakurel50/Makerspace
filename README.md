# The Forge — Makerspace Equipment Booking System

Enterprise Application Development Assignment (DBMS, Sem 4)
Python (Django) + Oracle Database

## What this is

A web application for managing bookings of shared equipment at a
community/university makerspace: 3D printers, woodworking tools,
electronics stations, and so on. Members book equipment, staff log
maintenance issues, and the system tracks overdue returns and late fees.

This is an original scenario built from scratch for this assignment
(not adapted from course tutorial examples).

## Architecture

The app is split into clear presentation / business / data-access layers:

```
makerspace_project/          Django project config (settings, URLs, WSGI/ASGI)
inventory/                   The single Django "app" containing everything
    models.py                 Data access layer: ORM models (5 linked tables)
    migrations/0001_initial.py  Django migration matching models.py
    serializers.py             DTOs: DRF serializers for server<->client data
    services.py                 Business layer: booking rules, CRUD orchestration
    tasks.py                     Background/async processing (see below)
    queries.py                   The 5 required queries (3 navigation + 2 complex)
    api_views.py / api_urls.py    REST API (JSON) - presentation layer for API clients
    web_views.py / web_urls.py    Server-rendered HTML GUI - presentation layer
    forms.py                     Django ModelForms backing the web GUI
    admin.py                     Django admin registration (handy for inspecting data)
    templates/inventory/         HTML templates for the web GUI
sql/
    create_tables.sql            Oracle DDL (tables, sequences, PK triggers)
    seed_data.sql                Sample data for demo/screenshots
requirements.txt
manage.py
```

### Database schema (5 linked tables)

- `category` (1) → (M) `equipment`
- `equipment` (1) → (M) `booking`
- `member` (1) → (M) `booking`
- `equipment` (1) → (M) `maintenance_record`

### Background / asynchronous processing component

When a member returns equipment (`POST /api/bookings/<id>/return/` or the
"Return" button in the GUI), the request returns immediately after marking
the booking `RETURNED`. A background worker thread (`inventory/tasks.py`)
then calculates any late fee and flips the equipment's status back to
`AVAILABLE`, updating the database without blocking the client. This
satisfies the requirement for "a background task or asynchronous
processing component that updates a database table based on a client
request" without needing an external broker (Celery/Redis) for the
assignment demo.

### The 5 required queries (`inventory/queries.py`)

Navigation queries:
1. `query_member_bookings` — Member → Booking → Equipment → Category
2. `query_equipment_by_category` — Category → Equipment
3. `query_maintenance_history` — Equipment → MaintenanceRecord

Complex queries (3+ entities):
4. `query_overdue_bookings_report` — Booking + Member + Equipment + Category
5. `query_equipment_utilization_report` — Equipment + Category + Booking (aggregated)

## Setup

### 1. Prerequisites

- Python 3.10+
- Oracle Database (XE, or any edition) reachable from your machine
- An Oracle schema/user for the app, e.g. `makerspace_app`

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the Oracle schema

Either let Django create it via migrations (recommended, step 4), or run
the hand-written DDL directly:

```bash
sqlplus makerspace_app/yourpassword@localhost:1521/XEPDB1 @sql/create_tables.sql
```

### 4. Configure the database connection

Set environment variables (or edit `makerspace_project/settings.py`
directly for local testing):

```bash
export DB_ENGINE=oracle
export ORACLE_DSN="localhost:1521/XEPDB1"
export ORACLE_USER="makerspace_app"
export ORACLE_PASSWORD="yourpassword"
```

To develop/test without Oracle installed, you can temporarily use SQLite:

```bash
export DB_ENGINE=sqlite
```

### 5. Run migrations and start the server

```bash
python manage.py migrate
python manage.py createsuperuser      # optional, for /admin/
python manage.py seed_demo_data       # optional, sample data for screenshots
python manage.py runserver
```

Then visit:
- Web GUI: http://127.0.0.1:8000/
- REST API root: http://127.0.0.1:8000/api/
- Django admin: http://127.0.0.1:8000/admin/

## API summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/categories/` | list / create categories |
| GET/PUT/DELETE | `/api/categories/<id>/` | retrieve / update / delete |
| GET/POST | `/api/members/` | list / create members |
| GET/PUT/DELETE | `/api/members/<id>/` | retrieve / update / delete |
| GET/POST | `/api/equipment/` | list / create equipment |
| GET/PUT/DELETE | `/api/equipment/<id>/` | retrieve / update / delete |
| GET/POST | `/api/bookings/` | list / create bookings |
| GET/DELETE | `/api/bookings/<id>/` | retrieve / delete |
| POST | `/api/bookings/<id>/return/` | return equipment (triggers background task) |
| POST | `/api/bookings/<id>/cancel/` | cancel an active booking |
| GET/POST | `/api/maintenance/` | list / log maintenance records |
| GET/PUT/DELETE | `/api/maintenance/<id>/` | retrieve / resolve / delete |
| GET | `/api/queries/members/<id>/bookings/` | navigation query 1 |
| GET | `/api/queries/categories/<id>/equipment/` | navigation query 2 |
| GET | `/api/queries/equipment/<id>/maintenance/` | navigation query 3 |
| GET | `/api/queries/overdue-bookings/` | complex query 1 |
| GET | `/api/queries/equipment-utilization/` | complex query 2 |

## Notes

The project is pinned to the versions listed in `requirements.txt` and has
been syntax-checked with `python -m compileall`. A repeatable `smoke_test.py`
script is included; it exercises the web dashboard, CRUD list endpoints, all
five required queries, booking validation and lifecycle actions, and the
background return-processing worker. Run it after applying migrations and
loading demo data:

```bash
DB_ENGINE=sqlite python manage.py migrate --noinput
DB_ENGINE=sqlite python manage.py seed_demo_data
DB_ENGINE=sqlite python smoke_test.py
```

Before submission, run the setup steps above end-to-end against the target
Oracle instance. This confirms that the migration or hand-written DDL applies
cleanly to the selected Oracle version and catches any environment-specific
connection or privilege settings.

