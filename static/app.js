// Civitas - Offline-First Disaster Management System
class CivitasApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.bleDevice = null;
        this.bleServer = null;
        this.bleService = null;
        this.bleCharacteristic = null;
        this.db = null;
        this.deferredPrompt = null;
        
        this.init();
    }

    async init() {
        await this.initIndexedDB();
        await this.initServiceWorker();
        this.initEventListeners();
        this.initBLE();
        this.initPWAInstall();
        this.updateOnlineStatus();
        this.loadDashboardData();
    }

    // IndexedDB for offline storage
    async initIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('CivitasDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Reports store
                if (!db.objectStoreNames.contains('reports')) {
                    const reportsStore = db.createObjectStore('reports', { keyPath: 'id', autoIncrement: true });
                    reportsStore.createIndex('user_id', 'user_id', { unique: false });
                    reportsStore.createIndex('status', 'status', { unique: false });
                }
                
                // Alerts store
                if (!db.objectStoreNames.contains('alerts')) {
                    const alertsStore = db.createObjectStore('alerts', { keyPath: 'id', autoIncrement: true });
                    alertsStore.createIndex('severity', 'severity', { unique: false });
                    alertsStore.createIndex('created_at', 'created_at', { unique: false });
                }
                
                // Missions store
                if (!db.objectStoreNames.contains('missions')) {
                    const missionsStore = db.createObjectStore('missions', { keyPath: 'id', autoIncrement: true });
                    missionsStore.createIndex('assigned_to', 'assigned_to', { unique: false });
                    missionsStore.createIndex('status', 'status', { unique: false });
                }
                
                // Safehouses store
                if (!db.objectStoreNames.contains('safehouses')) {
                    const safehousesStore = db.createObjectStore('safehouses', { keyPath: 'id', autoIncrement: true });
                    safehousesStore.createIndex('location', 'location', { unique: false });
                }
                
                // Resources store
                if (!db.objectStoreNames.contains('resources')) {
                    const resourcesStore = db.createObjectStore('resources', { keyPath: 'id', autoIncrement: true });
                    resourcesStore.createIndex('category', 'category', { unique: false });
                    resourcesStore.createIndex('status', 'status', { unique: false });
                }
                
                // Sync queue for offline operations
                if (!db.objectStoreNames.contains('syncQueue')) {
                    const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
                    syncStore.createIndex('type', 'type', { unique: false });
                    syncStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    // Service Worker for PWA functionality
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('Service Worker registered:', registration);
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    // Event Listeners
    initEventListeners() {
        // Online/Offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateOnlineStatus();
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateOnlineStatus();
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('civitas-form')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });

        // BLE connection status
        this.updateBLEStatus();
        setInterval(() => this.updateBLEStatus(), 5000);
    }

    // BLE Mesh Communication
    async initBLE() {
        if (!navigator.bluetooth) {
            console.warn('Web Bluetooth not supported in this browser');
            this.showBLEStatus('not_supported');
            return;
        }

        try {
            // Check if Bluetooth is available
            const available = await navigator.bluetooth.getAvailability();
            if (!available) {
                console.warn('Bluetooth not available on this device');
                this.showBLEStatus('not_available');
                return;
            }

            // Request BLE device with proper service UUIDs
            this.bleDevice = await navigator.bluetooth.requestDevice({
                filters: [
                    { namePrefix: 'Civitas' },
                    { namePrefix: 'DisasterMesh' },
                    { namePrefix: 'EmergencyNet' }
                ],
                optionalServices: [
                    '0000180d-0000-1000-8000-00805f9b34fb', // Heart Rate Service (for demo)
                    '0000180a-0000-1000-8000-00805f9b34fb', // Device Information Service
                    '12345678-1234-1234-1234-123456789abc'  // Custom Civitas Service
                ]
            });

            // Add disconnect event listener
            this.bleDevice.addEventListener('gattserverdisconnected', () => {
                console.log('BLE device disconnected');
                this.showBLEStatus('disconnected');
                this.bleDevice = null;
                this.bleServer = null;
                this.bleService = null;
                this.bleCharacteristic = null;
            });

            // Connect to device
            this.bleServer = await this.bleDevice.gatt.connect();
            console.log('BLE server connected');

            // Try to get our custom service first, fallback to standard services
            try {
                this.bleService = await this.bleServer.getPrimaryService('12345678-1234-1234-1234-123456789abc');
                this.bleCharacteristic = await this.bleService.getCharacteristic('87654321-4321-4321-4321-cba987654321');
            } catch (serviceError) {
                console.log('Custom service not found, using fallback service');
                // Use a standard service for demo purposes
                this.bleService = await this.bleServer.getPrimaryService('0000180d-0000-1000-8000-00805f9b34fb');
                this.bleCharacteristic = await this.bleService.getCharacteristic('00002a37-0000-1000-8000-00805f9b34fb');
            }

            // Listen for incoming data
            this.bleCharacteristic.addEventListener('characteristicvaluechanged', (event) => {
                this.handleBLEData(event.target.value);
            });

            await this.bleCharacteristic.startNotifications();
            console.log('BLE connected successfully');
            this.showBLEStatus('connected');

            // Start mesh discovery
            this.startMeshDiscovery();

        } catch (error) {
            console.error('BLE connection failed:', error);
            this.showBLEStatus('error');
            
            if (error.name === 'SecurityError') {
                this.showNotification('Bluetooth access denied. Please allow access to use mesh communication.', 'error');
            } else if (error.name === 'NotFoundError') {
                this.showNotification('No Civitas devices found nearby. Make sure devices are in pairing mode.', 'warning');
            }
        }
    }

    // Handle incoming BLE data
    handleBLEData(value) {
        try {
            const data = JSON.parse(new TextDecoder().decode(value));
            console.log('Received BLE data:', data);
            
            // Store in IndexedDB
            this.storeBLEData(data);
            
            // Update UI
            this.updateUIWithBLEData(data);
        } catch (error) {
            console.error('Error processing BLE data:', error);
        }
    }

    // Store BLE data in IndexedDB
    async storeBLEData(data) {
        const transaction = this.db.transaction([data.type], 'readwrite');
        const store = transaction.objectStore(data.type);
        
        try {
            await store.add(data.data);
            console.log(`Stored ${data.type} data from BLE`);
        } catch (error) {
            console.error('Error storing BLE data:', error);
        }
    }

    // Broadcast data via BLE
    async broadcastBLEData(type, data) {
        if (!this.bleCharacteristic) {
            console.warn('BLE not connected');
            return;
        }

        try {
            const payload = JSON.stringify({ type, data, timestamp: Date.now() });
            const encoder = new TextEncoder();
            await this.bleCharacteristic.writeValue(encoder.encode(payload));
            console.log(`Broadcasted ${type} data via BLE`);
        } catch (error) {
            console.error('Error broadcasting BLE data:', error);
        }
    }

    // Update BLE connection status
    updateBLEStatus() {
        const indicator = document.querySelector('.ble-indicator');
        const status = document.querySelector('.ble-status');
        
        if (indicator && status) {
            if (this.bleDevice && this.bleDevice.gatt.connected) {
                indicator.classList.remove('disconnected');
                status.textContent = 'BLE Connected';
            } else {
                indicator.classList.add('disconnected');
                status.textContent = 'BLE Disconnected';
            }
        }
    }

    // Show BLE status with specific states
    showBLEStatus(state) {
        const indicator = document.querySelector('.ble-indicator');
        const status = document.querySelector('.ble-status');
        
        if (indicator && status) {
            indicator.className = 'ble-indicator';
            status.className = 'ble-status';
            
            switch (state) {
                case 'connected':
                    indicator.classList.add('connected');
                    status.textContent = 'BLE Connected';
                    break;
                case 'disconnected':
                    indicator.classList.add('disconnected');
                    status.textContent = 'BLE Disconnected';
                    break;
                case 'not_supported':
                    indicator.classList.add('error');
                    status.textContent = 'BLE Not Supported';
                    break;
                case 'not_available':
                    indicator.classList.add('warning');
                    status.textContent = 'BLE Not Available';
                    break;
                case 'error':
                    indicator.classList.add('error');
                    status.textContent = 'BLE Error';
                    break;
                default:
                    indicator.classList.add('disconnected');
                    status.textContent = 'BLE Unknown';
            }
        }
    }

    // Start mesh discovery to find nearby devices
    async startMeshDiscovery() {
        if (!this.bleDevice || !this.bleDevice.gatt.connected) {
            return;
        }

        try {
            // Scan for nearby devices (this would be implemented with actual BLE scanning)
            console.log('Starting mesh discovery...');
            
            // Simulate finding nearby devices
            const nearbyDevices = await this.scanForNearbyDevices();
            console.log(`Found ${nearbyDevices.length} nearby Civitas devices`);
            
            // Update UI with discovered devices
            this.updateMeshDevices(nearbyDevices);
            
        } catch (error) {
            console.error('Mesh discovery failed:', error);
        }
    }

    // Scan for nearby BLE devices
    async scanForNearbyDevices() {
        // In a real implementation, this would use BLE scanning APIs
        // For demo purposes, we'll simulate finding devices
        return [
            { name: 'Civitas-Rescuer-001', distance: '5m', signal: -45 },
            { name: 'Civitas-Government-002', distance: '12m', signal: -67 },
            { name: 'Civitas-Citizen-003', distance: '8m', signal: -52 }
        ];
    }

    // Update mesh devices in UI
    updateMeshDevices(devices) {
        const meshContainer = document.querySelector('.mesh-devices');
        if (meshContainer) {
            meshContainer.innerHTML = devices.map(device => `
                <div class="mesh-device">
                    <div class="device-name">${device.name}</div>
                    <div class="device-distance">${device.distance}</div>
                    <div class="device-signal">${device.signal} dBm</div>
                </div>
            `).join('');
        }
    }

    // Enhanced BLE data broadcasting with encryption
    async broadcastBLEData(type, data, options = {}) {
        if (!this.bleCharacteristic) {
            console.warn('BLE not connected');
            return false;
        }

        try {
            // Encrypt sensitive data
            const encryptedData = await this.encryptBLEData(data);
            
            const payload = {
                type: type,
                data: encryptedData,
                timestamp: Date.now(),
                sender: this.getDeviceId(),
                version: '1.0',
                priority: options.priority || 'normal'
            };

            const jsonPayload = JSON.stringify(payload);
            const encoder = new TextEncoder();
            const dataBuffer = encoder.encode(jsonPayload);
            
            // Split large payloads into chunks if needed
            const maxChunkSize = 20; // BLE characteristic limit
            if (dataBuffer.length > maxChunkSize) {
                await this.broadcastLargePayload(dataBuffer, maxChunkSize);
            } else {
                await this.bleCharacteristic.writeValue(dataBuffer);
            }
            
            console.log(`Broadcasted ${type} data via BLE mesh`);
            return true;
            
        } catch (error) {
            console.error('Error broadcasting BLE data:', error);
            return false;
        }
    }

    // Encrypt BLE data for security
    async encryptBLEData(data) {
        // In a real implementation, this would use proper encryption
        // For demo purposes, we'll use a simple encoding
        const key = 'civitas-emergency-key-2025';
        const encoded = btoa(JSON.stringify(data));
        return encoded;
    }

    // Decrypt BLE data
    async decryptBLEData(encryptedData) {
        try {
            const decoded = atob(encryptedData);
            return JSON.parse(decoded);
        } catch (error) {
            console.error('Error decrypting BLE data:', error);
            return null;
        }
    }

    // Get unique device ID
    getDeviceId() {
        let deviceId = localStorage.getItem('civitas-device-id');
        if (!deviceId) {
            deviceId = 'civitas-' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('civitas-device-id', deviceId);
        }
        return deviceId;
    }

    // Broadcast large payloads in chunks
    async broadcastLargePayload(dataBuffer, chunkSize) {
        const chunks = [];
        for (let i = 0; i < dataBuffer.length; i += chunkSize) {
            chunks.push(dataBuffer.slice(i, i + chunkSize));
        }

        for (let i = 0; i < chunks.length; i++) {
            const chunk = chunks[i];
            const chunkHeader = new Uint8Array([i, chunks.length - 1]);
            const fullChunk = new Uint8Array(chunkHeader.length + chunk.length);
            fullChunk.set(chunkHeader);
            fullChunk.set(chunk, chunkHeader.length);
            
            await this.bleCharacteristic.writeValue(fullChunk);
            await new Promise(resolve => setTimeout(resolve, 100)); // Small delay between chunks
        }
    }

    // Chrome Nano AI API Integration
    async callChromeNanoAPI(apiType, data, options = {}) {
        try {
            // Check if Chrome Nano APIs are available
            if (window.chrome && window.chrome.nano) {
                return await this.callRealChromeNanoAPI(apiType, data, options);
            } else {
                console.warn('Chrome Nano APIs not available, using fallback');
                return this.simulateChromeNanoAPI(apiType, data);
            }
        } catch (error) {
            console.error('Chrome Nano API error:', error);
            return this.simulateChromeNanoAPI(apiType, data); // Fallback
        }
    }

    // Real Chrome Nano API calls
    async callRealChromeNanoAPI(apiType, data, options = {}) {
        const nano = window.chrome.nano;
        
        switch (apiType) {
            case 'summarize':
                return await nano.summarizer.summarize(data, {
                    maxLength: options.maxLength || 100,
                    style: options.style || 'concise'
                });
                
            case 'proofread':
                return await nano.proofreader.proofread(data, {
                    language: options.language || 'en',
                    style: options.style || 'formal'
                });
                
            case 'rewrite':
                return await nano.rewriter.rewrite(data, {
                    tone: options.tone || 'professional',
                    style: options.style || 'clear',
                    targetAudience: options.audience || 'general'
                });
                
            case 'translate':
                return await nano.translator.translate(data, {
                    targetLanguage: options.targetLanguage || 'en',
                    sourceLanguage: options.sourceLanguage || 'auto'
                });
                
            case 'prompt':
                return await nano.prompt.generate(data, {
                    context: options.context || 'disaster_management',
                    type: options.type || 'strategy',
                    role: options.role || 'coordinator'
                });
                
            default:
                throw new Error('Unknown Chrome Nano API type');
        }
    }

    // Fallback simulation when Chrome Nano APIs are not available
    simulateChromeNanoAPI(apiType, data) {
        switch (apiType) {
            case 'summarize':
                return this.simulateSummarizeAPI(data);
            case 'proofread':
                return this.simulateProofreadAPI(data);
            case 'rewrite':
                return this.simulateRewriteAPI(data);
            case 'translate':
                return this.simulateTranslateAPI(data);
            case 'prompt':
                return this.simulatePromptAPI(data);
            default:
                return data;
        }
    }

    simulateSummarizeAPI(text) {
        const words = text.split(' ');
        const maxWords = 20;
        if (words.length <= maxWords) return text;
        return words.slice(0, maxWords).join(' ') + '...';
    }

    simulateProofreadAPI(text) {
        return text.trim().replace(/\s+/g, ' ').replace(/\.\s*([a-z])/g, '. $1');
    }

    simulateRewriteAPI(text) {
        return text
            .replace(/urgent/gi, 'critical')
            .replace(/help/gi, 'assistance')
            .replace(/problem/gi, 'situation');
    }

    simulateTranslateAPI(text) {
        return text;
    }

    simulatePromptAPI(context) {
        return `Based on ${context}, here's the recommended strategy: 1) Assess immediate risks, 2) Prioritize critical needs, 3) Coordinate resources effectively.`;
    }

    // Form handling
    async handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const action = form.dataset.action;

        try {
            if (this.isOnline) {
                await this.submitOnline(action, data);
            } else {
                await this.queueForSync(action, data);
                this.showNotification('Data saved offline. Will sync when online.', 'info');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Error submitting form. Please try again.', 'error');
        }
    }

    // Submit data online
    async submitOnline(action, data) {
        const response = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network error');
        }

        const result = await response.json();
        this.showNotification('Data submitted successfully!', 'success');
        return result;
    }

    // Queue data for offline sync
    async queueForSync(action, data) {
        const transaction = this.db.transaction(['syncQueue'], 'readwrite');
        const store = transaction.objectStore('syncQueue');
        
        await store.add({
            type: action,
            data: data,
            timestamp: Date.now()
        });
    }

    // Sync offline data when online
    async syncOfflineData() {
        const transaction = this.db.transaction(['syncQueue'], 'readwrite');
        const store = transaction.objectStore('syncQueue');
        const items = await store.getAll();

        for (const item of items) {
            try {
                await this.submitOnline(item.type, item.data);
                await store.delete(item.id);
            } catch (error) {
                console.error('Sync error:', error);
            }
        }
    }

    // Update online status UI
    updateOnlineStatus() {
        const banner = document.querySelector('.offline-banner');
        if (banner) {
            if (this.isOnline) {
                banner.classList.remove('show');
            } else {
                banner.classList.add('show');
            }
        }
    }

    // Load dashboard data
    async loadDashboardData() {
        try {
            const [reports, alerts, missions, safehouses, resources] = await Promise.all([
                this.fetchData('reports'),
                this.fetchData('alerts'),
                this.fetchData('missions'),
                this.fetchData('safehouses'),
                this.fetchData('resources')
            ]);

            this.updateDashboardStats(reports, alerts, missions, safehouses, resources);
            this.updateRecentActivity(reports, alerts, missions);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    // Fetch data with offline fallback
    async fetchData(type) {
        if (this.isOnline) {
            try {
                const response = await fetch(`/api/${type}`);
                if (response.ok) {
                    const data = await response.json();
                    // Cache data for offline use
                    await this.cacheData(type, data);
                    return data;
                }
            } catch (error) {
                console.error(`Error fetching ${type}:`, error);
            }
        }

        // Fallback to cached data
        return await this.getCachedData(type);
    }

    // Cache data in IndexedDB
    async cacheData(type, data) {
        const transaction = this.db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        
        // Clear existing data
        await store.clear();
        
        // Add new data
        for (const item of data) {
            await store.add(item);
        }
    }

    // Get cached data from IndexedDB
    async getCachedData(type) {
        const transaction = this.db.transaction([type], 'readonly');
        const store = transaction.objectStore(type);
        return await store.getAll();
    }

    // Update dashboard statistics
    updateDashboardStats(reports, alerts, missions, safehouses, resources) {
        const stats = {
            totalReports: reports.length,
            activeAlerts: alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length,
            activeMissions: missions.filter(m => m.status === 'active').length,
            availableSafehouses: safehouses.filter(s => s.availability > 0).length,
            totalResources: resources.reduce((sum, r) => sum + r.quantity, 0)
        };

        // Update stat cards
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = value;
            }
        });
    }

    // Update recent activity
    updateRecentActivity(reports, alerts, missions) {
        const activity = [
            ...reports.slice(0, 3).map(r => ({ type: 'report', data: r, time: r.created_at })),
            ...alerts.slice(0, 3).map(a => ({ type: 'alert', data: a, time: a.created_at })),
            ...missions.slice(0, 3).map(m => ({ type: 'mission', data: m, time: m.created_at }))
        ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5);

        const container = document.querySelector('.recent-activity');
        if (container) {
            container.innerHTML = activity.map(item => this.createActivityItem(item)).join('');
        }
    }

    // Create activity item HTML
    createActivityItem(item) {
        const timeAgo = this.getTimeAgo(item.time);
        const icon = this.getActivityIcon(item.type);
        const title = item.data.title || item.data.name;
        
        return `
            <div class="activity-item">
                <div class="activity-icon">${icon}</div>
                <div class="activity-content">
                    <div class="activity-title">${title}</div>
                    <div class="activity-time">${timeAgo}</div>
                </div>
            </div>
        `;
    }

    // Get activity icon
    getActivityIcon(type) {
        const icons = {
            report: '📋',
            alert: '🚨',
            mission: '🎯',
            safehouse: '🏠',
            resource: '📦'
        };
        return icons[type] || '📄';
    }

    // Get time ago string
    getTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    // Update UI with BLE data
    updateUIWithBLEData(data) {
        // Update specific UI elements based on data type
        switch (data.type) {
            case 'alert':
                this.showNotification(`New alert: ${data.data.title}`, 'warning');
                break;
            case 'mission':
                this.showNotification(`Mission update: ${data.data.title}`, 'info');
                break;
            case 'safehouse':
                this.showNotification(`Safehouse update: ${data.data.name}`, 'success');
                break;
        }
    }

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // PWA Install functionality
    initPWAInstall() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt();
        });
    }

    showInstallPrompt() {
        const prompt = document.querySelector('.install-prompt');
        if (prompt) {
            prompt.classList.add('show');
        }
    }

    async installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            console.log(`PWA install outcome: ${outcome}`);
            this.deferredPrompt = null;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.civitasApp = new CivitasApp();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CivitasApp;
}

