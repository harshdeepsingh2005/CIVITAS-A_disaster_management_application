from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Report, Alert, Mission, Distribution, Safehouse, Resource, Team
from extensions import login_manager
import os
from datetime import datetime
import json

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///civitas.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

# Chrome Nano AI API Integration
class ChromeNanoAPI:
    @staticmethod
    async def summarize_text(text, max_length=100, style="concise"):
        """Generate summary using Chrome's built-in AI"""
        try:
            # Check if we're in a browser environment with Chrome Nano APIs
            if hasattr(app, 'chrome_nano_available') and app.chrome_nano_available:
                # This would be called from the frontend with real Chrome Nano APIs
                return await app.chrome_nano_available.summarizer.summarize(text, {
                    'maxLength': max_length,
                    'style': style
                })
            else:
                # Fallback implementation
                words = text.split()
                if len(words) <= max_length:
                    return text
                return ' '.join(words[:max_length]) + '...'
        except Exception as e:
            print(f"Chrome Nano Summarizer error: {e}")
            # Fallback
            words = text.split()
            if len(words) <= max_length:
                return text
            return ' '.join(words[:max_length]) + '...'
    
    @staticmethod
    async def proofread_text(text, language="en", style="formal"):
        """Clean and format text using Chrome's Proofreader API"""
        try:
            if hasattr(app, 'chrome_nano_available') and app.chrome_nano_available:
                return await app.chrome_nano_available.proofreader.proofread(text, {
                    'language': language,
                    'style': style
                })
            else:
                # Fallback implementation
                import re
                return re.sub(r'\s+', ' ', text.strip())
        except Exception as e:
            print(f"Chrome Nano Proofreader error: {e}")
            import re
            return re.sub(r'\s+', ' ', text.strip())
    
    @staticmethod
    async def rewrite_text(text, tone="professional", style="clear", audience="general"):
        """Rewrite text for clarity using Chrome's Rewriter API"""
        try:
            if hasattr(app, 'chrome_nano_available') and app.chrome_nano_available:
                return await app.chrome_nano_available.rewriter.rewrite(text, {
                    'tone': tone,
                    'style': style,
                    'targetAudience': audience
                })
            else:
                # Fallback implementation
                rewritten = text.replace("urgent", "critical").replace("help", "assistance")
                rewritten = rewritten.replace("problem", "situation").replace("bad", "concerning")
                return rewritten
        except Exception as e:
            print(f"Chrome Nano Rewriter error: {e}")
            return text.replace("urgent", "critical").replace("help", "assistance")
    
    @staticmethod
    async def translate_text(text, target_language="en", source_language="auto"):
        """Translate text using Chrome's Translator API"""
        try:
            if hasattr(app, 'chrome_nano_available') and app.chrome_nano_available:
                return await app.chrome_nano_available.translator.translate(text, {
                    'targetLanguage': target_language,
                    'sourceLanguage': source_language
                })
            else:
                # Fallback - return original text
                return text
        except Exception as e:
            print(f"Chrome Nano Translator error: {e}")
            return text
    
    @staticmethod
    async def generate_prompt(context, task_type="rescue", role="coordinator"):
        """Generate AI strategies using Chrome's Prompt API"""
        try:
            if hasattr(app, 'chrome_nano_available') and app.chrome_nano_available:
                return await app.chrome_nano_available.prompt.generate(context, {
                    'context': 'disaster_management',
                    'type': task_type,
                    'role': role
                })
            else:
                # Enhanced fallback implementation
                prompts = {
                    "rescue": f"Based on {context}, prioritize rescue operations by: 1) Assessing immediate danger levels, 2) Identifying accessible routes and safe zones, 3) Coordinating team resources and equipment, 4) Establishing communication protocols, 5) Implementing safety measures for responders",
                    "distribution": f"For {context}, optimize resource distribution by: 1) Calculating demand based on population density and needs, 2) Identifying bottlenecks in supply chains, 3) Ensuring equitable access across all affected areas, 4) Prioritizing vulnerable populations, 5) Establishing distribution checkpoints",
                    "evacuation": f"Regarding {context}, develop evacuation strategy: 1) Assess immediate threats and timeline, 2) Identify safe evacuation routes and assembly points, 3) Coordinate transportation resources, 4) Communicate with affected populations, 5) Ensure accessibility for all community members",
                    "communication": f"For {context}, establish communication protocols: 1) Set up emergency communication channels, 2) Coordinate with all response agencies, 3) Ensure multilingual support, 4) Implement redundancy for critical communications, 5) Train personnel on emergency procedures"
                }
                return prompts.get(task_type, f"Analyze {context} and provide comprehensive strategic recommendations for effective disaster response coordination.")
        except Exception as e:
            print(f"Chrome Nano Prompt Generator error: {e}")
            return f"Based on {context}, here's the recommended strategy: 1) Assess immediate risks, 2) Prioritize critical needs, 3) Coordinate resources effectively."

