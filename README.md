# Support Ticket Management System

A full-stack support ticket portal built for the Junior Full Stack Developer technical
assessment. Customers can raise and track tickets; support agents can triage, assign,
update and respond to them.

- **Frontend:** React (Create React App), React Router, Axios
- **Backend:** Python + Django REST Framework
- **Database:** MySQL
- **Auth:** JWT (djangorestframework-simplejwt), password hashing via Django's PBKDF2 hasher
- **Testing:** PyTest (backend, 15 tests) + Postman collection

## 1. Project Structure

```
support-ticket-system/
├── backend/            # Django REST API
│   ├── accounts/       # Custom User model, register/login/logout
│   ├── tickets/        # Ticket & TicketComment models, views, permissions
│   ├── tests/          # PyTest suite (auth + ticket behavior)
│   └── ticketsystem/   # Django project settings/urls
├── frontend/           # React application
│   └── src/
│       ├── api/        # Axios client with JWT + auto-refresh
│       ├── context/    # AuthContext
│       ├── components/ # Navbar, ProtectedRoute
│       └── pages/      # Login, Register, Dashboards, TicketDetail, CreateTicket
├── database/
│   ├── schema.sql      # MySQL schema (mirrors Django's models)
│   └── seed.sql        # Sample users/tickets/comments
├── postman_collection.json
├── docker-compose.yml  # Optional local dev convenience
├── .env.example
└── README.md
```

## 2. Data Model

| Table | Key columns |
|---|---|
| `users` | id, name (first/last), email (unique, login field), password_hash, role (`customer`/`agent`), created_at |
| `tickets` | id, user_id (FK → users, customer), subject, description, priority, status, assigned_to (FK → users, agent, nullable), created_at, updated_at |
| `ticket_comments` | id, ticket_id (FK → tickets), user_id (FK → users), comment, created_at |

Indexes exist on `status`, `priority`, `(status, priority)`, `created_at` and `subject`
(plus a full-text index) to keep search/filter/sort fast as ticket volume grows.

**Example JOIN query** (also in `database/schema.sql`) — all open tickets with the
customer's name and email:

```sql
SELECT t.id, t.subject, t.priority, t.status, t.created_at,
       u.name AS customer_name, u.email AS customer_email
FROM tickets t
JOIN users u ON u.id = t.user_id
WHERE t.status = 'open'
ORDER BY t.created_at DESC;
```

## 3. Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0 (running locally, or use `docker-compose up db`)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example .env      # or backend/.env.example — see below
# edit .env with your MySQL credentials and a real DJANGO_SECRET_KEY

# create the database (only needed if not using the docker MySQL image,
# which auto-loads database/schema.sql + seed.sql on first boot):
mysql -u root -p -e "CREATE DATABASE support_ticket_db CHARACTER SET utf8mb4;"

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access

python manage.py runserver         # API on http://localhost:8000
```

A `backend/.env.example` is included with all required variables
(`DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`,
`CORS_ALLOWED_ORIGINS`, JWT lifetimes). Copy it to `backend/.env` and fill in real
values — never commit the `.env` file itself.

**Optional:** load `database/seed.sql` after `schema.sql` for demo data (4 users,
5 tickets, 5 comments — all demo accounts use password `Password123!`). If you used
`manage.py migrate` instead of the raw schema.sql, register users through the API
or `createsuperuser` instead, since Django manages its own migrations table.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env    # set REACT_APP_API_BASE_URL if the API isn't on localhost:8000
npm start                # app on http://localhost:3000
```

### Running with Docker (optional)

```bash
docker compose up --build
```
This starts MySQL (auto-seeded from `database/schema.sql` + `seed.sql`), the Django
API on port 8000, and the React dev server on port 3000.

## Deploying on Railway

The root `railway.json` selects `backend/Dockerfile`, so Railway builds the Django
API instead of trying to detect a start script at the monorepo root. Add a Railway
MySQL service to the project; the backend recognizes Railway's `MYSQLHOST`,
`MYSQLPORT`, `MYSQLDATABASE`, `MYSQLUSER`, and `MYSQLPASSWORD` variables.

Set `DJANGO_SECRET_KEY` to a unique secret, `DJANGO_ALLOWED_HOSTS` to the backend
public domain, and `CORS_ALLOWED_ORIGINS` to the frontend public URL in the backend
service's variables. The container runs migrations, collects static files, and
serves Django with Gunicorn. For the React frontend, create a separate Railway
service with its root directory set to `/frontend` and configure
`REACT_APP_API_BASE_URL` to the backend public URL followed by `/api`.

## 4. Running Tests

```bash
cd backend
export PYTEST_RUNNING=1          # runs against a local SQLite file instead of MySQL
export DJANGO_SECRET_KEY=test-key
python manage.py migrate
python -m pytest tests/ -v
```

16 tests cover: the public API root, registration, valid/invalid login, unauthenticated access being
rejected, ticket creation, role-restricted ticket creation, cross-customer ticket
isolation, agent status/assignment updates, customers being blocked from changing
status, 404s for unknown tickets, comments, and role-based 403s.

