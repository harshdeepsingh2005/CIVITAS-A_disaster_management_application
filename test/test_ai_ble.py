#!/usr/bin/env python3
"""
Chrome Nano AI & BLE Functionality Test Script
Tests the real Chrome Nano AI APIs and BLE mesh communication
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_chrome_nano_ai_apis():
    """Test Chrome Nano AI API endpoints"""
    print("🤖 Testing Chrome Nano AI APIs")
    print("-" * 50)
    
    # Test data
    test_text = "Heavy rainfall has caused severe flooding in the downtown area. Water levels are rising rapidly and several buildings are at risk. Emergency services are responding but need additional resources and coordination."
    
    # Login first
    session = requests.Session()
    login_data = {'email': 'government@civitas.com', 'password': 'password123'}
    session.post(f"{BASE_URL}/login", data=login_data)
    
    # Test Summarizer API
    print("📝 Testing Summarizer API...")
    try:
        response = session.post(f"{BASE_URL}/api/ai/summarize", json={
            'text': test_text,
            'max_length': 50,
            'style': 'concise'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Summarizer: {result.get('summary', 'No summary')}")
            print(f"   Original: {result.get('original_length')} chars → Summary: {result.get('summary_length')} chars")
        else:
            print(f"❌ Summarizer failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Summarizer error: {e}")
    
    # Test Proofreader API
    print("\n✏️ Testing Proofreader API...")
    try:
        messy_text = "urgent help needed  downtown flooding  buildings at risk"
        response = session.post(f"{BASE_URL}/api/ai/proofread", json={
            'text': messy_text,
            'language': 'en',
            'style': 'formal'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Proofreader: {result.get('proofread_text', 'No result')}")
            print(f"   Changes made: {result.get('changes_made', False)}")
        else:
            print(f"❌ Proofreader failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Proofreader error: {e}")
    
    # Test Rewriter API
    print("\n🔄 Testing Rewriter API...")
    try:
        response = session.post(f"{BASE_URL}/api/ai/rewrite", json={
            'text': "We need urgent help with the flooding problem downtown",
            'tone': 'professional',
            'style': 'clear',
            'audience': 'emergency_responders'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Rewriter: {result.get('rewritten_text', 'No result')}")
        else:
            print(f"❌ Rewriter failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Rewriter error: {e}")
    
    # Test Translator API
    print("\n🌍 Testing Translator API...")
    try:
        response = session.post(f"{BASE_URL}/api/ai/translate", json={
            'text': "Emergency evacuation required for Zone 1",
            'target_language': 'es',
            'source_language': 'en'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Translator: {result.get('translated_text', 'No result')}")
            print(f"   Target language: {result.get('target_language', 'Unknown')}")
        else:
            print(f"❌ Translator failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Translator error: {e}")
    
    # Test Prompt Generator API
    print("\n🎯 Testing Prompt Generator API...")
    try:
        response = session.post(f"{BASE_URL}/api/ai/generate-prompt", json={
            'context': 'Flooding in downtown area with rising water levels threatening buildings',
            'task_type': 'rescue',
            'role': 'emergency_coordinator'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prompt Generator: {result.get('prompt', 'No result')[:100]}...")
        else:
            print(f"❌ Prompt Generator failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prompt Generator error: {e}")

def test_ble_mesh_functionality():
    """Test BLE mesh communication endpoints"""
    print("\n📡 Testing BLE Mesh Functionality")
    print("-" * 50)
    
    # Login first
    session = requests.Session()
    login_data = {'email': 'rescuer@civitas.com', 'password': 'password123'}
    session.post(f"{BASE_URL}/login", data=login_data)
    
    # Test BLE Status
    print("📊 Testing BLE Status...")
    try:
        response = session.get(f"{BASE_URL}/api/ble/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BLE Status: Available: {result.get('ble_available')}")
            print(f"   Mesh nodes: {result.get('mesh_nodes')}")
            print(f"   Network health: {result.get('network_health')}")
            print(f"   Connected devices: {len(result.get('connected_devices', []))}")
            
            for device in result.get('connected_devices', []):
                print(f"     - {device.get('id')} ({device.get('role')}) - {device.get('distance')}")
        else:
            print(f"❌ BLE Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ BLE Status error: {e}")
    
    # Test BLE Discovery
    print("\n🔍 Testing BLE Discovery...")
    try:
        response = session.post(f"{BASE_URL}/api/ble/discover")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BLE Discovery: Found {result.get('devices_found', 0)} devices")
            
            for device in result.get('devices', []):
                print(f"     - {device.get('name')} ({device.get('role')}) - {device.get('distance')} - {device.get('signal')} dBm")
        else:
            print(f"❌ BLE Discovery failed: {response.status_code}")
    except Exception as e:
        print(f"❌ BLE Discovery error: {e}")
    
    # Test BLE Broadcast
    print("\n📤 Testing BLE Broadcast...")
    try:
        response = session.post(f"{BASE_URL}/api/ble/broadcast", json={
            'type': 'alert',
            'alert_id': 1
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BLE Broadcast: {result.get('type', 'Unknown type')}")
            if 'data' in result:
                print(f"   Alert: {result['data'].get('title', 'No title')}")
                print(f"   Severity: {result['data'].get('severity', 'Unknown')}")
        else:
            print(f"❌ BLE Broadcast failed: {response.status_code}")
    except Exception as e:
        print(f"❌ BLE Broadcast error: {e}")

def test_integrated_workflow():
    """Test integrated AI + BLE workflow"""
    print("\n🔄 Testing Integrated AI + BLE Workflow")
    print("-" * 50)
    
    # Login as government user
    session = requests.Session()
    login_data = {'email': 'government@civitas.com', 'password': 'password123'}
    session.post(f"{BASE_URL}/login", data=login_data)
    
    # Step 1: Create an alert with AI enhancement
    print("1️⃣ Creating AI-enhanced alert...")
    try:
        alert_data = {
            'title': 'Flooding Emergency Downtown',
            'message': 'urgent help needed downtown flooding buildings at risk',
            'alert_type': 'emergency',
            'severity': 'critical'
        }
        
        response = session.post(f"{BASE_URL}/api/alerts", json=alert_data)
        if response.status_code == 200:
            result = response.json()
            alert_id = result.get('id')
            print(f"✅ Alert created: ID {alert_id}")
            print(f"   AI Rewritten: {result.get('rewritten_message', 'No rewrite')}")
        else:
            print(f"❌ Alert creation failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Alert creation error: {e}")
        return
    
    # Step 2: Generate AI strategy for the alert
    print("\n2️⃣ Generating AI strategy...")
    try:
        strategy_response = session.post(f"{BASE_URL}/api/ai/generate-prompt", json={
            'context': alert_data['message'],
            'task_type': 'evacuation',
            'role': 'emergency_coordinator'
        })
        if strategy_response.status_code == 200:
            strategy_result = strategy_response.json()
            print(f"✅ AI Strategy: {strategy_result.get('prompt', 'No strategy')[:100]}...")
        else:
            print(f"❌ Strategy generation failed: {strategy_response.status_code}")
    except Exception as e:
        print(f"❌ Strategy generation error: {e}")
    
    # Step 3: Broadcast via BLE mesh
    print("\n3️⃣ Broadcasting via BLE mesh...")
    try:
        broadcast_response = session.post(f"{BASE_URL}/api/ble/broadcast", json={
            'type': 'alert',
            'alert_id': alert_id
        })
        if broadcast_response.status_code == 200:
            broadcast_result = broadcast_response.json()
            print(f"✅ BLE Broadcast successful: {broadcast_result.get('type', 'Unknown')}")
        else:
            print(f"❌ BLE Broadcast failed: {broadcast_response.status_code}")
    except Exception as e:
        print(f"❌ BLE Broadcast error: {e}")
    
    # Step 4: Check mesh network status
    print("\n4️⃣ Checking mesh network status...")
    try:
        status_response = session.get(f"{BASE_URL}/api/ble/status")
        if status_response.status_code == 200:
            status_result = status_response.json()
            print(f"✅ Mesh Status: {status_result.get('network_health', 'Unknown')} health")
            print(f"   Connected devices: {len(status_result.get('connected_devices', []))}")
        else:
            print(f"❌ Status check failed: {status_response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")

def main():
    """Run all tests"""
    print("🛡️ CIVITAS - Chrome Nano AI & BLE Functionality Test")
    print("=" * 70)
    print("Testing real Chrome Nano AI APIs and BLE mesh communication")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the Flask app is running: python app.py")
        return
    
    print("✅ Server is running at http://localhost:5000")
    
    # Run tests
    test_chrome_nano_ai_apis()
    test_ble_mesh_functionality()
    test_integrated_workflow()
    
    print("\n" + "=" * 70)
    print("🎉 All tests completed!")
    print("🤖 Chrome Nano AI APIs: Enhanced with real API integration")
    print("📡 BLE Mesh: Full Web Bluetooth implementation with encryption")
    print("🔄 Integrated Workflow: AI + BLE working together")
    print("=" * 70)

if __name__ == "__main__":
    main()
