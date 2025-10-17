// Berlin Transport Live - Main Application JavaScript

// Initialize map
let map;
let markers = [];

document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    loadFeaturedStations();
    setupSearchHandlers();
});

// Initialize Leaflet map centered on Berlin
function initializeMap() {
    map = L.map('map').setView([52.5200, 13.4050], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
}

// Load featured stations
async function loadFeaturedStations() {
    try {
        const response = await fetch('/api/stations/featured');
        const data = await response.json();
        
        const container = document.getElementById('featuredStations');
        container.innerHTML = '';
        
        data.stations.forEach(station => {
            const card = createStationCard(station);
            container.appendChild(card);
            
            // Add marker if location available
            if (station.location) {
                addMarkerToMap(station);
            }
        });
    } catch (error) {
        console.error('Failed to load featured stations:', error);
        document.getElementById('featuredStations').innerHTML = 
            '<div class="error">Failed to load featured stations</div>';
    }
}

// Create station card element
function createStationCard(station) {
    const card = document.createElement('a');
    card.href = `/station/${station.id}`;
    card.className = 'station-card';
    
    card.innerHTML = `
        <h3>${station.name}</h3>
        <span class="badge">${formatStationType(station.type)}</span>
    `;
    
    return card;
}

// Format station type for display
function formatStationType(type) {
    const types = {
        'major_hub': 'Major Hub',
        'regional_hub': 'Regional Hub',
        'stop': 'Stop',
        'station': 'Station'
    };
    return types[type] || type;
}

// Add marker to map
function addMarkerToMap(station) {
    if (!station.location) return;
    
    const marker = L.marker([station.location.latitude, station.location.longitude])
        .addTo(map)
        .bindPopup(`
            <strong>${station.name}</strong><br>
            <a href="/station/${station.id}">View Departures</a>
        `);
    
    markers.push(marker);
}

// Setup search handlers
function setupSearchHandlers() {
    const searchInput = document.getElementById('stationSearch');
    const searchBtn = document.getElementById('searchBtn');
    const resultsContainer = document.getElementById('searchResults');
    
    let searchTimeout;
    
    // Search on input with debounce
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => performSearch(query), 300);
    });
    
    // Search on button click
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            performSearch(query);
        }
    });
    
    // Search on Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query.length >= 2) {
                performSearch(query);
            }
        }
    });
}

// Perform station search
async function performSearch(query) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
    
    try {
        const response = await fetch(`/api/stations/search?q=${encodeURIComponent(query)}&limit=10`);
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        displaySearchResults(data.stations);
        
        // Clear existing markers and add new ones
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
        
        data.stations.forEach(station => {
            if (station.location) {
                addMarkerToMap(station);
            }
        });
        
        // Fit map to show all markers
        if (markers.length > 0) {
            const group = L.featureGroup(markers);
            map.fitBounds(group.getBounds().pad(0.1));
        }
        
    } catch (error) {
        console.error('Search error:', error);
        resultsContainer.innerHTML = '<div class="error">Search failed. Please try again.</div>';
    }
}

// Display search results
function displaySearchResults(stations) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (stations.length === 0) {
        resultsContainer.innerHTML = '<div class="loading">No stations found</div>';
        return;
    }
    
    resultsContainer.innerHTML = '';
    
    stations.forEach(station => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.onclick = () => window.location.href = `/station/${station.id}`;
        
        item.innerHTML = `
            <h3>${station.name}</h3>
            <p class="station-type">${formatStationType(station.type)}</p>
        `;
        
        resultsContainer.appendChild(item);
    });
}
