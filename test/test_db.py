#!/usr/bin/env python3
"""
Database Connection Test Script
Tests if the database is connected and working properly
"""

from app import app, db
from models import User, Report, Alert, Mission, Safehouse, Resource

def test_database_connection():
    """Test database connection and data retrieval"""
    print("🔍 Testing Database Connection...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Test User table
            users = User.query.all()
            print(f"✅ Users table: {len(users)} records found")
            for user in users:
                print(f"   - {user.name} ({user.role}) - {user.email}")
            
            # Test Report table
            reports = Report.query.all()
            print(f"✅ Reports table: {len(reports)} records found")
            for report in reports:
                print(f"   - {report.title} - {report.severity} - {report.status}")
            
            # Test Alert table
            alerts = Alert.query.all()
            print(f"✅ Alerts table: {len(alerts)} records found")
            for alert in alerts:
                print(f"   - {alert.title} - {alert.severity} - {alert.alert_type}")
            
            # Test Mission table
            missions = Mission.query.all()
            print(f"✅ Missions table: {len(missions)} records found")
            for mission in missions:
                print(f"   - {mission.title} - {mission.priority} - {mission.status}")
            
            # Test Safehouse table
            safehouses = Safehouse.query.all()
            print(f"✅ Safehouses table: {len(safehouses)} records found")
            for safehouse in safehouses:
                print(f"   - {safehouse.name} - Capacity: {safehouse.capacity} - Occupancy: {safehouse.current_occupancy}")
            
            # Test Resource table
            resources = Resource.query.all()
            print(f"✅ Resources table: {len(resources)} records found")
            for resource in resources:
                print(f"   - {resource.name} - {resource.category} - Quantity: {resource.quantity}")
            
            print("\n🎉 Database connection successful!")
            print("📊 Summary:")
            print(f"   - Users: {len(users)}")
            print(f"   - Reports: {len(reports)}")
            print(f"   - Alerts: {len(alerts)}")
            print(f"   - Missions: {len(missions)}")
            print(f"   - Safehouses: {len(safehouses)}")
            print(f"   - Resources: {len(resources)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

def test_database_operations():
    """Test basic database operations"""
    print("\n🔧 Testing Database Operations...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Test creating a new record
            test_user = User(
                email='test@civitas.com',
                name='Test User',
                role='citizen',
                password_hash='test_hash'
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Create operation: Success")
            
            # Test reading the record
            found_user = User.query.filter_by(email='test@civitas.com').first()
            if found_user:
                print("✅ Read operation: Success")
                print(f"   - Found user: {found_user.name}")
            else:
                print("❌ Read operation: Failed")
            
            # Test updating the record
            if found_user:
                found_user.name = 'Updated Test User'
                db.session.commit()
                print("✅ Update operation: Success")
            
            # Test deleting the record
            if found_user:
                db.session.delete(found_user)
                db.session.commit()
                print("✅ Delete operation: Success")
            
            print("🎉 All database operations successful!")
            return True
            
        except Exception as e:
            print(f"❌ Database operations failed: {e}")
            return False

def main():
    """Run database tests"""
    print("🛡️ CIVITAS - Database Connection Test")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_database_connection()
    
    if connection_ok:
        # Test operations
        operations_ok = test_database_operations()
        
        if operations_ok:
            print("\n" + "=" * 60)
            print("✅ DATABASE IS FULLY FUNCTIONAL!")
            print("🌐 Ready to serve the Civitas application")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  Database connected but operations failed")
            print("🔧 Check database permissions and schema")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ DATABASE CONNECTION FAILED!")
        print("🔧 Check database file and permissions")
        print("💡 Try running: python seed.py")
        print("=" * 60)

if __name__ == "__main__":
    main()
