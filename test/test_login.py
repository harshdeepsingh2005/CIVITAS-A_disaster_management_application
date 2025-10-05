#!/usr/bin/env python3
"""
Login Test Script
Tests login functionality for all user roles
"""

import requests

def test_user_login(email, password, role):
    """Test login for a specific user"""
    print(f"🔐 Testing {role} login...")
    
    session = requests.Session()
    login_data = {'email': email, 'password': password}
    
    try:
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print(f"✅ {role} login successful (Status: {response.status_code})")
            
            # Test dashboard access
            dashboard_response = session.get('http://localhost:5000/dashboard')
            if dashboard_response.status_code == 200:
                print(f"✅ {role} dashboard access successful")
                
                # Test API access
                api_response = session.get('http://localhost:5000/api/reports')
                if api_response.status_code == 200:
                    reports = api_response.json()
                    print(f"✅ {role} API access successful ({len(reports)} reports)")
                else:
                    print(f"❌ {role} API access failed (Status: {api_response.status_code})")
            else:
                print(f"❌ {role} dashboard access failed (Status: {dashboard_response.status_code})")
        else:
            print(f"❌ {role} login failed (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ {role} login error: {e}")
    
    print()

def main():
    """Test all user logins"""
    print("🛡️ CIVITAS - Login Test")
    print("=" * 50)
    
    # Test users
    users = [
        ('citizen@civitas.com', 'password123', 'Citizen'),
        ('rescuer@civitas.com', 'password123', 'Rescuer'),
        ('government@civitas.com', 'password123', 'Government')
    ]
    
    for email, password, role in users:
        test_user_login(email, password, role)
    
    print("=" * 50)
    print("🎉 Login testing completed!")

if __name__ == "__main__":
    main()
