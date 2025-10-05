# 🛡️ Civitas - Disaster Management System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![Chrome Nano AI](https://img.shields.io/badge/Chrome%20Nano%20AI-Integrated-orange.svg)](https://developer.chrome.com)
[![BLE Mesh](https://img.shields.io/badge/BLE%20Mesh-Enabled-purple.svg)](https://web.dev/bluetooth)
[![PWA](https://img.shields.io/badge/PWA-Ready-red.svg)](https://web.dev/progressive-web-apps)

**An offline-first disaster management system combining Chrome Nano AI APIs with BLE mesh communication for emergency response scenarios.**

## 🎯 Overview

Civitas is a comprehensive disaster management platform that enables real-time communication and coordination between citizens, rescuers, and government agencies even when traditional networks fail. Built for the **Google Chrome Built-in AI Challenge 2025**, it showcases the power of Chrome Nano AI APIs and Web Bluetooth technology.

### 🌟 Key Features

- 🚨 **Real-time Emergency Alerts** with AI enhancement
- 📡 **BLE Mesh Communication** for offline connectivity  
- 🤖 **Chrome Nano AI Integration** (Summarizer, Proofreader, Rewriter, Translator, Prompt Generator)
- 📱 **Progressive Web App** with full offline capabilities
- 🔐 **Role-based Access Control** (Citizen, Rescuer, Government)
- 📊 **Analytics Dashboard** for disaster response monitoring
- 🏠 **Safehouse Management** and resource distribution
- 🔒 **End-to-end Encryption** for secure communications

## 🚀 Quick Start

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

### Default Login Credentials
- **Citizen**: `citizen@civitas.com` / `password123`
- **Rescuer**: `rescuer@civitas.com` / `password123`  
- **Government**: `government@civitas.com` / `password123`

## 🏗️ Architecture

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

## 📚 Documentation

- **[📖 Complete Project Documentation](PROJECT_DOCUMENTATION.md)** - Comprehensive guide covering all aspects
- **[🔧 Technical Specification](TECHNICAL_SPECIFICATION.md)** - Detailed technical implementation
- **[🚀 Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[📡 BLE Mesh Guide](BLE_MESH_GUIDE.md)** - BLE mesh connection and usage

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 1.4.23** - Database ORM
- **Flask-Login 0.6.3** - User authentication
- **bcrypt 4.1.2** - Password hashing
- **Gunicorn 21.2.0** - Production server

### Frontend
- **HTML5/CSS3/JavaScript (ES6+)** - Modern web technologies
- **Service Workers** - Offline functionality
- **IndexedDB** - Client-side storage
- **Web Bluetooth API** - BLE communication
- **Chrome Nano AI APIs** - AI integration

### Database
- **SQLite** - Development database
- **PostgreSQL** - Production ready

## 🔌 API Endpoints

### Core APIs
```http
GET    /api/reports              # List incident reports
POST   /api/reports              # Create new report
GET    /api/alerts               # List emergency alerts
POST   /api/alerts               # Create new alert
GET    /api/missions             # List missions
POST   /api/missions             # Create new mission
GET    /api/resources            # List resources
POST   /api/resources            # Create new resource
GET    /api/safehouses           # List safehouses
POST   /api/safehouses           # Create new safehouse
```

### Chrome Nano AI APIs
```http
POST   /api/ai/summarize         # AI text summarization
POST   /api/ai/proofread         # AI text proofreading
POST   /api/ai/rewrite           # AI text rewriting
POST   /api/ai/translate         # AI text translation
POST   /api/ai/generate-prompt   # AI strategy generation
```

### BLE Mesh APIs
```http
GET    /api/ble/status           # BLE network status
POST   /api/ble/discover         # Discover nearby devices
POST   /api/ble/broadcast        # Broadcast message via BLE
POST   /api/ble/sync             # Sync offline data
```

## 🤖 Chrome Nano AI Integration

### Supported APIs
- **Summarizer**: Generate concise summaries of incident reports
- **Proofreader**: Clean and format text for better readability
- **Rewriter**: Rewrite text for clarity and impact
- **Translator**: Translate emergency messages to multiple languages
- **Prompt Generator**: Generate strategic prompts for emergency response

### Implementation
```javascript
// Real Chrome Nano API calls
const summary = await chrome.nano.summarizer.summarize(text, {
    maxLength: 100,
    style: 'concise'
});

// Fallback when APIs unavailable
const fallbackSummary = text.substring(0, 100) + '...';
```

## 📡 BLE Mesh Communication

### Protocol Details
- **Service UUID**: `12345678-1234-1234-1234-123456789abc`
- **Characteristic UUID**: `87654321-4321-4321-4321-cba987654321`
- **Device Naming**: `Civitas-{Role}-{ID}`
- **Encryption**: AES-256 for all communications
- **Message Types**: Alert, Mission, Status, Sync, Discovery

### Connection Guide
1. Enable Web Bluetooth in Chrome: `chrome://flags/#enable-experimental-web-platform-features`
2. Navigate to `/ble-mesh` page
3. Click "Connect to Mesh"
4. Allow Bluetooth permissions
5. Select Civitas device from list

## 📱 Progressive Web App Features

- **Offline Support**: Full functionality without internet
- **Installable**: Install on any device
- **Push Notifications**: Emergency alert notifications
- **Background Sync**: Automatic data synchronization
- **Responsive Design**: Works on all screen sizes
- **App-like Experience**: Native app feel in browser

## 🧪 Testing

### Test Scripts
```bash
# Test database functionality
python test_db.py

# Test authentication system
python test_login.py

# Test AI and BLE features
python test_ai_ble.py

# Test BLE mesh connection
python connect_mesh.py
```

### Browser Compatibility
| Browser | Version | Web Bluetooth | Chrome Nano AI | PWA Support |
|---------|---------|---------------|----------------|-------------|
| Chrome  | 88+     | ✅            | ✅             | ✅           |
| Edge    | 88+     | ✅            | ❌             | ✅           |
| Firefox | 89+     | ❌            | ❌             | ✅           |
| Safari  | 14+     | ❌            | ❌             | ✅           |

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **Role-based Access**: Citizen, Rescuer, Government roles
- **Encrypted Communications**: AES-256 for BLE
- **CSRF Protection**: Flask-WTF tokens
- **Secure Sessions**: HTTP-only cookies
- **Input Validation**: Server-side validation

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker-compose up -d

# Using Heroku
git push heroku main
```

See [Deployment Guide](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📊 Project Structure

```
civitas/
├── 📄 app.py                    # Main Flask application
├── 📄 models.py                 # Database models
├── 📄 extensions.py             # Flask extensions
├── 📄 seed.py                   # Database seeding
├── 📄 requirements.txt          # Python dependencies
├── 📁 static/                   # Static assets
│   ├── 📄 app.js               # Main JavaScript
│   ├── 📄 style.css            # Application styles
│   ├── 📄 sw.js                # Service worker
│   └── 📄 manifest.json        # PWA manifest
├── 📁 templates/                # HTML templates
│   ├── 📄 base.html            # Base template
│   ├── 📄 login.html           # Login page
│   ├── 📄 dashboard.html       # Main dashboard
│   ├── 📄 ble_mesh.html        # BLE mesh interface
│   └── 📄 ...                  # Other pages
├── 📄 test_*.py                # Test scripts
├── 📄 connect_mesh.py          # BLE connection test
├── 📄 PROJECT_DOCUMENTATION.md # Complete documentation
├── 📄 TECHNICAL_SPECIFICATION.md # Technical details
├── 📄 DEPLOYMENT_GUIDE.md      # Deployment instructions
├── 📄 BLE_MESH_GUIDE.md        # BLE mesh guide
└── 📄 README.md                # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Add new feature"`
5. Push to branch: `git push origin feature/new-feature`
6. Create Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ES6+ for JavaScript
- Test all new features
- Update documentation
- Maintain backward compatibility

## 📞 Support

### Getting Help
- **Documentation**: Check the comprehensive guides above
- **Issues**: Create GitHub issue with detailed description
- **Discussions**: Use GitHub Discussions for questions

### Useful Commands
```bash
# Check application status
curl http://localhost:5000/health

# View logs
tail -f logs/civitas.log

# Test BLE connection
python connect_mesh.py

# Run all tests
python test_*.py
```

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Acknowledgments

- **Google Chrome Team** for Chrome Nano AI APIs
- **Web Bluetooth Community** for BLE mesh protocols
- **Flask Community** for the excellent web framework
- **Open Source Contributors** for various libraries used

---

**🎉 Built for the Google Chrome Built-in AI Challenge 2025**

*Civitas - Empowering communities through intelligent disaster management*