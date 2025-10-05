// Civitas Service Worker - Offline-First PWA
const CACHE_NAME = 'civitas-v1';
const STATIC_CACHE = 'civitas-static-v1';
const DYNAMIC_CACHE = 'civitas-dynamic-v1';

// Files to cache for offline use
const STATIC_FILES = [
    '/',
    '/static/style.css',
    '/static/app.js',
    '/templates/base.html',
    '/templates/login.html',
    '/templates/dashboard.html',
    '/templates/reports.html',
    '/templates/alerts.html',
    '/templates/missions.html',
    '/templates/distribution.html',
    '/templates/analytics.html',
    '/templates/safehouses.html'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/reports',
    '/api/alerts',
    '/api/missions',
    '/api/safehouses',
    '/api/resources'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Error caching static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleAPIRequest(request));
        return;
    }

    // Handle static file requests
    if (request.method === 'GET') {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle other requests normally
    event.respondWith(fetch(request));
});

// Handle API requests with offline fallback
async function handleAPIRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache successful responses
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
        
        throw new Error('Network response not ok');
    } catch (error) {
        console.log('Network failed, trying cache:', request.url);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API endpoints
        if (request.url.includes('/api/')) {
            return new Response(
                JSON.stringify({ 
                    error: 'Offline', 
                    message: 'This data is not available offline' 
                }),
                {
                    status: 503,
                    statusText: 'Service Unavailable',
                    headers: { 'Content-Type': 'application/json' }
                }
            );
        }
        
        // Return offline page for other requests
        return caches.match('/offline.html');
    }
}

// Handle static file requests
async function handleStaticRequest(request) {
    try {
        // Try cache first for static files
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // If not in cache, try network
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache the response
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Both cache and network failed for:', request.url);
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline.html');
        }
        
        // Return a generic offline response
        return new Response('Offline', { status: 503 });
    }
}

// Background sync for offline data
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'civitas-sync') {
        event.waitUntil(syncOfflineData());
    }
});

// Sync offline data when back online
async function syncOfflineData() {
    try {
        // This would sync data from IndexedDB to the server
        // Implementation depends on the specific sync strategy
        console.log('Syncing offline data...');
        
        // Notify the main thread that sync is complete
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_COMPLETE',
                timestamp: Date.now()
            });
        });
    } catch (error) {
        console.error('Error syncing offline data:', error);
    }
}

// Push notifications for alerts
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: 'New emergency alert received',
        icon: '/static/icon-192.png',
        badge: '/static/badge-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/alerts'
        },
        actions: [
            {
                action: 'view',
                title: 'View Alert',
                icon: '/static/icon-view.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icon-dismiss.png'
            }
        ]
    };
    
    if (event.data) {
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data = { ...options.data, ...data };
    }
    
    event.waitUntil(
        self.registration.showNotification('Civitas Alert', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(cacheURLs(event.data.urls));
    }
});

// Cache specific URLs
async function cacheURLs(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    return Promise.all(
        urls.map(url => {
            return fetch(url)
                .then(response => {
                    if (response.ok) {
                        return cache.put(url, response);
                    }
                })
                .catch(error => {
                    console.error('Error caching URL:', url, error);
                });
        })
    );
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'civitas-periodic-sync') {
        event.waitUntil(performPeriodicSync());
    }
});

// Perform periodic sync
async function performPeriodicSync() {
    try {
        console.log('Performing periodic sync...');
        
        // Sync critical data periodically
        const criticalEndpoints = ['/api/alerts', '/api/missions'];
        
        for (const endpoint of criticalEndpoints) {
            try {
                const response = await fetch(endpoint);
                if (response.ok) {
                    const cache = await caches.open(DYNAMIC_CACHE);
                    await cache.put(endpoint, response);
                }
            } catch (error) {
                console.error(`Error syncing ${endpoint}:`, error);
            }
        }
    } catch (error) {
        console.error('Error in periodic sync:', error);
    }
}

// Handle BLE mesh data sync
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'BLE_SYNC') {
        event.waitUntil(handleBLESync(event.data.data));
    }
});

// Handle BLE mesh data synchronization
async function handleBLESync(data) {
    try {
        console.log('Handling BLE sync data:', data);
        
        // Store BLE data in cache for offline access
        const cache = await caches.open(DYNAMIC_CACHE);
        
        // Create a response for the BLE data
        const response = new Response(JSON.stringify(data), {
            headers: { 'Content-Type': 'application/json' }
        });
        
        // Cache the BLE data
        await cache.put(`/api/ble/${data.type}`, response);
        
        // Notify main thread
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'BLE_DATA_SYNCED',
                data: data
            });
        });
    } catch (error) {
        console.error('Error handling BLE sync:', error);
    }
}

console.log('Civitas Service Worker loaded successfully');