# Authentication routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'citizen')
        name = request.form.get('name')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('login.html')
        
        user = User(
            email=email,
            name=name,
            role=role,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', user=current_user)

@app.route('/alerts')
@login_required
def alerts():
    return render_template('alerts.html', user=current_user)

@app.route('/missions')
@login_required
def missions():
    return render_template('missions.html', user=current_user)

@app.route('/distribution')
@login_required
def distribution():
    return render_template('distribution.html', user=current_user)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html', user=current_user)

@app.route('/ble-mesh')
@login_required
def ble_mesh():
    return render_template('ble_mesh.html', user=current_user)

@app.route('/safehouses')
@login_required
def safehouses():
    return render_template('safehouses.html', user=current_user)

@app.route('/offline.html')
def offline():
    return render_template('offline.html')

# API Routes
@app.route('/api/reports', methods=['GET', 'POST'])
@login_required
def reports_api():
    if request.method == 'POST':
        data = request.get_json()
        report = Report(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            severity=data.get('severity', 'medium'),
            user_id=current_user.id,
            status='pending'
        )
        db.session.add(report)
        db.session.commit()
        
        # Generate AI summary
        summary = ChromeNanoAPI.summarize_text(report.description)
        report.ai_summary = summary
        db.session.commit()
        
        return jsonify({'id': report.id, 'ai_summary': summary})
    
    reports = Report.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'location': r.location,
        'severity': r.severity,
        'status': r.status,
        'ai_summary': r.ai_summary,
        'created_at': r.created_at.isoformat()
    } for r in reports])

@app.route('/api/alerts', methods=['GET', 'POST'])
@login_required
def alerts_api():
    if request.method == 'POST' and current_user.role in ['government', 'rescuer']:
        data = request.get_json()
        alert = Alert(
            title=data['title'],
            message=data['message'],
            alert_type=data.get('alert_type', 'general'),
            severity=data.get('severity', 'medium'),
            created_by=current_user.id
        )
        db.session.add(alert)
        db.session.commit()
        
        # Rewrite for clarity (using fallback for now)
        rewritten_message = alert.message.replace("urgent", "critical").replace("help", "assistance")
        alert.rewritten_message = rewritten_message
        db.session.commit()
        
        return jsonify({'id': alert.id, 'rewritten_message': rewritten_message})
    
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'message': a.message,
        'rewritten_message': a.rewritten_message,
        'alert_type': a.alert_type,
        'severity': a.severity,
        'created_at': a.created_at.isoformat()
    } for a in alerts])

@app.route('/api/missions', methods=['GET', 'POST'])
@login_required
def missions_api():
    if request.method == 'POST' and current_user.role in ['government', 'rescuer']:
        data = request.get_json()
        mission = Mission(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            priority=data.get('priority', 'medium'),
            assigned_to=data.get('assigned_to'),
            created_by=current_user.id,
            status='active'
        )
        db.session.add(mission)
        db.session.commit()
        
        # Generate AI strategy
        strategy = ChromeNanoAPI.generate_prompt(mission.description, 'rescue')
        mission.ai_strategy = strategy
        db.session.commit()
        
        return jsonify({'id': mission.id, 'ai_strategy': strategy})
    
    missions = Mission.query.filter_by(assigned_to=current_user.id).all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'location': m.location,
        'priority': m.priority,
        'status': m.status,
        'ai_strategy': m.ai_strategy,
        'created_at': m.created_at.isoformat()
    } for m in missions])

@app.route('/api/safehouses', methods=['GET', 'POST'])
@login_required
def safehouses_api():
    if request.method == 'POST' and current_user.role in ['government']:
        data = request.get_json()
        safehouse = Safehouse(
            name=data['name'],
            location=data['location'],
            capacity=data['capacity'],
            current_occupancy=data.get('current_occupancy', 0),
            facilities=data.get('facilities', ''),
            contact_info=data.get('contact_info', '')
        )
        db.session.add(safehouse)
        db.session.commit()
        return jsonify({'id': safehouse.id})
    
    safehouses = Safehouse.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'location': s.location,
        'capacity': s.capacity,
        'current_occupancy': s.current_occupancy,
        'facilities': s.facilities,
        'contact_info': s.contact_info,
        'availability': s.capacity - s.current_occupancy
    } for s in safehouses])

@app.route('/api/resources', methods=['GET', 'POST'])
@login_required
def resources_api():
    if request.method == 'POST' and current_user.role in ['government', 'rescuer']:
        data = request.get_json()
        resource = Resource(
            name=data['name'],
            category=data['category'],
            quantity=data['quantity'],
            location=data['location'],
            status=data.get('status', 'available')
        )
        db.session.add(resource)
        db.session.commit()
        return jsonify({'id': resource.id})
    
    resources = Resource.query.all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'category': r.category,
        'quantity': r.quantity,
        'location': r.location,
        'status': r.status
    } for r in resources])

# BLE Mesh API endpoints
@app.route('/api/ble/sync', methods=['POST'])
@login_required
def ble_sync():
    """Handle BLE mesh data synchronization"""
    data = request.get_json()
    sync_type = data.get('type')
    
    if sync_type == 'reports':
        # Sync reports via BLE
        reports = data.get('reports', [])
        for report_data in reports:
            if not Report.query.filter_by(id=report_data['id']).first():
                report = Report(
                    id=report_data['id'],
                    title=report_data['title'],
                    description=report_data['description'],
                    location=report_data['location'],
                    severity=report_data['severity'],
                    user_id=report_data['user_id'],
                    status=report_data['status']
                )
                db.session.add(report)
        db.session.commit()
    
    return jsonify({'status': 'synced'})

