const API_URL = 'http://127.0.0.1:5000';
const apiKey = localStorage.getItem('apiKey');
const username = localStorage.getItem('username');
const userId = localStorage.getItem('userId');

if (!apiKey) window.location.href = '/login';
document.getElementById('userDisplay').textContent = username;

let map;
let selectionStep = 0; 
let startPoint = null; 
let endPoint = null;
let startMarker = null;
let endMarker = null;
let routeLayer = null; 
let currentRouteGeometry = null;

// --- INITIALIZATION ---
function initMap() {
    // Centered on Corfu
    map = L.map('map').setView([39.6243, 19.9217], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    map.on('click', (e) => handlePointSelection(e.latlng, 'manual'));
}

async function authFetch(endpoint, options = {}) {
    if (!options.headers) options.headers = {};
    options.headers['X-API-KEY'] = apiKey;
    options.headers['Content-Type'] = 'application/json';
    
    const res = await fetch(`${API_URL}${endpoint}`, options);
    if (res.status === 401 || res.status === 403) {
        alert("Session expired");
        window.location.href = '/login';
    }
    return res;
}

// --- CORE LOGIC ---

// 1. Load POIs
async function loadPOIs() {
    try {
        const res = await authFetch('/pois');
        if (!res.ok) throw new Error('Failed to load POIs');
        const data = await res.json();
        const pois = data.results || [];

        pois.forEach(poi => {
            console.log(`POI: ${poi.name}`, poi.location);
            if (poi.location && poi.location.lat && poi.location.lon) {
                const marker = L.marker([poi.location.lat, poi.location.lon]).addTo(map);
                marker.bindPopup(`<b>${poi.name}</b><br>${poi.description || ''}`);
                
                // Pass 'name' so we can save it in poi_sequence later
                marker.on('click', () => {
                    handlePointSelection(
                        { lat: poi.location.lat, lng: poi.location.lon }, 
                        'poi', 
                        poi.id, 
                        poi.name
                    );
                });
            }
        });
    } catch (err) {
        console.error("Error loading POIs:", err);
    }
}

// 2. Handle Selection
function handlePointSelection(latlng, type, id = null, name = null) {
    if (selectionStep === 2) return; 

    // Default name if manual click
    if (!name) name = (selectionStep === 0) ? "Start Point" : "End Point";

    const pointData = { lat: latlng.lat, lng: latlng.lng, id: id, name: name };

    if (selectionStep === 0) {
        startPoint = pointData;
        startMarker = L.marker(latlng).addTo(map).bindTooltip("Start", {permanent:true}).openTooltip();
        document.getElementById('statusMsg').textContent = "Select End Point...";
        selectionStep = 1;
    } else if (selectionStep === 1) {
        endPoint = pointData;
        endMarker = L.marker(latlng).addTo(map).bindTooltip("End", {permanent:true}).openTooltip();
        document.getElementById('statusMsg').textContent = "Ready to Calculate.";
        document.getElementById('calcRouteBtn').disabled = false;
        selectionStep = 2;
    }
}

// 3. Calculate Route (Updated with Vehicle)
document.getElementById('calcRouteBtn').addEventListener('click', async () => {
    if (!startPoint || !endPoint) return;

    const vehicle = document.getElementById('vehicleType').value;

    // Prepare payload for backend
    const payload = {
        locations: [
            [startPoint.lng, startPoint.lat], 
            [endPoint.lng, endPoint.lat]
        ],
        vehicle: vehicle
    };

    console.log("Calculating route for:", vehicle);

    try {
        const res = await authFetch('/routes/compute', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            const data = await res.json();
            currentRouteGeometry = data.geometry; 
            
            if (routeLayer) map.removeLayer(routeLayer);
            
            routeLayer = L.geoJSON(currentRouteGeometry, {
                style: { color: 'blue', weight: 5 }
            }).addTo(map);
            
            map.fitBounds(routeLayer.getBounds());
            document.getElementById('statusMsg').textContent = "Route Calculated.";
            document.getElementById('saveRouteBtn').disabled = false;
        } else {
            const err = await res.json();
            alert("Error: " + (err.message || "Route calculation failed"));
        }
    } catch (err) {
        console.error(err);
        alert("Network error.");
    }
});

// 4. Save Route (Updated for DB Schema)
document.getElementById('saveRouteBtn').addEventListener('click', async () => {
    // 1. Get Name
    const routeName = prompt("Enter a name for this route:");
    if (!routeName) return;

    // 2. Get Publicity
    const isPublic = confirm("Should this route be PUBLIC?\n\nOK = Yes\nCancel = No");

    // 3. Get Vehicle
    const vehicle = document.getElementById('vehicleType').value;

    // 4. Get User ID (ΝΕΟ)
    const currentUserId = localStorage.getItem('userId');

    // 5. Construct POI Sequence
    const poiSequence = [
        { 
            "poiId": startPoint.id || "manual_start", 
            "name": startPoint.name 
        },
        { 
            "poiId": endPoint.id || "manual_end", 
            "name": endPoint.name 
        }
    ];

    const payload = {
        "name": routeName,
        "public": isPublic,
        "vehicle": vehicle,
        "poiSequence": poiSequence,
        "geometry": currentRouteGeometry,
        "ownerId": currentUserId  // <--- ΕΔΩ ΠΡΟΣΘΕΤΟΥΜΕ ΤΟ ID
    };

    console.log("Saving payload:", payload); // Για να δεις τι στέλνεις στην κονσόλα

    try {
        const res = await authFetch('/routes', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("Route saved successfully!");
            loadSavedRoutes(); 
        } else {
            const err = await res.json();
            alert("Failed to save: " + (err.message || "Unknown error"));
        }
    } catch (err) {
        console.error(err);
        alert("Error saving route.");
    }
});

// 5. Clear Map
document.getElementById('clearRouteBtn').addEventListener('click', () => {
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    if (routeLayer) map.removeLayer(routeLayer);
    
    startPoint = null; endPoint = null;
    startMarker = null; endMarker = null;
    routeLayer = null; currentRouteGeometry = null;
    selectionStep = 0;
    
    document.getElementById('calcRouteBtn').disabled = true;
    document.getElementById('saveRouteBtn').disabled = true;
    document.getElementById('statusMsg').textContent = "Select Start Point...";
});

// 6. Manage Saved Routes
async function loadSavedRoutes() {
    const container = document.getElementById('savedRoutesList');
    container.innerHTML = "Loading...";

    try {
        const res = await authFetch('/routes');
        const data = await res.json();
        const routes = data.results || [];
        
        container.innerHTML = "";
        if (routes.length === 0) {
            container.innerHTML = "<small>No saved routes.</small>";
            return;
        }

        routes.forEach(route => {
            const div = document.createElement('div');
            div.className = 'route-item';
            
            const span = document.createElement('span');
            // Display Name and Vehicle type
            span.innerHTML = `<b>${route.name}</b> <small>(${route.vehicle || 'car'})</small>`;
            span.onclick = () => {
                if (routeLayer) map.removeLayer(routeLayer);
                routeLayer = L.geoJSON(route.geometry, { style: { color: 'green', weight: 5 } }).addTo(map);
                map.fitBounds(routeLayer.getBounds());
                document.getElementById('statusMsg').textContent = `Viewing: ${route.name}`;
            };

            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.textContent = 'X';
            delBtn.onclick = async (e) => {
                e.stopPropagation(); 
                if(confirm('Delete this route?')) {
                    await authFetch(`/routes/${route.id}`, { method: 'DELETE' });
                    loadSavedRoutes();
                }
            };

            div.appendChild(span);
            div.appendChild(delBtn);
            container.appendChild(div);
        });

    } catch (err) {
        console.error(err);
        container.textContent = "Error loading routes.";
    }
}

// 7. Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('apiKey');
    localStorage.removeItem('username');
    window.location.href = '/login';
});

// --- STARTUP ---
initMap();
loadPOIs();
loadSavedRoutes();