#!/usr/bin/env python3
"""
BLE Mesh Connection Script
Demonstrates how to connect to the Civitas BLE mesh network
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def connect_to_mesh():
    """Connect to BLE mesh network"""
    print("🔗 Connecting to Civitas BLE Mesh Network")
    print("=" * 50)
    
    # Login first
    session = requests.Session()
    login_data = {'email': 'rescuer@civitas.com', 'password': 'password123'}
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Check BLE status
    print("\n📊 Checking BLE Mesh Status...")
    try:
        response = session.get(f"{BASE_URL}/api/ble/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ BLE Available: {status.get('ble_available')}")
            print(f"✅ Mesh Nodes: {status.get('mesh_nodes')}")
            print(f"✅ Network Health: {status.get('network_health')}")
            print(f"✅ Connected Devices: {len(status.get('connected_devices', []))}")
            
            for device in status.get('connected_devices', []):
                print(f"   📱 {device.get('id')} ({device.get('role')}) - {device.get('distance')}")
        else:
            print(f"❌ BLE Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ BLE Status error: {e}")
    
    # Discover nearby devices
    print("\n🔍 Discovering Nearby BLE Devices...")
    try:
        response = session.post(f"{BASE_URL}/api/ble/discover")
        if response.status_code == 200:
            discovery = response.json()
            print(f"✅ Found {discovery.get('devices_found', 0)} devices")
            
            for device in discovery.get('devices', []):
                print(f"   📡 {device.get('name')} ({device.get('role')})")
                print(f"      Distance: {device.get('distance')}")
                print(f"      Signal: {device.get('signal')} dBm")
        else:
            print(f"❌ Device discovery failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Device discovery error: {e}")
    
    # Test mesh broadcast
    print("\n📤 Testing Mesh Broadcast...")
    try:
        response = session.post(f"{BASE_URL}/api/ble/broadcast", json={
            'type': 'test',
            'message': 'Hello from Civitas mesh network!'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Broadcast successful: {result.get('status')}")
        else:
            print(f"❌ Broadcast failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Broadcast error: {e}")
    
    print("\n🎉 BLE Mesh connection test completed!")

def show_connection_instructions():
    """Show detailed connection instructions"""
    print("\n📋 BLE Mesh Connection Instructions")
    print("=" * 50)
    print("1. 🌐 Open Chrome browser")
    print("2. 🔧 Enable Web Bluetooth:")
    print("   - Go to chrome://flags/#enable-experimental-web-platform-features")
    print("   - Enable 'Experimental Web Platform features'")
    print("   - Restart Chrome")
    print("3. 🔗 Navigate to http://localhost:5000")
    print("4. 🔐 Login with any role (citizen/rescuer/government)")
    print("5. 📡 Look for BLE status indicator in header")
    print("6. 🎯 Click 'Connect to Mesh' or similar button")
    print("7. ✅ Allow Bluetooth permissions when prompted")
    print("8. 📱 Select a Civitas device from the list")
    print("9. 🎉 You're connected to the mesh network!")
    
    print("\n🔧 Troubleshooting:")
    print("- Make sure Bluetooth is enabled on your device")
    print("- Ensure Chrome has Bluetooth permissions")
    print("- Try refreshing the page if connection fails")
    print("- Check browser console for error messages")

def main():
    """Main function"""
    print("🛡️ CIVITAS - BLE Mesh Connection Guide")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            connect_to_mesh()
        else:
            print("❌ Server not responding properly")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the Flask app: python app.py")
    
    show_connection_instructions()

if __name__ == "__main__":
    main()
