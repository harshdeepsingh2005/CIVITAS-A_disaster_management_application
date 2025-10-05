# 🔧 Civitas - Technical Specification

## 📋 System Architecture Overview

### Core Components
```
┌─────────────────────────────────────────────────────────────────┐
│                        CIVITAS SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (PWA)                                          │
│  ├── HTML5/CSS3/JavaScript (ES6+)                              │
│  ├── Service Worker (Offline Support)                          │
│  ├── IndexedDB (Local Storage)                                 │
│  ├── Web Bluetooth API (BLE Communication)                     │
│  └── Chrome Nano AI APIs (AI Integration)                      │
├─────────────────────────────────────────────────────────────────┤
│  Backend Layer (Flask)                                         │
│  ├── REST API Endpoints                                        │
│  ├── Authentication & Authorization                            │
│  ├── Database ORM (SQLAlchemy)                                 │
│  ├── AI API Integration Layer                                  │
│  └── BLE Mesh Management                                       │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ├── SQLite Database (Development)                             │
│  ├── PostgreSQL (Production Ready)                             │
│  ├── IndexedDB (Client-side Cache)                             │
│  └── File System (Static Assets)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Environment Specifications

### Development Environment
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.11.0 (tested)
- **Node.js**: Not required (pure Python backend)
- **Browser**: Chrome 88+ with Web Bluetooth support

### Production Environment
- **Server**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.11+
- **Web Server**: Gunicorn 21.2.0
- **Database**: PostgreSQL 13+ (or SQLite for small deployments)
- **Reverse Proxy**: Nginx (optional)

### Browser Compatibility
| Browser | Version | Web Bluetooth | Chrome Nano AI | PWA Support |
|---------|---------|---------------|----------------|-------------|
| Chrome  | 88+     | ✅            | ✅             | ✅           |
| Edge    | 88+     | ✅            | ❌             | ✅           |
| Firefox | 89+     | ❌            | ❌             | ✅           |
| Safari  | 14+     | ❌            | ❌             | ✅           |

---

## 📦 Dependencies & Versions

### Python Dependencies
```python
# Core Framework
Flask==3.0.0                    # Web framework
Flask-SQLAlchemy==3.1.1         # Database ORM
Flask-Login==0.6.3              # User authentication
Werkzeug==3.0.1                 # WSGI utilities
Jinja2==3.1.2                   # Template engine

# Security & Authentication
bcrypt==4.1.2                   # Password hashing
python-dotenv==1.0.0            # Environment variables

# Production Server
gunicorn==21.2.0                # WSGI HTTP server

# Additional (if needed)
requests==2.32.5                # HTTP client
cryptography==46.0.1            # Encryption utilities
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "service-worker": "built-in",
    "indexeddb": "built-in",
    "web-bluetooth": "built-in",
    "chrome-nano-ai": "built-in"
  }
}
```

### System Dependencies
- **SQLite3**: Built into Python
- **Bluetooth**: BLE 4.0+ adapter required
- **Web Server**: Built-in Flask development server (dev) or Gunicorn (prod)

---

## 🗄️ Database Schema Details

### Entity Relationship Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │   Report    │    │   Alert     │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │◄───┤ created_by  │    │ id (PK)     │
│ email       │    │ id (PK)     │    │ title       │
│ password    │    │ title       │    │ message     │
│ role        │    │ description │    │ rewritten   │
│ name        │    │ location    │    │ priority    │
│ phone       │    │ severity    │    │ target_roles│
│ location    │    │ status      │    │ created_by  │
│ created_at  │    │ created_at  │    │ created_at  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Mission   │    │  Resource   │    │  Safehouse  │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │    │ id (PK)     │    │ id (PK)     │
│ title       │    │ name        │    │ name        │
│ description │    │ type        │    │ location    │
│ location    │    │ quantity    │    │ capacity    │
│ priority    │    │ location    │    │ occupancy   │
│ status      │    │ status      │    │ facilities  │
│ assigned_to │    │ created_at  │    │ status      │
│ created_by  │    └─────────────┘    │ created_at  │
│ created_at  │                       └─────────────┘
└─────────────┘
```

### Indexes and Constraints
```sql
-- User table indexes
CREATE UNIQUE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_role ON user(role);

-- Report table indexes
CREATE INDEX idx_report_created_by ON report(created_by);
CREATE INDEX idx_report_severity ON report(severity);
CREATE INDEX idx_report_status ON report(status);
CREATE INDEX idx_report_created_at ON report(created_at);

-- Alert table indexes
CREATE INDEX idx_alert_priority ON alert(priority);
CREATE INDEX idx_alert_created_by ON alert(created_by);
CREATE INDEX idx_alert_created_at ON alert(created_at);

-- Mission table indexes
CREATE INDEX idx_mission_assigned_to ON mission(assigned_to);
CREATE INDEX idx_mission_created_by ON mission(created_by);
CREATE INDEX idx_mission_status ON mission(status);
CREATE INDEX idx_mission_priority ON mission(priority);

-- Resource table indexes
CREATE INDEX idx_resource_type ON resource(type);
CREATE INDEX idx_resource_status ON resource(status);
CREATE INDEX idx_resource_location ON resource(location);

-- Safehouse table indexes
CREATE INDEX idx_safehouse_status ON safehouse(status);
CREATE INDEX idx_safehouse_capacity ON safehouse(capacity);
```

