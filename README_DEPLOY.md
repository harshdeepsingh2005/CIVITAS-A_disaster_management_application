# Deploy & run (Docker + Render)

This file explains how to build and test the Docker image locally and how to deploy to Render using the repository's `Dockerfile` and `render.yaml`.

Prerequisites
- Docker installed locally
- Git repo pushed to GitHub (Render will need it)

Build locally

PowerShell:

```powershell
# from project root
docker build -t civitas:latest .

# run container (set DATABASE_URL if using external DB or sqlite)
docker run --rm -p 5000:5000 -e FLASK_ENV=production -e DATABASE_URL="sqlite:///civitas.db" civitas:latest
```

Run `seed.py` inside the container (local build)

```powershell
# create and run a temporary container to execute seed.py
docker run --rm -e DATABASE_URL="sqlite:///civitas.db" civitas:latest python seed.py
```

Deploy to Render

1. Push your repo to GitHub.
2. On Render, click New → Web Service.
3. Choose GitHub and select this repo and the `main` branch.
4. Render will detect `render.yaml` and the Dockerfile; it will build the Docker image using the `Dockerfile`.
5. In the Render dashboard for your Web Service set these environment variables (Render → service → Environment):
   - `SECRET_KEY` = (generate a secure value; don't commit it)
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = (use the *internal* Postgres connection string from Render Postgres instance)
   - `CHROME_NANO_ENABLED` = `True`
   - `AI_FALLBACK_ENABLED` = `True`

6. Provision a Postgres database from Render (New → PostgreSQL) and copy the *Internal Connection String* into `DATABASE_URL` in the Web Service env.

7. Deploy. After the service is live, open the service page and click "Open Shell" (or create a one-off job) and run:

```bash
python seed.py
```

This will run the seeder in the same environment as the app and populate the database with initial users/data.

Notes
- If the seeder expects an app context, it will run correctly from inside the container in Render Shell because the repo and env are the same as the running service.
- If you prefer a quick demo without Postgres, you can set `DATABASE_URL=sqlite:///civitas.db` but note that file-based SQLite won't be shared across multiple replicas and may be ephemeral on some hosts.
