// Berlin Transport Live - Station Departures Page

let autoRefreshInterval;
const AUTO_REFRESH_SECONDS = 30;

document.addEventListener('DOMContentLoaded', () => {
    loadDepartures();
    setupControls();
    startAutoRefresh();
});

// Load departures for the station
async function loadDepartures() {
    const duration = document.getElementById('durationSelect').value;
    const container = document.getElementById('departuresContainer');
    
    container.innerHTML = '<div class="loading">Loading departures...</div>';
    
    try {
        const response = await fetch(`/api/departures/${STATION_ID}?duration=${duration}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayDepartures(data);
        updateStationInfo(data.station);
        
    } catch (error) {
        console.error('Failed to load departures:', error);
        container.innerHTML = '<div class="error">Failed to load departures. Please try again.</div>';
    }
}

// Update station info in header
function updateStationInfo(station) {
    document.getElementById('stationName').textContent = station.name;
    document.getElementById('stationId').textContent = `Station ID: ${station.id}`;
}

// Display departures table
function displayDepartures(data) {
    const container = document.getElementById('departuresContainer');
    
    if (!data.departures || data.departures.length === 0) {
        container.innerHTML = '<div class="loading">No departures found for this time period</div>';
        return;
    }
    
    // Update last update time
    if (data.realtimeDataUpdatedAt) {
        const updateTime = new Date(data.realtimeDataUpdatedAt);
        document.getElementById('lastUpdate').textContent = 
            `Last updated: ${updateTime.toLocaleString()}`;
    }
    
    // Create departures table
    const table = document.createElement('table');
    table.className = 'departures-table';
    
    table.innerHTML = `
        <thead>
            <tr>
                <th>Line</th>
                <th>Direction</th>
                <th>Departure</th>
                <th>Delay</th>
                <th>Platform</th>
            </tr>
        </thead>
        <tbody>
            ${data.departures.map(dep => createDepartureRow(dep)).join('')}
        </tbody>
    `;
    
    container.innerHTML = '';
    container.appendChild(table);
}

// Create a departure row
function createDepartureRow(departure) {
    const departureTime = new Date(departure.when);
    const now = new Date();
    const minutesUntil = Math.floor((departureTime - now) / 60000);
    
    const delayMinutes = departure.delay ? Math.floor(departure.delay / 60) : 0;
    const delayClass = delayMinutes > 0 ? 'delay' : 'on-time';
    const delayText = delayMinutes > 0 ? `+${delayMinutes} min` : 'On time';
    
    const lineType = getLineType(departure.line.type);
    
    return `
        <tr>
            <td>
                <span class="line-badge ${lineType}">
                    ${departure.line.name}
                </span>
            </td>
            <td>${departure.direction}</td>
            <td>
                <strong>${minutesUntil >= 0 ? minutesUntil : 0} min</strong>
                <br>
                <small>${departureTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</small>
            </td>
            <td class="${delayClass}">${delayText}</td>
            <td>${departure.platform || '-'}</td>
        </tr>
    `;
}

// Determine line type for styling
function getLineType(type) {
    const typeMap = {
        'bus': 'bus',
        'tram': 'tram',
        'subway': 'subway',
        'u-bahn': 'subway',
        'train': 'train',
        's-bahn': 'train',
        'regional': 'train',
        'ferry': 'ferry'
    };
    
    const normalized = type.toLowerCase();
    return typeMap[normalized] || 'bus';
}

// Setup controls
function setupControls() {
    // Duration selector
    document.getElementById('durationSelect').addEventListener('change', () => {
        loadDepartures();
        restartAutoRefresh();
    });
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadDepartures();
        restartAutoRefresh();
    });
}

// Auto-refresh functionality
function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        loadDepartures();
    }, AUTO_REFRESH_SECONDS * 1000);
}

function restartAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    startAutoRefresh();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
