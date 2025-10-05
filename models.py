from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # citizen, rescuer, government
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reports = db.relationship('Report', backref='user', lazy=True)
    created_alerts = db.relationship('Alert', backref='creator', lazy=True)
    created_missions = db.relationship('Mission', foreign_keys='Mission.created_by', backref='creator', lazy=True)
    assigned_missions = db.relationship('Mission', foreign_keys='Mission.assigned_to', backref='assignee', lazy=True)
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='pending')  # pending, verified, resolved
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI-generated fields
    ai_summary = db.Column(db.Text)
    ai_priority_score = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Report {self.title}>'

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), default='general')  # weather, evacuation, safety, general
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # AI-enhanced fields
    rewritten_message = db.Column(db.Text)
    translated_messages = db.Column(db.JSON)  # Store translations in different languages
    
    def __repr__(self):
        return f'<Alert {self.title}>'

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # AI-generated fields
    ai_strategy = db.Column(db.Text)
    ai_estimated_duration = db.Column(db.Integer)  # in minutes
    
    def __repr__(self):
        return f'<Mission {self.title}>'

class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, distributed, cancelled
    distributed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    distributed_at = db.Column(db.DateTime)
    
    # AI-optimized fields
    ai_priority_score = db.Column(db.Float)
    ai_optimal_route = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Distribution {self.id}>'

class Safehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    facilities = db.Column(db.Text)  # JSON string of available facilities
    contact_info = db.Column(db.String(200))
    status = db.Column(db.String(20), default='operational')  # operational, full, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI-optimized fields
    ai_occupancy_prediction = db.Column(db.Float)
    ai_optimal_evacuation_route = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Safehouse {self.name}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # food, water, medical, shelter, transport
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='available')  # available, allocated, depleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI-optimized fields
    ai_demand_prediction = db.Column(db.Float)
    ai_optimal_distribution = db.Column(db.Text)
    
    # Relationships
    distributions = db.relationship('Distribution', backref='resource', lazy=True)
    
    def __repr__(self):
        return f'<Resource {self.name}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    team_type = db.Column(db.String(50), nullable=False)  # rescue, medical, logistics, communication
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, standby, deployed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI-optimized fields
    ai_team_efficiency = db.Column(db.Float)
    ai_optimal_assignments = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Team {self.name}>'
