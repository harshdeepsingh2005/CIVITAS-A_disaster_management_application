# 🚀 Civitas - Deployment & Setup Guide

## 📋 Quick Start

### Prerequisites
- Python 3.11+ installed
- Chrome browser with Web Bluetooth support
- Bluetooth adapter (for BLE mesh functionality)

### 1-Minute Setup
```bash
# Clone and setup
git clone <repository-url>
cd civitas
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install and run
pip install -r requirements.txt
python seed.py
python app.py
```

**Access**: `http://localhost:5000`

---

## 🖥️ Development Environment Setup

### Windows Setup
```powershell
# 1. Install Python 3.11+
# Download from https://python.org

# 2. Verify installation
python --version
pip --version

# 3. Clone repository
git clone <repository-url>
cd civitas

# 4. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Initialize database
python seed.py

# 7. Run development server
python app.py
```

### macOS Setup
```bash
# 1. Install Python 3.11+ (using Homebrew)
brew install python@3.11

# 2. Clone repository
git clone <repository-url>
cd civitas

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python seed.py

# 6. Run development server
python app.py
```

### Linux (Ubuntu/Debian) Setup
```bash
# 1. Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# 2. Clone repository
git clone <repository-url>
cd civitas

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python seed.py

# 6. Run development server
python app.py
```

---

## 🌐 Production Deployment

### Option 1: Traditional Server Deployment

#### Ubuntu Server Setup
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-pip nginx

# 3. Create application user
sudo useradd -m -s /bin/bash civitas
sudo su - civitas

# 4. Clone and setup application
git clone <repository-url> /home/civitas/civitas
cd /home/civitas/civitas
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 6. Initialize database
python seed.py

# 7. Test application
python app.py
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/civitas
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/civitas/civitas/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Systemd Service
```ini
# /etc/systemd/system/civitas.service
[Unit]
Description=Civitas Disaster Management System
After=network.target

[Service]
User=civitas
Group=civitas
WorkingDirectory=/home/civitas/civitas
Environment=PATH=/home/civitas/civitas/venv/bin
ExecStart=/home/civitas/civitas/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 civitas && chown -R civitas:civitas /app
USER civitas

# Initialize database
RUN python seed.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  civitas:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
      - DATABASE_URL=postgresql://civitas:password@db:5432/civitas
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=civitas
      - POSTGRES_USER=civitas
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - civitas
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Deployment Commands
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f civitas

# Update application
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec db pg_dump -U civitas civitas > backup.sql
```

### Option 3: Cloud Deployment

#### Heroku Deployment
```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create civitas-disaster-mgmt

# 4. Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production

# 5. Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# 6. Deploy
git push heroku main

# 7. Initialize database
heroku run python seed.py
```

#### Procfile
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

#### AWS EC2 Deployment
```bash
# 1. Launch EC2 instance (Ubuntu 20.04 LTS)
# 2. Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip nginx

# 4. Clone and setup application
git clone <repository-url> /home/ubuntu/civitas
cd /home/ubuntu/civitas
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure and run
python seed.py
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Application Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/civitas
# or for SQLite: sqlite:///civitas.db

# Security Configuration
BCRYPT_LOG_ROUNDS=12
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# BLE Configuration
BLE_SERVICE_UUID=12345678-1234-1234-1234-123456789abc
BLE_CHARACTERISTIC_UUID=87654321-4321-4321-4321-cba987654321

# AI Configuration
CHROME_NANO_ENABLED=True
AI_FALLBACK_ENABLED=True
AI_CACHE_ENABLED=True

# PWA Configuration
PWA_ENABLED=True
OFFLINE_CACHE_SIZE=50MB
BACKGROUND_SYNC_ENABLED=True

# Monitoring
LOG_LEVEL=INFO
LOG_FILE=/var/log/civitas.log
```

### Database Configuration

#### SQLite (Development)
```python
# Default configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///civitas.db'
```

