# 🛡️ Civitas - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Architecture](#architecture)
5. [API Documentation](#api-documentation)
6. [Database Schema](#database-schema)
7. [Chrome Nano AI Integration](#chrome-nano-ai-integration)
8. [BLE Mesh Communication](#ble-mesh-communication)
9. [PWA Features](#pwa-features)
10. [Deployment Guide](#deployment-guide)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)

---

## 🎯 Project Overview

**Civitas** is an offline-first disaster management system that combines Chrome Nano AI APIs with BLE mesh communication for emergency response scenarios. The system enables real-time communication and coordination between citizens, rescuers, and government agencies even when traditional networks fail.

### Key Features
- 🚨 **Real-time Emergency Alerts** with AI enhancement
- 📡 **BLE Mesh Communication** for offline connectivity
- 🤖 **Chrome Nano AI Integration** for intelligent processing
- 📱 **Progressive Web App** with offline capabilities
- 🔐 **Role-based Access Control** (Citizen, Rescuer, Government)
- 📊 **Analytics Dashboard** for disaster response monitoring
- 🏠 **Safehouse Management** and resource distribution

---

## 💻 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Browser**: Chrome 88+ with Web Bluetooth support

### Recommended Requirements
- **Python**: 3.11+ (tested with 3.11.0)
- **RAM**: 8GB or higher
- **Storage**: 5GB free space
- **Browser**: Chrome 120+ with experimental features enabled

### Hardware Requirements
- **Bluetooth**: BLE 4.0+ compatible adapter
- **Network**: Internet connection for initial setup (offline operation supported)

---

## 🚀 Installation Guide

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd civitas
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python seed.py
```

### Step 5: Run the Application
```bash
python app.py
```

### Step 6: Access the Application
Open your browser and navigate to: `http://localhost:5000`

---

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (PWA)         │◄──►│   (Flask)       │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • REST APIs     │    │ • User Data     │
│ • Service Worker│    │ • AI Integration│    │ • Reports       │
│ • IndexedDB     │    │ • BLE APIs      │    │ • Alerts        │
│ • Web Bluetooth │    │ • Authentication│    │ • Missions      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Chrome Nano AI  │    │ BLE Mesh        │    │ Offline Storage │
│ APIs            │    │ Communication   │    │ & Sync          │
│                 │    │                 │    │                 │
│ • Summarizer    │    │ • Device        │    │ • IndexedDB     │
│ • Proofreader   │    │   Discovery     │    │ • Service       │
│ • Rewriter      │    │ • Message       │    │   Worker        │
│ • Translator    │    │   Broadcasting  │    │ • Background    │
│ • Prompt Gen    │    │ • Encryption    │    │   Sync          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Backend**: Flask 3.0.0, SQLAlchemy 1.4.23, Flask-Login 0.6.3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Service Workers
- **Database**: SQLite (development), PostgreSQL (production ready)
- **AI Integration**: Chrome Nano APIs (Summarizer, Proofreader, Rewriter, Translator, Prompt Generator)
- **Communication**: Web Bluetooth API, BLE Mesh Protocol
- **Security**: bcrypt, JWT tokens, AES-256 encryption

---

## 📚 API Documentation

### Authentication Endpoints

#### POST /login
Authenticate user and create session.
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST /logout
Terminate user session.

### Core API Endpoints

#### GET /api/reports
Retrieve all incident reports.
**Response:**
```json
[
  {
    "id": 1,
    "title": "Flood Report",
    "description": "Water level rising in downtown area",
    "location": "Downtown",
    "severity": "high",
    "status": "active",
    "created_at": "2025-01-05T10:30:00Z"
  }
]
```

#### POST /api/reports
Create new incident report.
```json
{
  "title": "Fire Emergency",
  "description": "Building fire on Main Street",
  "location": "Main Street",
  "severity": "critical",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

#### GET /api/alerts
Retrieve all emergency alerts.

#### POST /api/alerts
Create new emergency alert.
```json
{
  "title": "Evacuation Notice",
  "message": "Immediate evacuation required",
  "priority": "critical",
  "target_roles": ["citizen", "rescuer"]
}
```

#### GET /api/missions
Retrieve all active missions.

#### POST /api/missions
Create new mission assignment.
```json
{
  "title": "Rescue Operation",
  "description": "Rescue trapped individuals",
  "location": "Building A",
  "assigned_to": 2,
  "priority": "high"
}
```

### Chrome Nano AI API Endpoints

#### POST /api/ai/summarize
Generate AI summary of text.
```json
{
  "text": "Long incident report text...",
  "max_length": 100,
  "style": "concise"
}
```

#### POST /api/ai/proofread
AI-powered text proofreading.
```json
{
  "text": "Text to proofread",
  "language": "en",
  "style": "formal"
}
```

#### POST /api/ai/rewrite
AI text rewriting for clarity.
```json
{
  "text": "Original text",
  "tone": "professional",
  "style": "clear",
  "audience": "general"
}
```

#### POST /api/ai/translate
AI-powered text translation.
```json
{
  "text": "Text to translate",
  "target_language": "es",
  "source_language": "en"
}
```

#### POST /api/ai/generate-prompt
Generate AI strategy prompts.
```json
{
  "context": "Emergency evacuation",
  "type": "strategy",
  "role": "rescuer"
}
```

### BLE Mesh API Endpoints

#### GET /api/ble/status
Get BLE mesh network status.
**Response:**
```json
{
  "ble_available": true,
  "mesh_nodes": 3,
  "network_health": "good",
  "connected_devices": [
    {
      "id": "civitas-rescuer-001",
      "role": "rescuer",
      "distance": "5m",
      "signal": -45
    }
  ]
}
```

#### POST /api/ble/discover
Discover nearby BLE devices.
**Response:**
```json
{
  "devices_found": 3,
  "devices": [
    {
      "name": "Civitas-Rescuer-001",
      "role": "rescuer",
      "distance": "5m",
      "signal": -45,
      "connected": true
    }
  ]
}
```

#### POST /api/ble/broadcast
Broadcast message via BLE mesh.
```json
{
  "type": "alert",
  "message": "Emergency evacuation required",
  "priority": "high"
}
```

#### POST /api/ble/sync
Sync offline data via BLE.
```json
{
  "data": {...},
  "timestamp": 1234567890,
  "device_id": "civitas-citizen-001"
}
```

---

## 🗄️ Database Schema

### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # citizen, rescuer, government
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Report Model
```python
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, resolved, false_alarm
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Alert Model
```python
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rewritten_message = db.Column(db.Text)  # AI-enhanced version
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    target_roles = db.Column(db.Text)  # JSON array of target roles
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Mission Model
```python
class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Resource Model
```python
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # food, water, medical, shelter, equipment
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='available')  # available, allocated, depleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Safehouse Model
```python
class Safehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    facilities = db.Column(db.Text)  # JSON array of available facilities
    status = db.Column(db.String(20), default='open')  # open, full, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🤖 Chrome Nano AI Integration

### Supported APIs

#### 1. Summarizer API
- **Purpose**: Generate concise summaries of incident reports and alerts
- **Usage**: Automatic summarization of long text content
- **Parameters**:
  - `text`: Input text to summarize
  - `max_length`: Maximum length of summary (default: 100)
  - `style`: Summary style - "concise", "detailed", "bullet_points"

#### 2. Proofreader API
- **Purpose**: Clean and format text for better readability
- **Usage**: Automatic proofreading of user-generated content
- **Parameters**:
  - `text`: Text to proofread
  - `language`: Target language (default: "en")
  - `style`: Writing style - "formal", "casual", "technical"

#### 3. Rewriter API
- **Purpose**: Rewrite text for clarity and impact
- **Usage**: Enhance emergency communications for better understanding
- **Parameters**:
  - `text`: Original text
  - `tone`: Desired tone - "urgent", "calm", "professional"
  - `style`: Writing style - "clear", "concise", "detailed"
  - `audience`: Target audience - "general", "technical", "citizens"

#### 4. Translator API
- **Purpose**: Translate emergency messages to multiple languages
- **Usage**: Ensure accessibility for diverse populations
- **Parameters**:
  - `text`: Text to translate
  - `target_language`: Target language code (e.g., "es", "fr", "zh")
  - `source_language`: Source language code (default: "en")

#### 5. Prompt Generator API
- **Purpose**: Generate strategic prompts for emergency response
- **Usage**: Create context-aware strategies for different scenarios
- **Parameters**:
  - `context`: Emergency context (e.g., "earthquake", "flood", "fire")
  - `type`: Prompt type - "strategy", "checklist", "communication"
  - `role`: User role - "citizen", "rescuer", "government"

### Implementation Details
- **Frontend Integration**: Direct calls to `window.chrome.nano` APIs
- **Fallback System**: Enhanced simulation when Chrome Nano APIs unavailable
- **Error Handling**: Graceful degradation with user feedback
- **Caching**: Results cached for performance optimization

---

## 📡 BLE Mesh Communication

### Protocol Specification

#### Service UUID
```
12345678-1234-1234-1234-123456789abc
```

#### Characteristic UUID
```
87654321-4321-4321-4321-cba987654321
```

#### Message Format
```json
{
  "type": "alert|mission|status|sync",
  "data": {...},
  "timestamp": 1234567890,
  "sender": "device-id",
  "priority": "low|medium|high|critical",
  "encrypted": true
}
```

### Device Naming Convention
- **Citizen Devices**: `Civitas-Citizen-{ID}`
- **Rescuer Devices**: `Civitas-Rescuer-{ID}`
- **Government Devices**: `Civitas-Government-{ID}`

### Security Features
- **AES-256 Encryption**: All BLE communications encrypted
- **Device Authentication**: Role-based access control
- **Message Integrity**: Checksum verification
- **Proximity Restrictions**: Geographic limitations

### Mesh Network Features
- **Auto-Discovery**: Automatic device detection
- **Signal Strength Monitoring**: Real-time connection quality
- **Distance Calculation**: Approximate device positioning
- **Network Health Assessment**: Connection stability monitoring

---

## 📱 PWA Features

### Service Worker
- **Offline Caching**: Cache critical resources for offline use
- **Background Sync**: Sync data when connection restored
- **Push Notifications**: Emergency alert notifications
- **Update Management**: Automatic app updates

### Manifest Configuration
```json
{
  "name": "Civitas - Disaster Management",
  "short_name": "Civitas",
  "description": "Offline-First Disaster Management System",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#0a0a0a",
  "background_color": "#000000",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

### Offline Capabilities
- **Data Storage**: IndexedDB for local data persistence
- **Offline Forms**: Create reports and alerts without internet
- **Background Sync**: Automatic data synchronization
- **Conflict Resolution**: Handle data conflicts intelligently

---

## 🚀 Deployment Guide

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python seed.py

# Run development server
python app.py
```

### Production Deployment

#### Using Gunicorn
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python seed.py

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Environment Variables
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/civitas"
export FLASK_ENV="production"
```

### Cloud Deployment Options
- **Heroku**: Easy deployment with Procfile
- **AWS**: EC2 with RDS for database
- **Google Cloud**: App Engine with Cloud SQL
- **Azure**: App Service with Azure Database

---

## 🧪 Testing

### Test Files
- `test_db.py`: Database connection and CRUD operations
- `test_login.py`: Authentication system testing
- `test_ai_ble.py`: AI and BLE functionality testing
- `connect_mesh.py`: BLE mesh connection testing

### Running Tests
```bash
# Test database functionality
python test_db.py

# Test login system
python test_login.py

# Test AI and BLE features
python test_ai_ble.py

# Test BLE mesh connection
python connect_mesh.py
```

### Test Coverage
- ✅ Database operations
- ✅ User authentication
- ✅ API endpoints
- ✅ Chrome Nano AI integration
- ✅ BLE mesh communication
- ✅ PWA functionality
- ✅ Offline capabilities

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
**Problem**: `sqlite3.OperationalError: database is locked`
**Solution**: 
```bash
# Check for running processes
ps aux | grep python
# Kill existing processes
kill -9 <process_id>
# Restart application
python app.py
```

#### 2. BLE Connection Issues
**Problem**: "Web Bluetooth not supported"
**Solution**:
- Enable experimental web platform features in Chrome
- Ensure Bluetooth is enabled on device
- Check browser permissions

#### 3. Chrome Nano API Errors
**Problem**: "Chrome Nano APIs not available"
**Solution**:
- Use Chrome browser with Nano API support
- Check for API availability: `window.chrome.nano`
- Fallback to enhanced simulation mode

#### 4. PWA Installation Issues
**Problem**: "Install prompt not showing"
**Solution**:
- Ensure HTTPS connection (or localhost)
- Check manifest.json validity
- Verify service worker registration

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=1
python app.py
```

### Log Files
- **Application Logs**: Console output
- **Error Logs**: Flask error handling
- **BLE Logs**: Web Bluetooth API responses
- **AI Logs**: Chrome Nano API calls

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Add new feature"`
5. Push to branch: `git push origin feature/new-feature`
6. Create Pull Request

### Code Standards
- **Python**: PEP 8 style guide
- **JavaScript**: ES6+ with JSDoc comments
- **CSS**: BEM methodology
- **HTML**: Semantic markup

### Testing Requirements
- All new features must include tests
- Maintain test coverage above 80%
- Test both online and offline scenarios
- Verify BLE functionality on real devices

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

### Getting Help
- **Documentation**: Check this file and README.md
- **Issues**: Create GitHub issue with detailed description
- **Discussions**: Use GitHub Discussions for questions

### Contact Information
- **Project Lead**: [Your Name]
- **Email**: [your-email@example.com]
- **GitHub**: [your-github-username]

---

## 🎯 Roadmap

### Version 2.0 (Planned)
- [ ] Real-time video streaming via BLE
- [ ] Advanced AI analytics
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Integration with emergency services

### Version 3.0 (Future)
- [ ] IoT device integration
- [ ] Machine learning predictions
- [ ] Blockchain-based verification
- [ ] Satellite communication backup
- [ ] Global deployment support

---

**🎉 Thank you for using Civitas!**

This documentation is maintained and updated regularly. For the latest information, always refer to the official repository.
