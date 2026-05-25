#!/usr/bin/env python
"""Seed the database with realistic developer incidents processed through the Buster crew."""

from crew import Buster
from db.database import save_bust

INCIDENTS = [
    {
        "entry": (
            "Project: devcontainer setup. "
            "Issue: Docker daemon not running inside the devcontainer — docker ps returns 'Cannot connect to the Docker daemon'. "
            "Solution attempted: mounted /var/run/docker.sock from the host into the devcontainer via devcontainer.json. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: backend API. "
            "Issue: Git rebase conflict blocking the CI pipeline — the pipeline failed with merge conflicts on the feature branch. "
            "Solution attempted: ran git rebase --abort, pulled latest main, resolved conflicts manually, then rebased again. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: data pipeline. "
            "Issue: ModuleNotFoundError when importing a local package after restructuring the project directory. "
            "Solution attempted: added __init__.py to the package directory and installed the project in editable mode with pip install -e . "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: web app. "
            "Issue: CORS error on FastAPI — the frontend was getting blocked by missing CORS headers on preflight requests. "
            "Solution attempted: added CORSMiddleware to the FastAPI app with the correct allow_origins list. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: local development. "
            "Issue: Port 8000 already in use when starting the dev server — OSError: address already in use. "
            "Solution attempted: ran lsof -i :8000 to find the process, killed it with kill -9, then restarted the server. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: API integration. "
            "Issue: SSL certificate verification error when making HTTPS requests to an internal staging server. "
            "Solution attempted: added the internal CA certificate to the trusted store and passed verify=True with the cert path. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: Flask application. "
            "Issue: Environment variable DATABASE_URL not loading in production — the app was connecting to localhost instead of the prod DB. "
            "Solution attempted: discovered the .env file was not being loaded, added python-dotenv and called load_dotenv() at startup. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: machine learning project. "
            "Issue: pip dependency conflict — two packages required incompatible versions of numpy. "
            "Solution attempted: created a fresh virtual environment, pinned numpy to the version that satisfied both, and updated requirements.txt. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: microservices. "
            "Issue: Docker Compose services could not communicate with each other — connection refused between containers. "
            "Solution attempted: replaced localhost with the service name in the connection string, as Docker Compose uses service names for DNS. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: auth service. "
            "Issue: JWT tokens expiring immediately — users were being logged out seconds after signing in. "
            "Solution attempted: found that the expiry was set in seconds instead of hours, corrected the timedelta to hours=24. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: CLI tool. "
            "Issue: SQLite database locked error when running concurrent workers — OperationalError: database is locked. "
            "Solution attempted: switched the connection to use WAL journal mode and added retry logic, but concurrent writes still cause occasional locks. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
    {
        "entry": (
            "Project: Python service. "
            "Issue: uv sync failed with a resolution error — could not find a compatible version of a transitive dependency. "
            "Solution attempted: ran uv lock --upgrade-package on the conflicting package and re-synced. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: monorepo. "
            "Issue: Pre-commit hook failing with ruff errors on every commit — the hook was checking files that were already formatted. "
            "Solution attempted: ran ruff format before committing and added ruff to the pre-commit config with the correct args. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: CI/CD pipeline. "
            "Issue: GitHub Actions workflow failing with permission denied when trying to push a Docker image to the registry. "
            "Solution attempted: added the GITHUB_TOKEN secret to the workflow and authenticated with docker login using it. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: containerised app. "
            "Issue: Docker build failing with COPY failed — the file path in the Dockerfile did not match the actual file location. "
            "Solution attempted: corrected the COPY instruction to use paths relative to the build context, not the Dockerfile location. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: REST API. "
            "Issue: FastAPI returning 422 Unprocessable Entity — the request body was valid JSON but the Pydantic model had a type mismatch. "
            "Solution attempted: checked the schema with /docs, found an int field was receiving a string, updated the model to coerce the type. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: async service. "
            "Issue: async function returning a coroutine object instead of the result — called the function without await. "
            "Solution attempted: added await to the call site, but some callers are in sync context and cannot use await. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
    {
        "entry": (
            "Project: caching layer. "
            "Issue: Redis connection refused — the app could not connect to Redis on startup. "
            "Solution attempted: checked docker ps, Redis container had crashed due to OOM, restarted it and added a memory limit. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: production deployment. "
            "Issue: nginx returning 502 Bad Gateway after deploying a new version of the backend. "
            "Solution attempted: checked the upstream server address in nginx.conf, the port had changed in the new version. Updated the config and reloaded nginx. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: test suite. "
            "Issue: pytest failing with ImportError — the test file could not import the module under test. "
            "Solution attempted: added the src directory to PYTHONPATH in pyproject.toml under tool.pytest.ini_options. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: remote server. "
            "Issue: SSH connection failing with permission denied — could not authenticate with the SSH key. "
            "Solution attempted: ran chmod 600 on the private key file, as SSH rejects keys that are world-readable. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: data processing. "
            "Issue: MemoryError when processing a large CSV file — the script was loading the entire file into memory. "
            "Solution attempted: switched to chunked reading with pandas read_csv chunksize parameter, but downstream processing still peaks too high. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
    {
        "entry": (
            "Project: containerised service. "
            "Issue: Docker volume mount causing permission denied — the container process could not write to the mounted directory. "
            "Solution attempted: added a user directive to the Dockerfile to match the host user UID, fixed the permission issue. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: database migrations. "
            "Issue: Alembic migration conflict — two developers created migrations from the same revision head. "
            "Solution attempted: merged the migration heads with alembic merge heads and created a new merge revision. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: typed Python service. "
            "Issue: mypy type error — function expected Optional[str] but was receiving str | None from a newer Python version. "
            "Solution attempted: updated the type annotation to use str | None syntax and upgraded mypy to a compatible version. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: webhook integration. "
            "Issue: Webhook not receiving events from the third-party service — the endpoint was returning 200 but no data was arriving. "
            "Solution attempted: checked the service dashboard, found the webhook URL was pointing to localhost which is unreachable externally. Switched to ngrok for local testing but prod issue persists. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
    {
        "entry": (
            "Project: external API client. "
            "Issue: HTTP 429 Too Many Requests — the API rate limit was being hit during a bulk data sync. "
            "Solution attempted: added exponential backoff with tenacity and reduced the batch size to stay within rate limits. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: Python package. "
            "Issue: Poetry lock file conflict after merging two branches that both updated dependencies. "
            "Solution attempted: ran poetry lock --no-update to regenerate the lock file from the merged pyproject.toml without upgrading packages. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: Django app. "
            "Issue: Django static files not loading in production — CSS and JS returning 404. "
            "Solution attempted: ran collectstatic, configured STATIC_ROOT and the nginx location block to serve from the collected directory. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: Python script. "
            "Issue: datetime.utcnow() returning wrong timezone in production — timestamps were stored as UTC but displayed without conversion. "
            "Solution attempted: switched to datetime.now(timezone.utc) and stored timezone-aware datetimes throughout the codebase. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: containerised database. "
            "Issue: PostgreSQL container data not persisting between restarts — the database was empty after every docker compose down. "
            "Solution attempted: added a named volume for /var/lib/postgresql/data in docker-compose.yml. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: API gateway. "
            "Issue: Requests timing out under load — p99 latency spiking to 30s with only 50 concurrent users. "
            "Solution attempted: profiled with py-spy, found a blocking database call in an async route. Moved it to a thread pool with run_in_executor, latency improved but not resolved under full load. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
]


def main() -> None:
    total = len(INCIDENTS)
    saved = 0
    failed = 0

    print(f"Seeding {total} incidents through the Buster crew...\n")

    for i, incident in enumerate(INCIDENTS, 1):
        print(f"[{i}/{total}] Processing...", end=" ", flush=True)
        try:
            result = Buster().crew().kickoff(inputs={"entry": incident["entry"]})
            if result.pydantic is None:
                print("SKIPPED (model did not return structured output)")
                failed += 1
                continue
            data = result.pydantic.model_dump()
            data["resolved"] = incident["resolved"]
            bust_id = save_bust(data)
            print(f"Saved as Bust #{bust_id} — {data['title']}")
            saved += 1
        except Exception as e:
            print(f"ERROR — {e}")
            failed += 1

    print(f"\nDone. {saved} saved, {failed} skipped.")


if __name__ == "__main__":
    main()