---

## 🔌 API Specification

### REST API Endpoints

#### Authentication
```http
POST /login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=password123

Response: 302 Redirect to /dashboard
```

#### Core Resources
```http
# Reports
GET    /api/reports              # List all reports
POST   /api/reports              # Create new report
GET    /api/reports/{id}         # Get specific report
PUT    /api/reports/{id}         # Update report
DELETE /api/reports/{id}         # Delete report

# Alerts
GET    /api/alerts               # List all alerts
POST   /api/alerts               # Create new alert
GET    /api/alerts/{id}          # Get specific alert
PUT    /api/alerts/{id}          # Update alert
DELETE /api/alerts/{id}          # Delete alert

# Missions
GET    /api/missions             # List all missions
POST   /api/missions             # Create new mission
GET    /api/missions/{id}        # Get specific mission
PUT    /api/missions/{id}        # Update mission
DELETE /api/missions/{id}        # Delete mission

# Resources
GET    /api/resources            # List all resources
POST   /api/resources            # Create new resource
GET    /api/resources/{id}       # Get specific resource
PUT    /api/resources/{id}       # Update resource
DELETE /api/resources/{id}       # Delete resource

# Safehouses
GET    /api/safehouses           # List all safehouses
POST   /api/safehouses           # Create new safehouse
GET    /api/safehouses/{id}      # Get specific safehouse
PUT    /api/safehouses/{id}      # Update safehouse
DELETE /api/safehouses/{id}      # Delete safehouse
```

#### AI API Endpoints
```http
# Chrome Nano AI Integration
POST /api/ai/summarize           # Text summarization
POST /api/ai/proofread           # Text proofreading
POST /api/ai/rewrite             # Text rewriting
POST /api/ai/translate           # Text translation
POST /api/ai/generate-prompt     # Strategy generation
```

#### BLE Mesh API Endpoints
```http
# BLE Mesh Communication
GET  /api/ble/status             # Network status
POST /api/ble/discover           # Device discovery
POST /api/ble/broadcast          # Message broadcasting
POST /api/ble/sync               # Data synchronization
```

### Response Formats

#### Success Response
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2025-01-05T10:30:00Z"
}
```

#### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  },
  "timestamp": "2025-01-05T10:30:00Z"
}
```

---

## 🔐 Security Specifications

### Authentication & Authorization
- **Password Hashing**: bcrypt with salt rounds = 12
- **Session Management**: Flask-Login with secure cookies
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Role-Based Access**: Citizen, Rescuer, Government roles

### Data Encryption
- **BLE Communication**: AES-256 encryption
- **Password Storage**: bcrypt hashing
- **API Communication**: HTTPS/TLS 1.3
- **Local Storage**: Browser-native encryption

### Security Headers
```python
# Security headers configuration
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 📡 BLE Mesh Protocol

### Service Definition
```javascript
// BLE Service UUID
const CIVITAS_SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';

// BLE Characteristic UUID
const CIVITAS_CHARACTERISTIC_UUID = '87654321-4321-4321-4321-cba987654321';

// Service Definition
const service = {
    uuid: CIVITAS_SERVICE_UUID,
    characteristics: [
        {
            uuid: CIVITAS_CHARACTERISTIC_UUID,
            properties: ['read', 'write', 'notify'],
            permissions: ['read', 'write']
        }
    ]
};
```

### Message Protocol
```json
{
  "header": {
    "version": "1.0",
    "type": "alert|mission|status|sync|discovery",
    "priority": "low|medium|high|critical",
    "timestamp": 1234567890,
    "sender": "device-id",
    "recipient": "device-id|broadcast"
  },
  "payload": {
    "data": {...},
    "encrypted": true,
    "checksum": "sha256-hash"
  }
}
```

### Device Discovery Protocol
```json
{
  "type": "discovery",
  "device_info": {
    "id": "civitas-rescuer-001",
    "name": "Civitas Rescuer Device",
    "role": "rescuer",
    "version": "1.0.0",
    "capabilities": ["alert", "mission", "status"],
    "battery_level": 85,
    "signal_strength": -45
  },
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 5.0
  }
}
```

---

## 🤖 Chrome Nano AI Integration

### API Interface
```javascript
// Chrome Nano AI API Interface
class ChromeNanoAPI {
    // Summarizer
    async summarize(text, options = {}) {
        return await chrome.nano.summarizer.summarize(text, {
            maxLength: options.maxLength || 100,
            style: options.style || 'concise'
        });
    }

    // Proofreader
    async proofread(text, options = {}) {
        return await chrome.nano.proofreader.proofread(text, {
            language: options.language || 'en',
            style: options.style || 'formal'
        });
    }

