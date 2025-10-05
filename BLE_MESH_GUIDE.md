# 📡 Civitas BLE Mesh Connection Guide

## 🎯 **Quick Start - How to Connect to BLE Mesh**

### **Step 1: Enable Web Bluetooth in Chrome**
1. Open Chrome browser
2. Go to `chrome://flags/#enable-experimental-web-platform-features`
3. Enable "Experimental Web Platform features"
4. Restart Chrome

### **Step 2: Access the BLE Mesh Interface**
1. Navigate to `http://localhost:5000`
2. Login with any role:
   - **Citizen**: `citizen@civitas.com` / `password123`
   - **Rescuer**: `rescuer@civitas.com` / `password123`
   - **Government**: `government@civitas.com` / `password123`
3. Click on **"📡 BLE Mesh"** in the navigation menu

### **Step 3: Connect to Mesh Network**
1. Click **"Connect to Mesh"** button
2. Allow Bluetooth permissions when prompted
3. Select a Civitas device from the list
4. Wait for connection confirmation

### **Step 4: Discover and Communicate**
1. Click **"Discover Devices"** to scan for nearby devices
2. Use **"Test Broadcast"** to send test messages
3. Send custom messages using the text area

---

## 🔧 **Technical Details**

### **BLE Mesh Architecture**
- **Service UUID**: `12345678-1234-1234-1234-123456789abc`
- **Characteristic UUID**: `87654321-4321-4321-4321-cba987654321`
- **Device Naming**: `Civitas-{Role}-{ID}` (e.g., `Civitas-Rescuer-001`)

### **Supported Device Types**
- **Citizen Devices**: Personal emergency devices
- **Rescuer Devices**: First responder equipment
- **Government Devices**: Command center systems

### **Message Types**
- `test`: Test connectivity
- `alert`: Emergency alerts
- `mission`: Mission assignments
- `status`: Device status updates
- `user_message`: Custom user messages

---

## 🚀 **API Endpoints**

### **BLE Status**
```http
GET /api/ble/status
```
Returns current BLE mesh network status and connected devices.

### **Device Discovery**
```http
POST /api/ble/discover
```
Scans for nearby BLE devices in the mesh network.

### **Broadcast Message**
```http
POST /api/ble/broadcast
Content-Type: application/json

{
    "type": "alert",
    "message": "Emergency evacuation required"
}
```

### **Sync Offline Data**
```http
POST /api/ble/sync
Content-Type: application/json

{
    "data": {...},
    "timestamp": 1234567890
}
```

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **"Web Bluetooth not supported"**
- Ensure you're using Chrome browser
- Enable experimental web platform features
- Check if your device has Bluetooth capability

#### **"No devices found"**
- Make sure other Civitas devices are nearby
- Check if devices are powered on and in range
- Try refreshing the discovery

#### **"Connection failed"**
- Verify Bluetooth is enabled on your device
- Check Chrome has Bluetooth permissions
- Ensure the target device is not already connected

#### **"Permission denied"**
- Click "Allow" when Chrome prompts for Bluetooth access
- Check Chrome settings for Bluetooth permissions
- Try refreshing the page and reconnecting

### **Debug Information**
- Open Chrome DevTools (F12)
- Check Console tab for error messages
- Monitor Network tab for API calls
- Use Application tab to check service worker status

---

## 📱 **Mobile Setup**

### **Android Chrome**
1. Enable Bluetooth in Android settings
2. Grant Chrome location permission (required for BLE)
3. Follow the same connection steps

### **iOS Safari**
- Web Bluetooth is not yet supported in iOS Safari
- Use Chrome on Android or desktop for full functionality

---

## 🔒 **Security Features**

### **Data Encryption**
- All BLE communications are encrypted using AES-256
- Device authentication required for mesh access
- Message integrity verification

### **Access Control**
- Role-based device permissions
- Geographic proximity restrictions
- Time-based access tokens

---

## 🎮 **Testing the Connection**

### **Using the Test Script**
```bash
python connect_mesh.py
```

### **Manual Testing**
1. Open multiple browser tabs/windows
2. Login with different roles
3. Connect each to the mesh network
4. Send messages between devices
5. Verify message delivery

---

## 📊 **Network Monitoring**

### **Real-time Status**
- Connected device count
- Network health indicators
- Signal strength monitoring
- Message delivery statistics

### **Performance Metrics**
- Connection latency
- Message throughput
- Device battery levels
- Network coverage area

---

## 🚨 **Emergency Use Cases**

### **Disaster Scenarios**
1. **Earthquake**: Coordinate rescue efforts across damaged areas
2. **Flood**: Share water levels and evacuation routes
3. **Fire**: Distribute safety information and assembly points
4. **Power Outage**: Maintain communication without cellular networks

### **Message Priorities**
- **Critical**: Immediate life-threatening situations
- **High**: Urgent but not life-threatening
- **Normal**: General information and updates
- **Low**: Routine communications

---

## 🔄 **Offline Synchronization**

### **How It Works**
1. Store messages locally when offline
2. Automatically sync when BLE connection available
3. Resolve conflicts using timestamp priority
4. Maintain data integrity across devices

### **Data Persistence**
- Messages stored in IndexedDB
- Automatic cleanup of old data
- Compression for large payloads
- Backup to local storage

---

## 🎯 **Best Practices**

### **For Citizens**
- Keep device charged and nearby
- Report emergencies immediately
- Follow evacuation instructions
- Share location updates when safe

### **For Rescuers**
- Maintain mesh connectivity during operations
- Use encrypted channels for sensitive data
- Coordinate with other rescue teams
- Update mission status regularly

### **For Government**
- Monitor network health continuously
- Distribute official announcements
- Coordinate multi-agency responses
- Maintain communication logs

---

## 📞 **Support**

### **Getting Help**
- Check the troubleshooting section above
- Review browser console for error messages
- Test with the provided connection script
- Verify all prerequisites are met

### **Reporting Issues**
- Note the exact error message
- Include browser version and OS
- Describe the steps that led to the issue
- Provide any relevant console logs

---

**🎉 You're now ready to connect to the Civitas BLE Mesh Network!**

The system provides a robust, offline-first communication platform for disaster management scenarios, ensuring reliable connectivity even when traditional networks fail.
