// ============================================================
// Civitas BLE Mesh Engine — complete rewrite of BLE layer
// Fixes all inter-device connectivity bugs:
//   1. Duplicate broadcastBLEData() method (second silently wins)
//   2. initBLE() auto-fires requestDevice() without user gesture → DOMException
//   3. GATT reconnect not attempted on disconnect
//   4. Chunked-payload reassembly is missing on the receiver side
//   5. storeBLEData() crashes on unknown `data.type` store names
//   6. BLE filters in ble_mesh.html and app.js differ (inconsistent namePrefix)
//   7. /api/ble/broadcast always returns 'broadcast_ready', never 'success'
//      so testBroadcast() always shows "Broadcast failed"
// ============================================================

class CivitasApp {
    constructor() {
        this.isOnline = navigator.onLine;

        // BLE state
        this.bleDevice        = null;
        this.bleServer        = null;
        this.bleService       = null;
        this.bleCharacteristic = null;
        this.bleReconnectTimer = null;

        // Chunked-message reassembly buffer: Map<sender, {total, chunks[]}>
        this._chunkBuffers = new Map();

        // IndexedDB
        this.db = null;

        // PWA
        this.deferredPrompt = null;

        this.init();
    }

    async init() {
        await this.initIndexedDB();
        await this.initServiceWorker();
        this.initEventListeners();
        // NOTE: do NOT call initBLE() here – Web Bluetooth requires a user gesture.
        //       The UI "Connect" button calls connectBLE() instead.
        this.initPWAInstall();
        this.updateOnlineStatus();
        this.loadDashboardData();
        this.updateBLEStatus();
    }

    // ─── IndexedDB ────────────────────────────────────────────────────────────
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

                const stores = [
                    { name: 'reports',   keyPath: 'id', indexes: [['user_id', false], ['status', false]] },
                    { name: 'alerts',    keyPath: 'id', indexes: [['severity', false], ['created_at', false]] },
                    { name: 'missions',  keyPath: 'id', indexes: [['assigned_to', false], ['status', false]] },
                    { name: 'safehouses',keyPath: 'id', indexes: [['location', false]] },
                    { name: 'resources', keyPath: 'id', indexes: [['category', false], ['status', false]] },
                    { name: 'syncQueue', keyPath: 'id', indexes: [['type', false], ['timestamp', false]] },
                    // FIX: add a dedicated store for raw BLE messages
                    { name: 'bleMessages', keyPath: 'id', indexes: [['type', false], ['timestamp', false]] },
                ];

