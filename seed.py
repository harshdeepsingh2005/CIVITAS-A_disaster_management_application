from app import app, db
from models import User, Report, Alert, Mission, Safehouse, Resource, Team
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create sample users
        users = [
            User(
                email='citizen@civitas.com',
                name='John Citizen',
                role='citizen',
                password_hash=generate_password_hash('password123')
            ),
            User(
                email='rescuer@civitas.com',
                name='Sarah Rescuer',
                role='rescuer',
                password_hash=generate_password_hash('password123')
            ),
            User(
                email='government@civitas.com',
                name='Mike Official',
                role='government',
                password_hash=generate_password_hash('password123')
            )
        ]
        
        for user in users:
            if not User.query.filter_by(email=user.email).first():
                db.session.add(user)
        
        db.session.commit()
        
        # Get user IDs
        citizen = User.query.filter_by(email='citizen@civitas.com').first()
        rescuer = User.query.filter_by(email='rescuer@civitas.com').first()
        government = User.query.filter_by(email='government@civitas.com').first()
        
        # Create sample reports
        reports = [
            Report(
                title='Flooding in Downtown Area',
                description='Heavy rainfall has caused severe flooding in the downtown area. Water levels are rising rapidly and several buildings are at risk.',
                location='Downtown District',
                severity='high',
                user_id=citizen.id,
                status='pending',
                ai_summary='Severe flooding in downtown due to heavy rainfall. Rising water levels threatening buildings.'
            ),
            Report(
                title='Power Outage in Residential Zone',
                description='Complete power outage affecting 500+ households in the residential zone. No estimated restoration time available.',
                location='Residential Zone A',
                severity='medium',
                user_id=citizen.id,
                status='verified',
                ai_summary='Power outage affecting 500+ households with no restoration timeline.'
            )
        ]
        
        for report in reports:
            if not Report.query.filter_by(title=report.title).first():
                db.session.add(report)
        
        # Create sample alerts
        alerts = [
            Alert(
                title='Evacuation Order - Zone 1',
                message='Immediate evacuation required for all residents in Zone 1 due to rising floodwaters. Please proceed to designated safehouses immediately.',
                alert_type='evacuation',
                severity='critical',
                created_by=government.id,
                rewritten_message='URGENT: Zone 1 evacuation mandatory. Rising floodwaters require immediate relocation to safehouses.'
            ),
            Alert(
                title='Weather Update',
                message='Heavy rainfall expected to continue for the next 6 hours. Stay indoors and avoid unnecessary travel.',
                alert_type='weather',
                severity='medium',
                created_by=government.id,
                rewritten_message='Heavy rainfall continues for 6 hours. Remain indoors, avoid travel.'
            )
        ]
        
        for alert in alerts:
            if not Alert.query.filter_by(title=alert.title).first():
                db.session.add(alert)
        
        # Create sample missions
        missions = [
            Mission(
                title='Rescue Operation - Downtown',
                description='Deploy rescue team to downtown area to evacuate stranded residents from flooded buildings.',
                location='Downtown District',
                priority='critical',
                assigned_to=rescuer.id,
                created_by=government.id,
                status='active',
                ai_strategy='Prioritize high-rise buildings first, use boats for ground-level rescues, coordinate with emergency services.'
            ),
            Mission(
                title='Resource Distribution - Zone 2',
                description='Distribute emergency supplies including food, water, and medical kits to residents in Zone 2.',
                location='Zone 2',
                priority='high',
                assigned_to=rescuer.id,
                created_by=government.id,
                status='active',
                ai_strategy='Establish distribution points at community centers, prioritize vulnerable populations, maintain supply chain.'
            )
        ]
        
        for mission in missions:
            if not Mission.query.filter_by(title=mission.title).first():
                db.session.add(mission)
        
        # Create sample safehouses
        safehouses = [
            Safehouse(
                name='Central Community Center',
                location='123 Main Street',
                capacity=200,
                current_occupancy=45,
                facilities='Food, Water, Medical Aid, Restrooms',
                contact_info='555-0123',
                status='operational'
            ),
            Safehouse(
                name='High School Gymnasium',
                location='456 Education Ave',
                capacity=300,
                current_occupancy=120,
                facilities='Food, Water, Sleeping Areas, First Aid',
                contact_info='555-0456',
                status='operational'
            )
        ]
        
        for safehouse in safehouses:
            if not Safehouse.query.filter_by(name=safehouse.name).first():
                db.session.add(safehouse)
        
        # Create sample resources
        resources = [
            Resource(
                name='Emergency Food Rations',
                category='food',
                quantity=500,
                location='Central Warehouse',
                status='available'
            ),
            Resource(
                name='Bottled Water',
                category='water',
                quantity=1000,
                location='Central Warehouse',
                status='available'
            ),
            Resource(
                name='Medical Kits',
                category='medical',
                quantity=50,
                location='Medical Center',
                status='available'
            ),
            Resource(
                name='Emergency Blankets',
                category='shelter',
                quantity=200,
                location='Central Warehouse',
                status='available'
            )
        ]
        
        for resource in resources:
            if not Resource.query.filter_by(name=resource.name).first():
                db.session.add(resource)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()