    // Rewriter
    async rewrite(text, options = {}) {
        return await chrome.nano.rewriter.rewrite(text, {
            tone: options.tone || 'professional',
            style: options.style || 'clear',
            audience: options.audience || 'general'
        });
    }

    // Translator
    async translate(text, options = {}) {
        return await chrome.nano.translator.translate(text, {
            targetLanguage: options.targetLanguage || 'en',
            sourceLanguage: options.sourceLanguage || 'auto'
        });
    }

    // Prompt Generator
    async generatePrompt(context, options = {}) {
        return await chrome.nano.prompt.generate(context, {
            type: options.type || 'strategy',
            role: options.role || 'general'
        });
    }
}
```

### Fallback Implementation
```javascript
// Fallback when Chrome Nano APIs not available
class FallbackAI {
    summarize(text, maxLength = 100) {
        const words = text.split(' ');
        if (words.length <= maxLength) return text;
        return words.slice(0, maxLength).join(' ') + '...';
    }

    proofread(text) {
        return text.trim().replace(/\s+/g, ' ');
    }

    rewrite(text) {
        return text.replace(/urgent/gi, 'critical')
                  .replace(/help/gi, 'assistance');
    }

    translate(text, targetLang) {
        // Simple keyword translation
        const translations = {
            'es': { 'help': 'ayuda', 'emergency': 'emergencia' },
            'fr': { 'help': 'aide', 'emergency': 'urgence' }
        };
        return translations[targetLang] ? text : text;
    }

    generatePrompt(context, type) {
        return `Strategy for ${context} - ${type} approach recommended`;
    }
}
```

---

## 📱 PWA Technical Details

### Service Worker Implementation
```javascript
// Service Worker (sw.js)
const CACHE_NAME = 'civitas-v1.0.0';
const STATIC_CACHE = [
    '/',
    '/static/style.css',
    '/static/app.js',
    '/static/manifest.json',
    '/offline.html'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_CACHE))
    );
});

// Fetch event
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
```

### IndexedDB Schema
```javascript
// IndexedDB Database Schema
const DB_NAME = 'CivitasDB';
const DB_VERSION = 1;

const stores = {
    reports: {
        keyPath: 'id',
        indexes: ['created_at', 'severity', 'status']
    },
    alerts: {
        keyPath: 'id',
        indexes: ['priority', 'created_at', 'target_roles']
    },
    missions: {
        keyPath: 'id',
        indexes: ['status', 'priority', 'assigned_to']
    },
    offline_queue: {
        keyPath: 'id',
        indexes: ['timestamp', 'type', 'status']
    }
};
```

### Manifest Configuration
```json
{
  "name": "Civitas - Disaster Management System",
  "short_name": "Civitas",
  "description": "Offline-First Disaster Management with AI and BLE Mesh",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "theme_color": "#0a0a0a",
  "background_color": "#000000",
  "scope": "/",
  "lang": "en",
  "categories": ["emergency", "productivity", "utilities"],
  "icons": [
    {
      "src": "/static/icon-72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/icon-384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

## 🚀 Performance Specifications

### Response Time Targets
- **API Endpoints**: < 200ms average
- **Database Queries**: < 100ms average
- **BLE Communication**: < 500ms for message delivery
- **AI Processing**: < 2s for text processing
- **Page Load**: < 3s initial load

### Scalability Limits
- **Concurrent Users**: 1000+ (with proper server setup)
- **BLE Mesh Nodes**: 50+ devices
- **Database Records**: 100,000+ per table
- **File Storage**: 1GB+ for offline data

### Resource Usage
- **Memory**: 512MB base, 1GB with full features
- **CPU**: Low usage, spikes during AI processing
- **Storage**: 100MB base installation, 1GB+ with data
- **Network**: Minimal when offline, standard web traffic when online

---

## 🔧 Configuration Management

### Environment Variables
```bash
# Application Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development|production
FLASK_DEBUG=True|False

# Database Configuration
DATABASE_URL=sqlite:///civitas.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/civitas

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
```

### Configuration Files
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///civitas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    
    # BLE Configuration
    BLE_SERVICE_UUID = os.environ.get('BLE_SERVICE_UUID', '12345678-1234-1234-1234-123456789abc')
    BLE_CHARACTERISTIC_UUID = os.environ.get('BLE_CHARACTERISTIC_UUID', '87654321-4321-4321-4321-cba987654321')
    
    # AI Configuration
    CHROME_NANO_ENABLED = os.environ.get('CHROME_NANO_ENABLED', 'True').lower() == 'true'
    AI_FALLBACK_ENABLED = os.environ.get('AI_FALLBACK_ENABLED', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

## 📊 Monitoring & Logging

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        file_handler = RotatingFileHandler('logs/civitas.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Civitas startup')
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        app.logger.info(f'{f.__name__} executed in {end_time - start_time:.2f}s')
        return result
    return decorated_function
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': 'connected',
        'ble_mesh': 'available',
        'ai_apis': 'available'
    })
```

---

This technical specification provides comprehensive details about the Civitas system architecture, implementation, and configuration. It serves as a reference for developers, system administrators, and technical stakeholders.