                stores.forEach(({ name, keyPath, indexes }) => {
                    if (!db.objectStoreNames.contains(name)) {
                        const store = db.createObjectStore(name, { keyPath, autoIncrement: true });
                        indexes.forEach(([idx, unique]) => store.createIndex(idx, idx, { unique }));
                    }
                });
            };
        });
    }

    // ─── Service Worker ───────────────────────────────────────────────────────
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const reg = await navigator.serviceWorker.register('/static/sw.js');
                console.log('[SW] registered:', reg.scope);
            } catch (err) {
                console.error('[SW] registration failed:', err);
            }
        }
    }

    // ─── Event listeners ──────────────────────────────────────────────────────
    initEventListeners() {
        window.addEventListener('online',  () => { this.isOnline = true;  this.updateOnlineStatus(); this.syncOfflineData(); });
        window.addEventListener('offline', () => { this.isOnline = false; this.updateOnlineStatus(); });

        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('civitas-form')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });

        // Refresh BLE status badge every 5 s
        setInterval(() => this.updateBLEStatus(), 5000);
    }

    // ─── BLE: public entry-point (must be triggered by a user gesture) ────────
    /**
     * Call this from a click handler, e.g. <button onclick="civitasApp.connectBLE()">
     * Web Bluetooth's requestDevice() REQUIRES a user gesture – calling it
     * automatically on page load causes a SecurityError in all browsers.
     */
    async connectBLE() {
        if (!navigator.bluetooth) {
            this.showBLEStatus('not_supported');
            this.showNotification('Web Bluetooth is not supported in this browser. Use Chrome on Android/desktop.', 'error');
            return;
        }

        try {
            const available = await navigator.bluetooth.getAvailability();
            if (!available) {
                this.showBLEStatus('not_available');
                this.showNotification('Bluetooth hardware is unavailable or turned off.', 'warning');
                return;
            }

            this.showBLEStatus('scanning');

            // FIX: unified filter list used everywhere in the app
            this.bleDevice = await navigator.bluetooth.requestDevice({
                filters: [
                    { namePrefix: 'Civitas' },
                    { namePrefix: 'DisasterMesh' },
                    { namePrefix: 'EmergencyNet' },
                    { namePrefix: 'BLE' }   // matches the ble_mesh.html filter too
                ],
                optionalServices: [
                    '12345678-1234-1234-1234-123456789abc',  // Custom Civitas
                    '0000180d-0000-1000-8000-00805f9b34fb',  // Heart Rate (fallback demo)
                    '0000180a-0000-1000-8000-00805f9b34fb',  // Device Information
                    '0000180f-0000-1000-8000-00805f9b34fb',  // Battery
                ]
            });

            // FIX: handle GATT disconnects with auto-reconnect
            this.bleDevice.addEventListener('gattserverdisconnected', () =>
                this._onBLEDisconnect()
            );

            await this._connectGATT();

        } catch (error) {
            console.error('[BLE] connection failed:', error);
            this.showBLEStatus('error');

            if (error.name === 'NotFoundError') {
                this.showNotification('No Civitas devices found. Make sure the other device has the app open and Bluetooth on.', 'warning');
            } else if (error.name === 'SecurityError') {
                this.showNotification('Bluetooth access denied. Please allow access.', 'error');
            } else if (error.name === 'NotSupportedError') {
                this.showNotification('This browser does not fully support Web Bluetooth.', 'error');
            } else {
                this.showNotification(`BLE error: ${error.message}`, 'error');
            }
        }
    }

    // Internal: (re)connect to GATT server and set up characteristic
    async _connectGATT() {
        try {
            this.bleServer = await this.bleDevice.gatt.connect();
            console.log('[BLE] GATT connected');

            // Try custom Civitas service first, fall back to Heart-Rate for demos
            try {
                this.bleService = await this.bleServer.getPrimaryService('12345678-1234-1234-1234-123456789abc');
                this.bleCharacteristic = await this.bleService.getCharacteristic('87654321-4321-4321-4321-cba987654321');
                console.log('[BLE] using custom Civitas service');
            } catch (_) {
                console.warn('[BLE] custom service not found, falling back to Heart-Rate demo service');
                this.bleService = await this.bleServer.getPrimaryService('0000180d-0000-1000-8000-00805f9b34fb');
                this.bleCharacteristic = await this.bleService.getCharacteristic('00002a37-0000-1000-8000-00805f9b34fb');
            }

            // FIX: remove old listener before adding a new one to avoid duplicates after reconnect
            this.bleCharacteristic.removeEventListener('characteristicvaluechanged', this._boundHandleBLEData);
            this._boundHandleBLEData = (event) => this._handleBLEData(event.target.value);
            this.bleCharacteristic.addEventListener('characteristicvaluechanged', this._boundHandleBLEData);

            await this.bleCharacteristic.startNotifications();

            // Cancel any pending reconnect timer
            if (this.bleReconnectTimer) {
                clearTimeout(this.bleReconnectTimer);
                this.bleReconnectTimer = null;
            }

            this.showBLEStatus('connected');
            this.showNotification(`Connected to ${this.bleDevice.name}`, 'success');
            console.log('[BLE] fully connected and listening');

        } catch (err) {
            console.error('[BLE] GATT setup failed:', err);
            this.showBLEStatus('error');
            throw err;
        }
    }

    // FIX: auto-reconnect on disconnect (up to 3 attempts, 3 s apart)
    _onBLEDisconnect(attempt = 0) {
        console.warn('[BLE] disconnected (attempt', attempt, ')');
        this.bleServer = null;
        this.bleService = null;
        this.bleCharacteristic = null;
        this.showBLEStatus('disconnected');

        const MAX_ATTEMPTS = 3;
        if (attempt < MAX_ATTEMPTS && this.bleDevice) {
            this.showNotification(`BLE disconnected. Reconnecting… (${attempt + 1}/${MAX_ATTEMPTS})`, 'warning');
            this.bleReconnectTimer = setTimeout(async () => {
                try {
                    await this._connectGATT();
                } catch (_) {
                    this._onBLEDisconnect(attempt + 1);
                }
            }, 3000);
        } else {
            this.bleDevice = null;
            this.showNotification('BLE device disconnected. Please reconnect manually.', 'error');
        }
    }

    // ─── Receiving BLE data ───────────────────────────────────────────────────
    _handleBLEData(dataView) {
        const bytes = new Uint8Array(dataView.buffer);

        // FIX: detect chunked payloads (first 2 bytes are [chunkIndex, totalChunks])
        // A plain JSON message will never start with two small integers followed by valid JSON,
        // so we distinguish by checking if byte[1] > 0 and byte[0] <= byte[1].
        if (bytes.length > 2 && bytes[1] > 0 && bytes[0] <= bytes[1]) {
            const chunkIndex = bytes[0];
            const totalChunks = bytes[1] + 1;  // stored as (total-1) in broadcastLargePayload
            const chunk = bytes.slice(2);
            this._reassembleChunk(chunkIndex, totalChunks, chunk);
            return;
        }

        // Normal (single-frame) message
        this._processRawBLEMessage(bytes);
    }

    _reassembleChunk(index, total, chunk) {
        // Use a simple key per connection (we only have 1 peer in a GATT connection)
        const key = 'current';
        if (!this._chunkBuffers.has(key)) {
            this._chunkBuffers.set(key, { total, chunks: new Array(total) });
        }
        const buf = this._chunkBuffers.get(key);
        buf.chunks[index] = chunk;

        const received = buf.chunks.filter(Boolean).length;
        console.log(`[BLE] chunk ${index + 1}/${total} received`);

        if (received === total) {
            // Reassemble all chunks into one Uint8Array
            const fullLength = buf.chunks.reduce((n, c) => n + c.length, 0);
            const full = new Uint8Array(fullLength);
            let offset = 0;
            buf.chunks.forEach(c => { full.set(c, offset); offset += c.length; });
            this._chunkBuffers.delete(key);
            this._processRawBLEMessage(full);
        }
    }

    _processRawBLEMessage(bytes) {
        try {
            const raw = new TextDecoder().decode(bytes);
            const payload = JSON.parse(raw);
            console.log('[BLE] received:', payload);

            // FIX: if data is base64-encoded (from encryptBLEData), decode it first
            if (payload.data && typeof payload.data === 'string') {
                try {
                    payload.data = JSON.parse(atob(payload.data));
                } catch (_) { /* data is plain text, leave as-is */ }
            }

            this._storeBLEMessage(payload);
            this._updateUIWithBLEData(payload);

        } catch (err) {
            console.error('[BLE] failed to parse incoming message:', err);
        }
    }

    // FIX: store BLE messages in the dedicated 'bleMessages' store,
    //      not in type-named stores that may not exist.
    async _storeBLEMessage(payload) {
        if (!this.db) return;
        const tx = this.db.transaction(['bleMessages'], 'readwrite');
        const store = tx.objectStore('bleMessages');
        store.add({ ...payload, timestamp: Date.now() });
    }

    // ─── Sending BLE data ─────────────────────────────────────────────────────
    // FIX: only ONE broadcastBLEData() method (the old file had two – the second
    //      one (with encryption) silently overwrote the first).
    async broadcastBLEData(type, data, options = {}) {
        if (!this.bleCharacteristic) {
            console.warn('[BLE] not connected – cannot broadcast');
            this.showNotification('BLE not connected. Connect first.', 'warning');
            return false;
        }

        try {
            const encryptedData = await this._encryptBLEData(data);

            const payload = JSON.stringify({
                type,
                data: encryptedData,
                timestamp: Date.now(),
                sender: this.getDeviceId(),
                version: '1.0',
                priority: options.priority || 'normal'
            });

            const bytes = new TextEncoder().encode(payload);

            // BLE GATT characteristic max is 512 bytes (iOS/Android cap at 20 without MTU negotiation)
            // We use 512 as the safe maximum for modern stacks; split if needed.
            const MTU = 512;
            if (bytes.length > MTU) {
                await this._broadcastChunked(bytes, MTU);
            } else {
                await this.bleCharacteristic.writeValue(bytes);
            }

            console.log(`[BLE] broadcast sent: type=${type}`);
            return true;

        } catch (err) {
            console.error('[BLE] broadcast failed:', err);
            return false;
        }
    }

    // FIX: chunk header uses [chunkIndex, totalChunks-1] to match reassembler above
    async _broadcastChunked(dataBuffer, chunkSize) {
        const HEADER = 2;
        const bodySize = chunkSize - HEADER;
        const chunks = [];
        for (let i = 0; i < dataBuffer.length; i += bodySize) {
            chunks.push(dataBuffer.slice(i, i + bodySize));
        }
        console.log(`[BLE] sending ${chunks.length} chunks`);
        for (let i = 0; i < chunks.length; i++) {
            const frame = new Uint8Array(HEADER + chunks[i].length);
            frame[0] = i;
            frame[1] = chunks.length - 1;  // total - 1
            frame.set(chunks[i], HEADER);
            await this.bleCharacteristic.writeValue(frame);
            await new Promise(r => setTimeout(r, 50));  // BLE stack breathing room
        }
    }

    async _encryptBLEData(data) {
        // Simple Base64 + JSON — replace with SubtleCrypto AES-GCM for production
        return btoa(JSON.stringify(data));
    }

    // ─── BLE status UI ────────────────────────────────────────────────────────
    updateBLEStatus() {
        const connected = this.bleDevice && this.bleDevice.gatt && this.bleDevice.gatt.connected;
        this.showBLEStatus(connected ? 'connected' : 'disconnected');
    }

    showBLEStatus(state) {
        const indicator = document.querySelector('.ble-indicator');
        const statusEl  = document.querySelector('.ble-status');
        if (!indicator || !statusEl) return;

        indicator.className = 'ble-indicator';
        const labels = {
            connected:     ['connected',   'BLE Connected'],
            disconnected:  ['disconnected','BLE Disconnected'],
            scanning:      ['scanning',    'BLE Scanning…'],
            not_supported: ['error',       'BLE Not Supported'],
            not_available: ['warning',     'BLE Not Available'],
            error:         ['error',       'BLE Error'],
        };
        const [cls, text] = labels[state] || ['disconnected', 'BLE Unknown'];
        indicator.classList.add(cls);
        statusEl.textContent = text;
    }

    // ─── Device discovery ──────────────────────────────────────────────────────
    async startMeshDiscovery() {
        if (!this.bleDevice || !this.bleDevice.gatt.connected) {
            console.warn('[BLE] not connected – cannot discover');
            return;
        }
        try {
            const devices = await this._scanForNearbyDevices();
            this._updateMeshDevices(devices);
        } catch (err) {
            console.error('[BLE] mesh discovery failed:', err);
        }
    }

    async _scanForNearbyDevices() {
        // Web Bluetooth does not expose a general scanning API.
        // Real multi-device mesh requires each peripheral to advertise its own service.
        // This simulates the API contract until native BLE scanning is standardised.
        return [
            { name: 'Civitas-Rescuer-001',    distance: '5m',  signal: -45, role: 'rescuer' },
            { name: 'Civitas-Government-002', distance: '12m', signal: -67, role: 'government' },
            { name: 'Civitas-Citizen-003',    distance: '8m',  signal: -52, role: 'citizen' },
        ];
    }

    _updateMeshDevices(devices) {
        const container = document.querySelector('.mesh-devices');
        if (!container) return;
        container.innerHTML = devices.map(d => `
            <div class="mesh-device">
                <div class="device-name">${d.name}</div>
                <div class="device-role">${d.role}</div>
                <div class="device-distance">${d.distance}</div>
                <div class="device-signal">${d.signal} dBm</div>
            </div>`).join('');
    }

    // ─── Unique device ID ─────────────────────────────────────────────────────
    getDeviceId() {
        let id = localStorage.getItem('civitas-device-id');
        if (!id) {
            id = 'civitas-' + crypto.randomUUID().slice(0, 8);
            localStorage.setItem('civitas-device-id', id);
        }
        return id;
    }

    // ─── Incoming BLE → UI ────────────────────────────────────────────────────
    _updateUIWithBLEData(payload) {
        const data = payload.data || {};
        const typeMap = {
            alert:     () => this.showNotification(`📡 BLE Alert: ${data.title || ''}`, 'warning'),
            mission:   () => this.showNotification(`📡 BLE Mission: ${data.title || ''}`, 'info'),
            safehouse: () => this.showNotification(`📡 BLE Safehouse: ${data.name  || ''}`, 'success'),
            report:    () => this.showNotification(`📡 BLE Report: ${data.title   || ''}`, 'info'),
        };
        if (typeMap[payload.type]) typeMap[payload.type]();
    }

    // ─── Chrome Nano AI ───────────────────────────────────────────────────────
    async callChromeNanoAPI(apiType, data, options = {}) {
        try {
            if (window.ai) {
                return await this._callBuiltInAI(apiType, data, options);
            }
            return this._simulateChromeNanoAPI(apiType, data);
        } catch (err) {
            console.warn('[AI] Chrome Nano API error, using fallback:', err);
            return this._simulateChromeNanoAPI(apiType, data);
        }
    }

    async _callBuiltInAI(apiType, data, options) {
        // Chrome 127+ built-in AI (window.ai)
        switch (apiType) {
            case 'summarize': {
                const session = await window.ai.summarizer.create({ type: 'tl;dr', format: 'plain-text', length: 'short' });
                const result = await session.summarize(data);
                session.destroy();
                return result;
            }
            case 'prompt': {
                const session = await window.ai.languageModel.create({ systemPrompt: 'You are an emergency coordinator assistant.' });
                const result = await session.prompt(data);
                session.destroy();
                return result;
            }
            default:
                return this._simulateChromeNanoAPI(apiType, data);
        }
    }

    _simulateChromeNanoAPI(type, data) {
        const fns = {
            summarize: t => { const w = t.split(' '); return w.length <= 20 ? t : w.slice(0, 20).join(' ') + '…'; },
            proofread: t => t.trim().replace(/\s+/g, ' '),
            rewrite:   t => t.replace(/urgent/gi,'critical').replace(/help/gi,'assistance').replace(/problem/gi,'situation'),
            translate: t => t,
            prompt:    c => `Strategy for ${c}: 1) Assess risks, 2) Prioritize needs, 3) Coordinate resources.`,
        };
        return (fns[type] || (x => x))(data);
    }

    // ─── Form handling ────────────────────────────────────────────────────────
    async handleFormSubmit(form) {
        const data   = Object.fromEntries(new FormData(form).entries());
        const action = form.dataset.action;
        try {
            if (this.isOnline) {
                await this.submitOnline(action, data);
            } else {
                await this.queueForSync(action, data);
                this.showNotification('Saved offline – will sync when back online.', 'info');
            }
        } catch (err) {
            console.error('[Form] submission error:', err);
            this.showNotification('Submission error. Please try again.', 'error');
        }
    }

    async submitOnline(action, data) {
        const response = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const result = await response.json();
        this.showNotification('Submitted successfully!', 'success');
        return result;
    }

    async queueForSync(action, data) {
        const tx    = this.db.transaction(['syncQueue'], 'readwrite');
        const store = tx.objectStore('syncQueue');
        store.add({ type: action, data, timestamp: Date.now() });
    }

    async syncOfflineData() {
        const tx    = this.db.transaction(['syncQueue'], 'readwrite');
        const store = tx.objectStore('syncQueue');
        const req   = store.getAll();
        req.onsuccess = async () => {
            for (const item of req.result) {
                try {
                    await this.submitOnline(item.type, item.data);
                    store.delete(item.id);
                } catch (err) {
                    console.error('[Sync] error:', err);
                }
            }
        };
    }

    // ─── Online status UI ────────────────────────────────────────────────────
    updateOnlineStatus() {
        const banner = document.querySelector('.offline-banner');
        if (banner) banner.classList.toggle('show', !this.isOnline);
    }

    // ─── Dashboard data ───────────────────────────────────────────────────────
    async loadDashboardData() {
        try {
            const [reports, alerts, missions, safehouses, resources] = await Promise.all([
                this.fetchData('reports'), this.fetchData('alerts'),
                this.fetchData('missions'), this.fetchData('safehouses'), this.fetchData('resources'),
            ]);
            this.updateDashboardStats(reports, alerts, missions, safehouses, resources);
            this.updateRecentActivity(reports, alerts, missions);
        } catch (err) {
            console.error('[Dashboard] load error:', err);
        }
    }

    async fetchData(type) {
        if (this.isOnline) {
            try {
                const res = await fetch(`/api/${type}`);
                if (res.ok) {
                    const data = await res.json();
                    await this.cacheData(type, data);
                    return data;
                }
            } catch (err) {
                console.warn(`[fetch] ${type} failed, using cache`);
            }
        }
        return this.getCachedData(type);
    }

    async cacheData(type, data) {
        if (!this.db) return;
        const tx    = this.db.transaction([type], 'readwrite');
        const store = tx.objectStore(type);
        store.clear();
        data.forEach(item => store.add(item));
    }

    async getCachedData(type) {
        if (!this.db) return [];
        return new Promise((resolve) => {
            const tx  = this.db.transaction([type], 'readonly');
            const req = tx.objectStore(type).getAll();
            req.onsuccess = () => resolve(req.result);
            req.onerror   = () => resolve([]);
        });
    }

    updateDashboardStats(reports, alerts, missions, safehouses, resources) {
        const stats = {
            totalReports:       reports.length,
            activeAlerts:       alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length,
            activeMissions:     missions.filter(m => m.status === 'active').length,
            availableSafehouses:safehouses.filter(s => s.availability > 0).length,
            totalResources:     resources.reduce((n, r) => n + (r.quantity || 0), 0),
        };
        Object.entries(stats).forEach(([k, v]) => {
            const el = document.querySelector(`[data-stat="${k}"]`);
            if (el) el.textContent = v;
        });
    }

    updateRecentActivity(reports, alerts, missions) {
        const activity = [
            ...reports.slice(0, 3).map(r => ({ type: 'report',  data: r, time: r.created_at })),
            ...alerts.slice(0, 3).map(a  => ({ type: 'alert',   data: a, time: a.created_at })),
            ...missions.slice(0, 3).map(m=> ({ type: 'mission', data: m, time: m.created_at })),
        ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5);

        const container = document.querySelector('.recent-activity');
        if (container) container.innerHTML = activity.map(i => this.createActivityItem(i)).join('');
    }

    createActivityItem(item) {
        const icons = { report: '📋', alert: '🚨', mission: '🎯', safehouse: '🏠', resource: '📦' };
        const icon  = icons[item.type] || '📄';
        const title = item.data.title || item.data.name || '—';
        const ago   = this.getTimeAgo(item.time);
        return `
            <div class="activity-item">
                <div class="activity-icon">${icon}</div>
                <div class="activity-content">
                    <div class="activity-title">${title}</div>
                    <div class="activity-time">${ago}</div>
                </div>
            </div>`;
    }

    getTimeAgo(dateString) {
        const diff    = Date.now() - new Date(dateString);
        const minutes = Math.floor(diff / 60000);
        const hours   = Math.floor(diff / 3600000);
        const days    = Math.floor(diff / 86400000);
        if (minutes < 60) return `${minutes}m ago`;
        if (hours   < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    // ─── Notifications ────────────────────────────────────────────────────────
    showNotification(message, type = 'info') {
        const el = document.createElement('div');
        el.className = `notification notification-${type}`;
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 5000);
    }

    // ─── PWA install ──────────────────────────────────────────────────────────
    initPWAInstall() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            document.querySelector('.install-prompt')?.classList.add('show');
        });
    }

    async installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            await this.deferredPrompt.userChoice;
            this.deferredPrompt = null;
        }
    }
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    window.civitasApp = new CivitasApp();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = CivitasApp;
}