`PYTEST_RUNNING=1` is only a convenience switch for the test suite so it doesn't
require a live MySQL server — the app always uses MySQL in development/production.

## 5. API Testing (Postman)

Import `postman_collection.json` into Postman. It includes requests (with basic
assertions) for: successful/duplicate registration, valid/invalid login, token
refresh, logout, ticket creation, listing/filtering tickets, retrieving a ticket,
adding a comment, invalid input, a not-found ticket, an unauthenticated request,
a forbidden (wrong-role) request, agent-only ticket updates/assignment/deletion,
and the agent stats endpoint. Run "Login as Customer" / "Login as Agent" first —
their test scripts populate the token variables used by later requests.

## 6. Authentication & Authorization

- Passwords are hashed with Django's PBKDF2 hasher; nothing is ever stored in plain text.
- Login/registration use **email**, not username, as the identifier.
- JWT access + refresh tokens are issued on login (`djangorestframework-simplejwt`).
  Access tokens are short-lived; the frontend transparently refreshes them on a 401.
- Logout blacklists the refresh token server-side (`token_blacklist` app) so it can't
  be reused after the user signs out.
- **Authentication** (is this a valid token?) and **authorization** (is this user
  allowed to do this?) are handled separately: DRF's JWT authentication class verifies
  the token, while per-view permission classes (`IsCustomer`, `IsAgent`,
  `IsTicketOwnerOrAgent`) and object-level checks in the view logic enforce role and
  ownership rules — e.g. a customer can only ever see/comment on their own tickets,
  and only agents can change ticket status, priority, assignment, or delete a ticket.

## 7. REST API Reference

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/` | Public — API landing page with links to available endpoints |
| POST | `/api/auth/register` | Public — creates a customer account |
| POST | `/api/auth/login` | Public — returns `access`, `refresh`, `user` |
| POST | `/api/auth/refresh` | Public — exchanges a refresh token for a new access token |
| POST | `/api/auth/logout` | Authenticated — blacklists the refresh token |
| GET | `/api/tickets` | Authenticated — customers see only their own; agents see all. Supports `?search=`, `?status=`, `?priority=`, `?ordering=` |
| POST | `/api/tickets` | Customer only |
| GET | `/api/tickets/:id` | Owning customer or any agent |
| PUT | `/api/tickets/:id` | Agents can update any field; the owning customer may only edit subject/description |
| DELETE | `/api/tickets/:id` | Agent only |
| GET | `/api/tickets/:id/comments` | Owning customer or any agent |
| POST | `/api/tickets/:id/comments` | Owning customer or any agent |
| GET | `/api/tickets/stats` | Agent only — dashboard counts by status/priority |
| GET | `/api/users?role=agent` | Agent only — used to populate the assignment dropdown |

All error responses follow `{"error": true, "status_code": ..., "detail": ...}` with
appropriate HTTP status codes (400/401/403/404).

## 8. Security Notes

- Parameterized queries throughout (Django ORM) — no raw/string-built SQL.
- CORS restricted via `CORS_ALLOWED_ORIGINS` env var to the frontend's origin.
- Secrets (DB credentials, `DJANGO_SECRET_KEY`) are read from environment
  variables — see `backend/.env.example` — and `.env` is git-ignored.
- Object-level checks prevent IDOR (e.g. a customer requesting another
  customer's ticket ID gets a 403, not the ticket).

## 9. Deployment

This app is designed to deploy as two services plus a managed database:

1. **Database:** any managed MySQL (PlanetScale, AWS RDS, Railway, Render). Run
   `database/schema.sql` or `python manage.py migrate` against it.
2. **Backend:** deploy `backend/` to Railway/Render/Fly.io/an EC2 instance. Set
   `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` to the backend's domain, and all
   `DB_*`/`CORS_ALLOWED_ORIGINS` env vars from `.env.example`. Run
   `python manage.py migrate` as a release step.
3. **Frontend:** deploy `frontend/` to Vercel/Netlify/Render static hosting. Set
   `REACT_APP_API_BASE_URL` to the deployed backend's `/api` URL at build time.

Once deployed, record the live URLs below (fill in before submission):

- **Live frontend URL:** _add after deploying_
- **Live backend/API URL:** _add after deploying_
- **GitHub repository URL:** _add after pushing_

## 10. Git Workflow

Commit incrementally rather than as one final upload, e.g.:
`chore: project scaffold` → `feat: user model + JWT auth` → `feat: ticket CRUD API`
→ `feat: comments + permissions` → `test: backend test suite` →
`feat: React auth flow` → `feat: dashboards + ticket detail` →
`docs: README + Postman collection` → `chore: deployment config`.

## 11. What Wasn't Built (per the assessment's "optional enhancements")

Docker is included only as a convenience, not a requirement. TypeScript,
pagination, file attachments, email notifications, CI/CD, Redis caching, and
advanced monitoring were intentionally left out as explicitly optional/out of
scope for this assessment.
