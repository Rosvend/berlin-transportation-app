const searchInput = document.getElementById('station-search');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');

const API_URL = 'http://localhost:8000/api';

async function searchStation(stationName) {
    resultsContainer.innerHTML = `<div class="text-center py-3"><i class="fas fa-spinner fa-spin"></i> Buscando estaciones...</div>`;
    try {
        const res = await fetch(`${API_URL}/stations/search?q=${encodeURIComponent(stationName)}`);
        if (!res.ok) throw new Error('Error en la respuesta del servidor');
        const data = await res.json();
        console.log('Datos recibidos:', data); // Para depuración
        displayResults(data);
    } catch (err) {
        console.error('Error:', err); // Para depuración
        resultsContainer.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle"></i> Error al obtener datos: ${err.message}
            </div>`;
    }
}

function displayResults(data) {
    if (!data || (Array.isArray(data) && data.length === 0)) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle"></i> No se encontraron estaciones con ese nombre.
            </div>`;
        return;
    }

    const stations = data.stations || [];
    if (stations.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-info-circle"></i> No se encontraron estaciones con ese nombre.
            </div>`;
        return;
    }

    const items = stations.map(station => `
        <div class="card mb-3 station-card">
            <div class="card-body">
                <h5 class="card-title">
                    <i class="fas fa-subway"></i> ${station.name || 'Sin nombre'}
                </h5>
                <div class="station-details">
                    <p class="mb-2">
                        <span class="badge bg-primary">
                            <i class="fas fa-${station.type === 'major_hub' ? 'star' : 
                                              station.type === 'regional_hub' ? 'building' : 
                                              'train'}"></i>
                            ${station.type === 'major_hub' ? 'Estación Principal' : 
                              station.type === 'regional_hub' ? 'Estación Regional' : 
                              'Estación'}
                        </span>
                    </p>
                    ${station.location ? `
                        <p class="mb-2 text-muted small">
                            <i class="fas fa-location-dot"></i> 
                            Lat: ${station.location.latitude.toFixed(4)}, 
                            Lon: ${station.location.longitude.toFixed(4)}
                        </p>
                        <div class="station-actions mt-3">
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="showDepartures('${station.id}')">
                                <i class="fas fa-clock"></i> Ver Horarios
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="showOnMap(${station.location.latitude}, ${station.location.longitude})">
                                <i class="fas fa-map-marker-alt"></i> Ver en Mapa
                            </button>
                        </div>
                    ` :  
                        `<p class="mb-2 text-muted">
                            <i class="fas fa-location-dot"></i> Ubicación: 
                            ${station.location.latitude.toFixed(4)}, ${station.location.longitude.toFixed(4)}
                        </p>` : 
                        ''}
                </div>
            </div>
        </div>
    `).join('');
    resultsContainer.innerHTML = items;
}

// Polling cada 30s
let pollingId = null;
function startPolling() {
    if (pollingId) clearInterval(pollingId);
    pollingId = setInterval(() => {
        const q = searchInput.value.trim();
        if (q) searchStation(q);
    }, 30000);
}

// Event Listeners
searchButton.addEventListener('click', () => {
    const q = searchInput.value.trim();
    if (q) {
        searchStation(q);
        startPolling();
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const q = searchInput.value.trim();
        if (q) {
            searchStation(q);
            startPolling();
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    if (searchInput && searchInput.value.trim()) startPolling();
});

 

// Map initialization
let map = null;
let markers = [];

function initMap() {
    // Berlin coordinates
    const berlin = [52.52, 13.405];
    
    map = L.map('map').setView(berlin, 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Update existing displayResults function to show markers
const originalDisplayResults = displayResults;
displayResults = function(data) {
    // Clear existing markers
    if (markers.length) {
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
    }

    // Call original display function
    originalDisplayResults(data);

    // Add markers for each station
    if (data && Array.isArray(data)) {
        data.forEach(st => {
            if (st.latitude && st.longitude) {
                const marker = L.marker([st.latitude, st.longitude])
                    .bindPopup(`<b>${st.name}</b><br>Lines: ${st.lines?.join(', ') || st.line || 'N/D'}`)
                    .addTo(map);
                markers.push(marker);
            }
        });
    }
};

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    // ...existing polling code will run after this
});