# Deploy & run (Docker + Railway)

This file explains how to build and test the Docker image locally and how to deploy to **Railway** using the repository's `Dockerfile` and `railway.toml`.

## Prerequisites
- Docker installed locally (for local testing)
- Git repo pushed to GitHub
- Railway account — sign up free at [railway.app](https://railway.app)

---

## Build & test locally

```bash
# from project root
docker build -t civitas:latest .

# run container
docker run --rm -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL="sqlite:///civitas.db" \
  civitas:latest
```

Run `seed.py` inside the container (local build):

```bash
docker run --rm -e DATABASE_URL="sqlite:///civitas.db" civitas:latest python seed.py
```

---

## Deploy to Railway

### 1. Create a project

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project → Deploy from GitHub Repo**.
3. Select this repository and the `main` branch.
4. Railway detects `railway.toml` + `Dockerfile` and starts building automatically.

### 2. Add a Postgres database

1. Inside the same Railway project, click **+ New → Database → PostgreSQL**.
2. Railway automatically injects `DATABASE_URL` into your web service — no manual copy-paste needed.

### 3. Set environment variables

Go to your web service → **Variables** tab and add:

| Key                   | Value                                       |
|-----------------------|---------------------------------------------|
| `SECRET_KEY`          | *(generate a strong random string)*         |
| `FLASK_ENV`           | `production`                                |
| `CHROME_NANO_ENABLED` | `True`                                     |
| `AI_FALLBACK_ENABLED` | `True`                                     |

> `DATABASE_URL` is set automatically by the Postgres plugin — you don't need to add it manually.

### 4. Seed the database

Once the first deploy succeeds:

1. Open your web service in the Railway dashboard.
2. Go to the **Settings** tab → click **Open Shell** (or use the Railway CLI: `railway run python seed.py`).
3. Run:

```bash
python seed.py
```

This populates the database with initial users and demo data.

### 5. Access the app

Railway gives you a public URL like `https://civitas-web-production-XXXX.up.railway.app`. Click **Settings → Networking → Generate Domain** if you don't see one.

---

## Railway CLI (optional, for power users)

```bash
# Install CLI
brew install railway    # macOS
# or: npm install -g @railway/cli

# Login and link
railway login
railway link            # select your project

# Deploy from local
railway up

# Run one-off commands
railway run python seed.py

# View logs
railway logs
```

---

## Notes
- **SQLite caveat**: For a quick demo you can set `DATABASE_URL=sqlite:///civitas.db`, but file-based SQLite is ephemeral on Railway and won't persist across deploys. Use the Postgres plugin for production.
- **Custom domain**: In Railway dashboard → service → Settings → Networking → Custom Domain.
- **Auto-deploy**: Every push to `main` triggers a new deploy automatically.
- **Scaling**: Upgrade to Railway Pro ($5/mo) for more resources, horizontal scaling, and persistent volumes.
