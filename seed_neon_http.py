"""
seed_neon_http.py — Seeds the Neon PostgreSQL database via the Neon Serverless HTTP API.
Run this when port 5432 is blocked and psycopg2 can't connect directly.

Usage:
    python seed_neon_http.py
"""
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# ── Config ─────────────────────────────────────────────────────────────────
# Load from .env manually (safe even without python-dotenv installed)
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if not DATABASE_URL or 'neon.tech' not in DATABASE_URL:
    raise SystemExit("❌ DATABASE_URL must point to a Neon database. Check your .env file.")

# Parse the Neon connection string to extract the project/host info
# Format: postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
import urllib.parse as urlparse
parsed = urlparse.urlparse(DATABASE_URL)
neon_host = parsed.hostname          # e.g. ep-wispy-hill-ajl2csp3.c-3.us-east-2.aws.neon.tech
neon_db   = parsed.path.lstrip('/')  # e.g. neondb
neon_user = parsed.username
neon_pass = parsed.password

# Neon serverless HTTP endpoint
NEON_HTTP_URL = f"https://{neon_host}/sql"

def neon_query(sql: str, params: list = None):
    """Execute SQL via Neon's HTTP API (works over port 443)."""
    payload = json.dumps({
        "query": sql,
        "params": params or []
    }).encode()

    req = urllib.request.Request(
        NEON_HTTP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Neon-Connection-String": DATABASE_URL,
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}")

def run_sql(sql: str, params: list = None):
    """Run a single SQL statement, print errors but continue."""
    try:
        result = neon_query(sql, params)
        return result
    except Exception as e:
        print(f"  ⚠️  SQL error (non-fatal): {e}")
        return None

# ── Create Tables ──────────────────────────────────────────────────────────
print("🔧 Creating tables...")

run_sql("""
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS report (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(200) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_summary TEXT,
    ai_priority_score FLOAT
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS alert (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    alert_type VARCHAR(50) DEFAULT 'general',
    severity VARCHAR(20) DEFAULT 'medium',
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    rewritten_message TEXT,
    translated_messages JSONB
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS mission (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(200) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'active',
    assigned_to INTEGER REFERENCES "user"(id),
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    ai_strategy TEXT,
    ai_estimated_duration INTEGER
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS resource (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    location VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_demand_prediction FLOAT,
    ai_optimal_distribution TEXT
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS distribution (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER REFERENCES resource(id) NOT NULL,
    recipient_id INTEGER REFERENCES "user"(id) NOT NULL,
    quantity INTEGER NOT NULL,
    location VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    distributed_by INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    distributed_at TIMESTAMP WITH TIME ZONE,
    ai_priority_score FLOAT,
    ai_optimal_route TEXT
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS safehouse (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    capacity INTEGER NOT NULL,
    current_occupancy INTEGER DEFAULT 0,
    facilities TEXT,
    contact_info VARCHAR(200),
    status VARCHAR(20) DEFAULT 'operational',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_occupancy_prediction FLOAT,
    ai_optimal_evacuation_route TEXT
)
""")

run_sql("""
CREATE TABLE IF NOT EXISTS team (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    team_type VARCHAR(50) NOT NULL,
    leader_id INTEGER REFERENCES "user"(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_team_efficiency FLOAT,
    ai_optimal_assignments TEXT
)
""")

print("✅ Tables created")

# ── Seed Users ─────────────────────────────────────────────────────────────
print("🌱 Seeding users...")

users = [
    ('citizen@civitas.com',    'John Citizen',  'citizen',    generate_password_hash('password123')),
    ('rescuer@civitas.com',    'Sarah Rescuer', 'rescuer',    generate_password_hash('password123')),
    ('government@civitas.com', 'Mike Official', 'government', generate_password_hash('password123')),
]
for email, name, role, pw_hash in users:
    run_sql(
        'INSERT INTO "user" (email, name, role, password_hash) VALUES ($1,$2,$3,$4) ON CONFLICT (email) DO NOTHING',
        [email, name, role, pw_hash]
    )

# Fetch IDs
citizen_row    = neon_query('SELECT id FROM "user" WHERE email=$1', ['citizen@civitas.com'])
rescuer_row    = neon_query('SELECT id FROM "user" WHERE email=$1', ['rescuer@civitas.com'])
government_row = neon_query('SELECT id FROM "user" WHERE email=$1', ['government@civitas.com'])

