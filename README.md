# Recetario

A modern, self-hosted recipe management web application built as a clean modular monolith.

---

## Technology Stack

- **Backend**: Python 3.12+ with [FastAPI](https://fastapi.tiangolo.com/).
- **Database & ORM**: PostgreSQL 16 with [SQLAlchemy 2.x](https://docs.sqlalchemy.org/en/20/) session management.
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/).
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) and `pydantic-settings`.
- **Frontend**: [SvelteKit](https://kit.svelte.dev/) with TypeScript and Svelte 5.
- **Frontend Web Server & Proxy**: Unprivileged [Nginx](https://hub.docker.com/r/nginxinc/nginx-unprivileged) serving the production build and proxying `/api` requests to FastAPI.
- **Deployment**: Docker Compose with persistent volumes for database records and recipe media uploads.
- **Automated Testing**: [pytest](https://docs.pytest.org/) with isolated in-memory test fixtures.

---

## Architectural Design

Recetario is architected as a **modular monolith** emphasizing strict separation of concerns, maintainability, and clean dependency injection without premature abstractions:

```
recetario/
├── backend/
│   ├── app/
│   │   ├── api/             # HTTP routing & endpoint controllers (FastAPI)
│   │   │   ├── router.py    # Master router aggregating feature routes
│   │   │   └── v1/
│   │   │       └── health.py # GET /api/health endpoint
│   │   ├── core/            # Core infrastructure & configuration
│   │   │   ├── config.py    # Environment settings via Pydantic
│   │   │   ├── database.py  # SQLAlchemy engine, session maker & get_db dependency
│   │   │   └── logging.py   # Structured logging & request telemetry middleware
│   │   ├── models/          # SQLAlchemy Declarative models & UTC timestamp mixins
│   │   │   └── base.py
│   │   ├── schemas/         # Pydantic validation request & response schemas
│   │   │   └── health.py
│   │   ├── services/        # Business logic & database querying routines
│   │   │   └── health.py
│   │   └── main.py          # Application entrypoint, lifespan, CORS, and middleware
│   ├── alembic/             # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── tests/               # Backend test suite
│   │   ├── conftest.py      # Isolated test fixtures & database overrides
│   │   └── test_health.py   # Health endpoint unit and integration tests
│   ├── Dockerfile           # Non-root unprivileged backend container
│   ├── requirements.txt     # Pinned production dependencies
│   ├── requirements-dev.txt # Pinned development/testing dependencies
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/         # Typed API clients (keeps HTTP separate from UI)
│   │   │   │   └── client.ts
│   │   │   ├── components/  # Presentation UI components (clean culinary design)
│   │   │   │   ├── Navbar.svelte
│   │   │   │   ├── StatusBadge.svelte
│   │   │   │   ├── ComponentCard.svelte
│   │   │   │   ├── MetricCard.svelte
│   │   │   │   └── Footer.svelte
│   │   │   ├── stores/      # Reactive stores & state management
│   │   │   │   └── health.ts
│   │   │   └── types/       # Shared TypeScript domain contracts
│   │   │       └── health.ts
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   └── +page.svelte # Health status dashboard
│   │   ├── app.css          # Design system tokens, warm culinary palette & CSS variables
│   │   └── app.html
│   ├── nginx.conf           # Reverse proxy configuration
│   ├── Dockerfile           # Multi-stage build (Node build -> Nginx unprivileged)
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml       # Multi-service composition (db, backend, frontend)
├── .env.example             # Documented environment template
├── .gitignore
└── README.md
```

### Key Architectural Decisions

1. **Modular Monolith**: Eliminates the overhead of microservices while strictly isolating concerns into separate layers (`api`, `schemas`, `models`, `services`, `core`).
2. **Reverse Proxying**: The frontend web server (Nginx in production, Vite proxy in local development) serves the application and proxies `/api/*` requests directly to FastAPI. The browser never needs hardcoded backend URLs.
3. **Internal Database Isolation**: PostgreSQL is strictly connected to the internal Docker bridge network (`recetario_network`) and is not exposed to host ports by default.
4. **Timezone-Aware UTC Standard**: All backend timestamps are strictly timezone-aware UTC (`datetime.now(timezone.utc)`), standardizing record keeping.
5. **Persistent Storage**:
   - `postgres_data`: Persistent volume for PostgreSQL database storage.
   - `recipe_uploads`: Persistent volume mounted at `/app/uploads` (configurable via `UPLOAD_DIR`) for future recipe images.
6. **Container Security**: Both backend and frontend containers execute as non-root users (`appuser` with UID 10001 in backend, `nginx-unprivileged` with UID 101 in frontend).

---

## Quickstart (Docker Compose)

### 1. Configure Environment

Copy the example environment configuration:
```bash
cp .env.example .env
```

### 2. Start the Application

Run the Compose command to build and launch all services:
```bash
docker compose up -d --build
```

### 3. Verify Application

Open your browser and navigate to:
- **Frontend Dashboard**: [http://localhost:3041](http://localhost:3041)
- **Health Check Endpoint**: [http://localhost:3041/api/health](http://localhost:3041/api/health)

### 4. Inspect Logs & Status

```bash
# View real-time logs across all services
docker compose logs -f

# Check container health status
docker compose ps
```

### 5. Stop the Application

```bash
docker compose down
```

---

## Local Development (Without Docker)

### Backend Setup

1. **Navigate to the backend directory and activate a virtual environment**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

2. **Configure local environment**:
   Ensure `.env` in the root (or `backend/.env`) has the database configuration. For local testing without PostgreSQL running, SQLite fallback is handled in unit tests.

3. **Run the FastAPI development server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8041
   ```
   Interactive OpenAPI documentation is accessible at `http://127.0.0.1:8041/api/docs`.

### Frontend Setup

1. **Navigate to the frontend directory and install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   The Vite dev server proxies `/api` requests to `http://localhost:8041`. Open `http://localhost:5173`.

---

## Running Tests & Checks

### Backend Unit & Integration Tests

From the workspace root or inside `backend`:
```bash
backend/.venv/bin/pytest backend/tests -v
```

The health check test verifies:
- Operational status code `200 OK`
- Pydantic response schema compliance
- Downstream database and storage accessibility
- Fallback degradation when database connectivity drops
- Timezone-aware UTC timestamp parsing

### Frontend Type-Checking and Build

```bash
cd frontend
npm run check
npm run build
```

### Database Migrations (Alembic)

When models are added to `backend/app/models/`:
```bash
# Generate a new migration revision
backend/.venv/bin/alembic -c backend/alembic.ini revision --autogenerate -m "create_recipes_table"

# Apply pending migrations
backend/.venv/bin/alembic -c backend/alembic.ini upgrade head
```

---

## CI/CD Pipelines (GitHub Actions)

Recetario includes automated GitHub Actions workflows located in `.github/workflows/`:

### 1. Continuous Integration (`ci.yml`)
Runs automatically on every push and pull request to the `main` branch:
- **Backend Job**: Sets up Python 3.12, installs dependencies, runs `pytest` test suite, and checks Alembic migration configurations.
- **Frontend Job**: Sets up Node.js 22, runs `svelte-check` type checking, and builds the production bundle with Vite.
- **Docker Compose Integration Job**: Builds all containers, launches the composition, polls service health until all services report healthy, executes a smoke test against `http://localhost:3041/api/health`, and ensures clean teardown.

### 2. Continuous Delivery (`cd.yml`)
Runs on pushes to `main` and on version tags (`v*.*.*`):
- Uses Docker Buildx and QEMU to cross-compile images for `linux/amd64` and `linux/arm64`.
- Authenticates securely with GitHub Container Registry (`ghcr.io`).
- Pushes multi-arch images for `ghcr.io/<owner>/recetario/backend` and `ghcr.io/<owner>/recetario/frontend` tagged with git branch, commit SHA, semver tag, and `latest`.

---


## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Recetario` | Name of the application |
| `ENVIRONMENT` | `production` | Deployment mode (`production`, `development`, `test`) |
| `VERSION` | `0.1.0` | Application version identifier |
| `LOG_LEVEL` | `INFO` | Logger verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PORT` | `3041` | Host port mapped to the frontend web server |
| `POSTGRES_SERVER` | `db` | Database hostname (`db` in Docker, `localhost` locally) |
| `POSTGRES_PORT` | `5432` | PostgreSQL internal port |
| `POSTGRES_DB` | `recetario` | Database name |
| `POSTGRES_USER` | `recetario` | Database user |
| `POSTGRES_PASSWORD` | `recetario_secret` | Database user password |
| `UPLOAD_DIR` | `/app/uploads` | Persistent path for media uploads |
| `CORS_ORIGINS` | `http://localhost:3041,...` | Allowed CORS origins for the API |