@app.route('/api/ble/broadcast', methods=['POST'])
@login_required
def ble_broadcast():
    """Broadcast data via BLE mesh"""
    data = request.get_json()
    broadcast_type = data.get('type')
    
    if broadcast_type == 'alert' and current_user.role in ['government']:
        alert = Alert.query.get(data.get('alert_id'))
        if alert:
            return jsonify({
                'type': 'alert',
                'data': {
                    'id': alert.id,
                    'title': alert.title,
                    'message': alert.rewritten_message or alert.message,
                    'severity': alert.severity,
                    'created_at': alert.created_at.isoformat()
                }
            })
    
    return jsonify({'status': 'broadcast_ready'})

# Chrome Nano AI API Endpoints
@app.route('/api/ai/summarize', methods=['POST'])
@login_required
def ai_summarize():
    """Generate AI summary using Chrome Nano API"""
    data = request.get_json()
    text = data.get('text', '')
    max_length = data.get('max_length', 100)
    style = data.get('style', 'concise')
    
    try:
        summary = ChromeNanoAPI.summarize_text(text, max_length, style)
        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_summary': text[:max_length] + '...' if len(text) > max_length else text
        })

@app.route('/api/ai/proofread', methods=['POST'])
@login_required
def ai_proofread():
    """Proofread text using Chrome Nano API"""
    data = request.get_json()
    text = data.get('text', '')
    language = data.get('language', 'en')
    style = data.get('style', 'formal')
    
    try:
        proofread_text = ChromeNanoAPI.proofread_text(text, language, style)
        return jsonify({
            'success': True,
            'proofread_text': proofread_text,
            'changes_made': text != proofread_text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_text': text.strip()
        })

@app.route('/api/ai/rewrite', methods=['POST'])
@login_required
def ai_rewrite():
    """Rewrite text using Chrome Nano API"""
    data = request.get_json()
    text = data.get('text', '')
    tone = data.get('tone', 'professional')
    style = data.get('style', 'clear')
    audience = data.get('audience', 'general')
    
    try:
        rewritten_text = ChromeNanoAPI.rewrite_text(text, tone, style, audience)
        return jsonify({
            'success': True,
            'rewritten_text': rewritten_text,
            'original_text': text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_text': text.replace("urgent", "critical").replace("help", "assistance")
        })

@app.route('/api/ai/translate', methods=['POST'])
@login_required
def ai_translate():
    """Translate text using Chrome Nano API"""
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')
    source_language = data.get('source_language', 'auto')
    
    try:
        translated_text = ChromeNanoAPI.translate_text(text, target_language, source_language)
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'original_text': text,
            'target_language': target_language
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_text': text
        })

@app.route('/api/ai/generate-prompt', methods=['POST'])
@login_required
def ai_generate_prompt():
    """Generate AI strategy prompt using Chrome Nano API"""
    data = request.get_json()
    context = data.get('context', '')
    task_type = data.get('task_type', 'rescue')
    role = data.get('role', 'coordinator')
    
    try:
        prompt = ChromeNanoAPI.generate_prompt(context, task_type, role)
        return jsonify({
            'success': True,
            'prompt': prompt,
            'context': context,
            'task_type': task_type,
            'role': role
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_prompt': f"Based on {context}, prioritize operations by assessing risks and coordinating resources."
        })

# BLE Mesh Management Endpoints
@app.route('/api/ble/status', methods=['GET'])
@login_required
def ble_status():
    """Get BLE mesh network status"""
    return jsonify({
        'ble_available': True,  # This would check actual BLE availability
        'mesh_nodes': 3,  # This would be dynamic
        'connected_devices': [
            {'id': 'civitas-rescuer-001', 'role': 'rescuer', 'signal': -45, 'distance': '5m'},
            {'id': 'civitas-government-002', 'role': 'government', 'signal': -67, 'distance': '12m'},
            {'id': 'civitas-citizen-003', 'role': 'citizen', 'signal': -52, 'distance': '8m'}
        ],
        'network_health': 'good',
        'last_sync': '2025-10-05T01:40:00Z'
    })

@app.route('/api/ble/discover', methods=['POST'])
@login_required
def ble_discover():
    """Discover nearby BLE devices"""
    try:
        # This would trigger actual BLE device discovery
        discovered_devices = [
            {'name': 'Civitas-Rescuer-001', 'distance': '5m', 'signal': -45, 'role': 'rescuer'},
            {'name': 'Civitas-Government-002', 'distance': '12m', 'signal': -67, 'role': 'government'},
            {'name': 'Civitas-Citizen-003', 'distance': '8m', 'signal': -52, 'role': 'citizen'}
        ]
        
        return jsonify({
            'success': True,
            'devices_found': len(discovered_devices),
            'devices': discovered_devices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