#### PostgreSQL (Production)
```python
# Production configuration
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/civitas'
```

#### Database Migration
```bash
# Create migration
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or use our custom seed script
python seed.py
```

---

## 🔍 Testing & Validation

### Pre-Deployment Testing
```bash
# 1. Run all tests
python test_db.py
python test_login.py
python test_ai_ble.py
python connect_mesh.py

# 2. Check application health
curl http://localhost:5000/health

# 3. Test BLE functionality
# Open Chrome and navigate to /ble-mesh
# Test device discovery and broadcasting

# 4. Test PWA functionality
# Install app and test offline capabilities
```

### Performance Testing
```bash
# Install testing tools
pip install locust

# Run load test
locust -f load_test.py --host=http://localhost:5000
```

### Security Testing
```bash
# Install security scanner
pip install bandit

# Run security scan
bandit -r . -f json -o security-report.json
```

---

## 📊 Monitoring & Maintenance

### Logging Setup
```python
# logging.conf
[loggers]
keys=root,civitas

[handlers]
keys=fileHandler,consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_civitas]
level=INFO
handlers=fileHandler,consoleHandler
qualname=civitas
propagate=0

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/civitas.log',)

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Health Monitoring
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "$(date): Civitas is down!" | mail -s "Civitas Alert" admin@example.com
        systemctl restart civitas
    fi
    sleep 60
done
EOF

chmod +x monitor.sh
nohup ./monitor.sh &
```

### Backup Strategy
```bash
# Database backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/civitas"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump civitas > $BACKUP_DIR/civitas_$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/civitas_app_$DATE.tar.gz /home/civitas/civitas

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

# Schedule backup (daily at 2 AM)
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# or on Windows
netstat -ano | findstr :5000

# Kill process
kill -9 <PID>
# or on Windows
taskkill /PID <PID> /F
```

#### 2. Database Connection Issues
```bash
# Check database status
systemctl status postgresql

# Restart database
sudo systemctl restart postgresql

# Check connection
psql -h localhost -U civitas -d civitas
```

#### 3. BLE Not Working
```bash
# Check Bluetooth status
systemctl status bluetooth

# Enable Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Check Bluetooth devices
bluetoothctl list
```

#### 4. PWA Not Installing
- Ensure HTTPS is enabled
- Check manifest.json validity
- Verify service worker registration
- Check browser console for errors

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=1
export FLASK_ENV=development
python app.py
```

### Log Analysis
```bash
# View application logs
tail -f logs/civitas.log

# Search for errors
grep -i error logs/civitas.log

# Monitor real-time logs
journalctl -u civitas -f
```

---

## 🔄 Updates & Maintenance

### Application Updates
```bash
# 1. Backup current version
cp -r /home/civitas/civitas /home/civitas/civitas.backup

# 2. Pull latest changes
cd /home/civitas/civitas
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations (if any)
python seed.py

# 5. Restart application
sudo systemctl restart civitas

# 6. Verify deployment
curl http://localhost:5000/health
```

### Dependency Updates
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages
pip install --upgrade -r requirements.txt
```

### Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip install safety
safety check
```

---

## 📞 Support & Resources

### Getting Help
- **Documentation**: Check PROJECT_DOCUMENTATION.md
- **Technical Specs**: See TECHNICAL_SPECIFICATION.md
- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub Discussions

### Useful Commands
```bash
# Check application status
systemctl status civitas

# View logs
journalctl -u civitas -f

# Restart application
sudo systemctl restart civitas

# Check database
psql -h localhost -U civitas -d civitas

# Test BLE connection
python connect_mesh.py

# Run all tests
python test_*.py
```

### Emergency Procedures
```bash
# Quick restart
sudo systemctl restart civitas nginx

# Database recovery
sudo systemctl restart postgresql
python seed.py

# Full system restart
sudo reboot
```

---

**🎉 Your Civitas deployment is ready!**

For additional support, refer to the main documentation or create an issue in the repository.
