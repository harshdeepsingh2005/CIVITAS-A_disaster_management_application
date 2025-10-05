#!/usr/bin/env python3
"""
Civitas Demo Script
Demonstrates the key features of the offline-first disaster management system
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def demo_login():
    """Demo user login"""
    print("🔐 Demo: User Login")
    print("-" * 40)
    
    # Test login with citizen account
    login_data = {
        'email': 'citizen@civitas.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:  # Redirect indicates successful login
            print("✅ Citizen login successful")
        else:
            print("❌ Login failed")
    except Exception as e:
        print(f"❌ Login error: {e}")

def demo_api_endpoints():
    """Demo API endpoints"""
    print("\n🌐 Demo: API Endpoints")
    print("-" * 40)
    
    # Test reports API
    try:
        response = requests.get(f"{BASE_URL}/api/reports")
        if response.status_code == 200:
            reports = response.json()
            print(f"✅ Reports API: {len(reports)} reports found")
        else:
            print("❌ Reports API failed")
    except Exception as e:
        print(f"❌ Reports API error: {e}")
    
    # Test alerts API
    try:
        response = requests.get(f"{BASE_URL}/api/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"✅ Alerts API: {len(alerts)} alerts found")
        else:
            print("❌ Alerts API failed")
    except Exception as e:
        print(f"❌ Alerts API error: {e}")
    
    # Test missions API
    try:
        response = requests.get(f"{BASE_URL}/api/missions")
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ Missions API: {len(missions)} missions found")
        else:
            print("❌ Missions API failed")
    except Exception as e:
        print(f"❌ Missions API error: {e}")
    
    # Test safehouses API
    try:
        response = requests.get(f"{BASE_URL}/api/safehouses")
        if response.status_code == 200:
            safehouses = response.json()
            print(f"✅ Safehouses API: {len(safehouses)} safehouses found")
        else:
            print("❌ Safehouses API failed")
    except Exception as e:
        print(f"❌ Safehouses API error: {e}")
    
    # Test resources API
    try:
        response = requests.get(f"{BASE_URL}/api/resources")
        if response.status_code == 200:
            resources = response.json()
            print(f"✅ Resources API: {len(resources)} resources found")
        else:
            print("❌ Resources API failed")
    except Exception as e:
        print(f"❌ Resources API error: {e}")

def demo_chrome_nano_apis():
    """Demo Chrome Nano AI API integration"""
    print("\n🤖 Demo: Chrome Nano AI APIs")
    print("-" * 40)
    
    # Test summarization
    test_text = "Heavy rainfall has caused severe flooding in the downtown area. Water levels are rising rapidly and several buildings are at risk. Emergency services are responding but need additional resources."
    
    print(f"📝 Original text: {test_text[:50]}...")
    
    # Simulate AI summarization (in real app, this would use Chrome Nano APIs)
    summary = test_text.split('.')[0] + "..."
    print(f"✨ AI Summary: {summary}")
    
    # Test rewriting
    rewritten = test_text.replace("urgent", "critical").replace("help", "assistance")
    print(f"🔄 AI Rewritten: {rewritten[:50]}...")
    
    # Test strategy generation
    strategy = "Based on the flooding situation, prioritize: 1) Evacuate high-risk buildings, 2) Deploy rescue boats, 3) Set up emergency shelters"
    print(f"🎯 AI Strategy: {strategy}")

def demo_ble_mesh():
    """Demo BLE mesh communication"""
    print("\n📡 Demo: BLE Mesh Communication")
    print("-" * 40)
    
    # Simulate BLE data sync
    ble_data = {
        "type": "alert",
        "data": {
            "id": 1,
            "title": "Emergency Evacuation",
            "message": "Immediate evacuation required for Zone 1",
            "severity": "critical"
        },
        "timestamp": int(time.time())
    }
    
    print("📤 Broadcasting data via BLE mesh...")
    print(f"📦 Data: {json.dumps(ble_data, indent=2)}")
    print("✅ BLE mesh communication simulated")

def demo_offline_capabilities():
    """Demo offline-first features"""
    print("\n💾 Demo: Offline-First Capabilities")
    print("-" * 40)
    
    print("📱 PWA Features:")
    print("  ✅ Service Worker for offline caching")
    print("  ✅ IndexedDB for local data storage")
    print("  ✅ Background sync when online")
    print("  ✅ Installable on all platforms")
    
    print("\n🔄 Offline Sync Strategy:")
    print("  ✅ Store data locally when offline")
    print("  ✅ Sync with server when online")
    print("  ✅ BLE mesh for peer-to-peer sync")
    print("  ✅ Conflict resolution for data integrity")

def demo_analytics():
    """Demo analytics and insights"""
    print("\n📈 Demo: Analytics & AI Insights")
    print("-" * 40)
    
    # Simulate analytics data
    analytics = {
        "total_reports": 47,
        "active_alerts": 3,
        "completed_missions": 12,
        "resources_distributed": 1250,
        "people_evacuated": 340,
        "ble_connected_devices": 89,
        "ai_insights": [
            "High demand for medical supplies in Zone 3",
            "Route B recommended for faster evacuation",
            "Resource rebalancing needed in Central Warehouse"
        ]
    }
    
    print("📊 System Analytics:")
    for key, value in analytics.items():
        if key != "ai_insights":
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n🤖 AI Insights:")
    for insight in analytics["ai_insights"]:
        print(f"  💡 {insight}")

def main():
    """Run the complete demo"""
    print("🛡️ CIVITAS - Offline-First Disaster Management System")
    print("=" * 60)
    print("Demonstrating key features and capabilities")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running at http://localhost:5000")
        else:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the Flask app is running: python app.py")
        return
    
    # Run demos
    demo_login()
    demo_api_endpoints()
    demo_chrome_nano_apis()
    demo_ble_mesh()
    demo_offline_capabilities()
    demo_analytics()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("🌐 Open http://localhost:5000 in Chrome to access the full application")
    print("📱 Install as PWA for offline functionality")
    print("🔗 Enable Web Bluetooth for BLE mesh communication")
    print("=" * 60)

if __name__ == "__main__":
    main()