citizen_id    = citizen_row['rows'][0]['id']
rescuer_id    = rescuer_row['rows'][0]['id']
government_id = government_row['rows'][0]['id']
print(f"  citizen={citizen_id}, rescuer={rescuer_id}, government={government_id}")

# ── Seed Reports ───────────────────────────────────────────────────────────
print("🌱 Seeding reports...")
run_sql(
    "INSERT INTO report (title, description, location, severity, user_id, status, ai_summary) VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING",
    ['Flooding in Downtown Area',
     'Heavy rainfall has caused severe flooding in the downtown area. Water levels are rising rapidly and several buildings are at risk.',
     'Downtown District', 'high', citizen_id, 'pending',
     'Severe flooding in downtown due to heavy rainfall. Rising water levels threatening buildings.']
)
run_sql(
    "INSERT INTO report (title, description, location, severity, user_id, status, ai_summary) VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING",
    ['Power Outage in Residential Zone',
     'Complete power outage affecting 500+ households in the residential zone. No estimated restoration time available.',
     'Residential Zone A', 'medium', citizen_id, 'verified',
     'Power outage affecting 500+ households with no restoration timeline.']
)

# ── Seed Alerts ────────────────────────────────────────────────────────────
print("🌱 Seeding alerts...")
run_sql(
    "INSERT INTO alert (title, message, alert_type, severity, created_by, rewritten_message) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING",
    ['Evacuation Order - Zone 1',
     'Immediate evacuation required for all residents in Zone 1 due to rising floodwaters.',
     'evacuation', 'critical', government_id,
     'URGENT: Zone 1 evacuation mandatory. Rising floodwaters require immediate relocation to safehouses.']
)
run_sql(
    "INSERT INTO alert (title, message, alert_type, severity, created_by, rewritten_message) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING",
    ['Weather Update',
     'Heavy rainfall expected to continue for the next 6 hours. Stay indoors and avoid unnecessary travel.',
     'weather', 'medium', government_id,
     'Heavy rainfall continues for 6 hours. Remain indoors, avoid travel.']
)

# ── Seed Missions ──────────────────────────────────────────────────────────
print("🌱 Seeding missions...")
run_sql(
    "INSERT INTO mission (title, description, location, priority, assigned_to, created_by, status, ai_strategy) VALUES ($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING",
    ['Rescue Operation - Downtown',
     'Deploy rescue team to downtown area to evacuate stranded residents from flooded buildings.',
     'Downtown District', 'critical', rescuer_id, government_id, 'active',
     'Prioritize high-rise buildings first, use boats for ground-level rescues, coordinate with emergency services.']
)

# ── Seed Safehouses ────────────────────────────────────────────────────────
print("🌱 Seeding safehouses...")
run_sql(
    "INSERT INTO safehouse (name, location, capacity, current_occupancy, facilities, contact_info, status) VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING",
    ['Central Community Center', '123 Main Street', 200, 45,
     'Food, Water, Medical Aid, Restrooms', '555-0123', 'operational']
)
run_sql(
    "INSERT INTO safehouse (name, location, capacity, current_occupancy, facilities, contact_info, status) VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING",
    ['High School Gymnasium', '456 Education Ave', 300, 120,
     'Food, Water, Sleeping Areas, First Aid', '555-0456', 'operational']
)

# ── Seed Resources ─────────────────────────────────────────────────────────
print("🌱 Seeding resources...")
for rname, cat, qty, loc in [
    ('Emergency Food Rations', 'food',    500,  'Central Warehouse'),
    ('Bottled Water',          'water',   1000, 'Central Warehouse'),
    ('Medical Kits',           'medical', 50,   'Medical Center'),
    ('Emergency Blankets',     'shelter', 200,  'Central Warehouse'),
]:
    run_sql(
        "INSERT INTO resource (name, category, quantity, location, status) VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING",
        [rname, cat, qty, loc, 'available']
    )

print("\n🎉 Database seeded successfully on Neon!")
print("\nDemo credentials:")
print("  citizen@civitas.com    / password123")
print("  rescuer@civitas.com    / password123")
print("  government@civitas.com / password123")
