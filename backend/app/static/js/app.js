const searchInput = document.getElementById('station-search');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');

const API_URL = 'http://localhost:8000/status';

async function searchStation(stationName) {
    resultsContainer.innerHTML = `<div class="text-center py-3">Cargando...</div>`;
    try {
        const res = await fetch(`${API_URL}?station=${encodeURIComponent(stationName)}`);
        if (!res.ok) throw new Error('Error en la respuesta del servidor');
        const data = await res.json();
        displayResults(data);
    } catch (err) {
        resultsContainer.innerHTML = `
            <div class="alert alert-danger" role="alert">
                Error al obtener datos. ${err.message}
            </div>`;
    }
}

function displayResults(data) {
    if (!data || (Array.isArray(data) && data.length === 0)) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                No se encontraron estaciones.
            </div>`;
        return;
    }

    const items = (Array.isArray(data) ? data : [data]).map(st => `
        <div class="card mb-2">
            <div class="card-body">
                <h6 class="card-title mb-1">${st.name || st.station || 'Sin nombre'}</h6>
                <p class="mb-1"><strong>Líneas:</strong> ${st.lines ? st.lines.join(', ') : (st.line || 'N/D')}</p>
                <p class="mb-0"><strong>Estado:</strong> ${st.status || 'N/D'}</p>
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