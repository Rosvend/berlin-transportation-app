// Configuración global
const API_URL = 'http://localhost:8000/api';
let map = null;
let markers = [];
let vehicleMarkers = [];
let radarUpdateInterval = null;
let isRadarActive = false;

// Funciones para manejar favoritos
function getFavorites() {
    const favorites = localStorage.getItem('favoriteStations');
    return favorites ? JSON.parse(favorites) : [];
}

function saveFavorites(favorites) {
    localStorage.setItem('favoriteStations', JSON.stringify(favorites));
}

function addFavorite(station) {
    const favorites = getFavorites();
    // Verificar si ya existe
    if (!favorites.find(fav => fav.id === station.id)) {
        favorites.push({
            id: station.id,
            name: station.name,
            latitude: station.latitude,
            longitude: station.longitude
        });
        saveFavorites(favorites);
        return true;
    }
    return false;
}

function removeFavorite(stationId) {
    const favorites = getFavorites();
    const filtered = favorites.filter(fav => fav.id !== stationId);
    saveFavorites(filtered);
}

function isFavorite(stationId) {
    const favorites = getFavorites();
    return favorites.some(fav => fav.id === stationId);
}

// Funciones para historial de búsquedas
function getSearchHistory() {
    const history = localStorage.getItem('searchHistory');
    return history ? JSON.parse(history) : [];
}

function addToSearchHistory(query) {
    if (!query || query.trim().length < 2) return;
    
    const history = getSearchHistory();
    // Remover duplicados y agregar al inicio
    const filtered = history.filter(item => item.toLowerCase() !== query.toLowerCase());
    filtered.unshift(query);
    
    // Mantener solo los últimos 10
    const limited = filtered.slice(0, 10);
    localStorage.setItem('searchHistory', JSON.stringify(limited));
}

function clearSearchHistory() {
    localStorage.removeItem('searchHistory');
}

// Utility function: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Función para inicializar el mapa
function initMap() {
    try {
        // Coordenadas de Berlín
        const berlin = [52.52, 13.405];
        map = L.map('map').setView(berlin, 12);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Forzar recalculo de tamaño (evita render vacío en algunos casos)
        setTimeout(() => {
            try { map.invalidateSize(); } catch (e) { /* ignore */ }
        }, 200);

        console.log('Mapa inicializado correctamente');
    } catch (error) {
        console.error('Error al inicializar el mapa:', error);
    }
}

// Funciones para el manejo del mapa
function clearMapMarkers() {
    if (markers && markers.length > 0) {
        markers.forEach(marker => {
            if (map && marker) {
                map.removeLayer(marker);
            }
        });
        markers = [];
    }
}

// Crear íconos personalizados para diferentes tipos de transporte
const transportIcons = {
    station: L.divIcon({
        html: '<i class="fas fa-map-marker-alt fa-2x" style="color: #2D3047;"></i>',
        iconSize: [30, 30],
        className: 'custom-icon'
    }),
    subway: L.divIcon({
        html: '<i class="fas fa-subway fa-2x" style="color: #0066cc;"></i>',
        iconSize: [30, 30],
        className: 'custom-icon'
    }),
    train: L.divIcon({
        html: '<i class="fas fa-train fa-2x" style="color: #dc3545;"></i>',
        iconSize: [30, 30],
        className: 'custom-icon'
    }),
    bus: L.divIcon({
        html: '<i class="fas fa-bus fa-2x" style="color: #ffc107;"></i>',
        iconSize: [30, 30],
        className: 'custom-icon'
    }),
    tram: L.divIcon({
        html: '<i class="fas fa-train-tram fa-2x" style="color: #28a745;"></i>',
        iconSize: [30, 30],
        className: 'custom-icon'
    })
};

function addMarkerToMap(station) {
    if (map && station.latitude && station.longitude) {
        // Determinar el ícono basado en el tipo de estación o productos disponibles
        let icon = transportIcons.station;
        
        // Si la estación tiene información de productos, usar ícono específico
        if (station.products) {
            if (station.products.subway) icon = transportIcons.subway;
            else if (station.products.train || station.products.regional) icon = transportIcons.train;
            else if (station.products.tram) icon = transportIcons.tram;
            else if (station.products.bus) icon = transportIcons.bus;
        }
        
        const marker = L.marker([station.latitude, station.longitude], { icon: icon })
            .bindPopup(`
                <div style="text-align: center;">
                    <strong>${station.name}</strong><br>
                    <small>Haz clic en "Horarios" para más información</small>
                </div>
            `)
            .addTo(map);
        
        markers.push(marker);
        return marker;
    }
    return null;
}

function showOnMap(lat, lng, stationName) {
    if (map && lat && lng) {
        // Centrar y hacer zoom en la estación
        map.setView([lat, lng], 15);
        
        // Abrir el popup del marcador correspondiente
        markers.forEach(marker => {
            const markerLatLng = marker.getLatLng();
            if (Math.abs(markerLatLng.lat - lat) < 0.0001 && Math.abs(markerLatLng.lng - lng) < 0.0001) {
                marker.openPopup();
            }
        });
        
        // Hacer scroll suave hasta el mapa
        const mapElement = document.getElementById('map');
        if (mapElement) {
            mapElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }
}

// Función para mostrar mensajes
function showMessage(container, message, type = 'info') {
    const iconMap = {
        'info': 'fa-info-circle',
        'warning': 'fa-exclamation-triangle',
        'success': 'fa-check-circle',
        'danger': 'fa-times-circle'
    };
    
    container.innerHTML = `
        <div class="alert alert-${type} fade show" role="alert">
            <i class="fas ${iconMap[type]}"></i> ${message}
        </div>`;
    
    // Auto-hide después de 3 segundos
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (container.querySelector('.alert') === alert) {
                    container.innerHTML = '';
                }
            }, 150);
        }
    }, 3000);
}

// Función para buscar estaciones
async function searchStation(stationName) {
    const resultsContainer = document.getElementById('results-container');
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    console.log('Buscando estación:', stationName);

    if (!resultsContainer) {
        console.error('No se encontró el contenedor de resultados');
        return;
    }
    
    // Si no hay término de búsqueda, obtenerlo del input
    if (!stationName) {
        stationName = searchInput ? searchInput.value.trim() : '';
    }
    
    if (!stationName || stationName.length < 2) {
        console.log('Búsqueda demasiado corta, ignorando');
        return;
    }

    // Deshabilitar botón de búsqueda y cambiar icono
    if (searchButton) {
        searchButton.disabled = true;
        searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
    }

    resultsContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-3 text-muted">Buscando estaciones...</p>
        </div>`;

    try {
        const url = `${API_URL}/stations/search?q=${encodeURIComponent(stationName)}&results=15`;
        console.log('Realizando petición a:', url);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        // El backend devuelve { stations: [...], query: "..." }
        let stations = [];
        
        if (Array.isArray(data)) {
            stations = data;
        } else if (data && Array.isArray(data.stations)) {
            stations = data.stations;
            console.log(`Extraídas ${stations.length} estaciones del objeto`);
        }
        
        // Procesar coordenadas si vienen en location
        stations = stations.map(station => {
            if (station && station.location) {
                return {
                    ...station,
                    latitude: station.location.latitude,
                    longitude: station.location.longitude
                };
            }
            return station;
        });
        
        console.log('Estaciones procesadas:', stations);
        
        // ========== FEATURE #5: Add to search history ==========
        if (stations.length > 0) {
            addToSearchHistory(stationName);
            hideSearchHistory();
        }
        
        displayResults(stations);
        
    } catch (error) {
        console.error('Error en la búsqueda:', error);
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                <strong>Error:</strong> ${error.message}
                <br><small>Verifica que el backend esté corriendo en http://localhost:8000</small>
            </div>`;
    } finally {
        // Rehabilitar botón de búsqueda
        if (searchButton) {
            searchButton.disabled = false;
            searchButton.innerHTML = '<i class="fas fa-search"></i> Buscar';
        }
    }
}

// Función para mostrar resultados
function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    const stations = Array.isArray(data) ? data : (data.stations || []);

    if (!stations.length) {
        resultsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-search"></i> 
                <strong>No se encontraron estaciones.</strong>
                <p class="mb-0 mt-2">Intenta con otro nombre o verifica la ortografía.</p>
            </div>`;
        clearMapMarkers();
        return;
    }

    // Limpiar marcadores existentes
    clearMapMarkers();

    console.log('Mostrando estaciones:', stations.length);

    let hasMapCoordinates = false;
    let firstCoordinates = null;

    const stationsHTML = stations.map((station, index) => {
        // Agregar marcador al mapa SOLO si hay coordenadas
        if (station.latitude && station.longitude) {
            console.log('Agregando marcador para:', station.name, station.latitude, station.longitude);
            addMarkerToMap(station);
            hasMapCoordinates = true;
            if (!firstCoordinates) {
                firstCoordinates = { lat: station.latitude, lng: station.longitude };
            }
        } else {
            console.warn('Estación sin coordenadas (no se agrega al mapa):', station.name);
        }

        return `
            <div class="card mb-2 station-card animate-fade-in" data-station-id="${station.id}" style="animation-delay: ${index * 0.05}s;">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                <i class="fas fa-subway text-primary"></i> 
                                <strong>${station.name || 'Sin nombre'}</strong>
                            </h6>
                            ${station.id ? `<small class="text-muted">ID: ${station.id}</small>` : ''}
                            ${!station.latitude || !station.longitude ? 
                                '<br><small class="text-warning"><i class="fas fa-exclamation-circle"></i> Sin ubicación en mapa</small>' : 
                                ''}
                        </div>
                        <button class="btn btn-sm ${isFavorite(station.id) ? 'btn-warning' : 'btn-outline-warning'} favorite-btn" 
                                onclick='toggleFavorite(${JSON.stringify(station)})'
                                title="${isFavorite(station.id) ? 'Quitar de favoritos' : 'Agregar a favoritos'}">
                            <i class="${isFavorite(station.id) ? 'fas' : 'far'} fa-star"></i>
                        </button>
                    </div>
                    <div class="mt-2 d-flex gap-2 flex-wrap">
                        <button class="btn btn-sm btn-primary" 
                                onclick="showDepartures('${station.id}', '${escapeHtml(station.name)}', ${station.latitude || 'null'}, ${station.longitude || 'null'})"
                                title="Ver próximas salidas de trenes, buses y tranvías">
                            <i class="fas fa-clock"></i> Horarios
                        </button>
                        ${station.latitude && station.longitude ? `
                            <button class="btn btn-sm btn-outline-secondary" 
                                    onclick="showOnMap(${station.latitude}, ${station.longitude}, '${escapeHtml(station.name)}')"
                                    title="Mostrar ubicación en el mapa y hacer zoom">
                                <i class="fas fa-map-marker-alt"></i> Ver en Mapa
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>`;
    }).join('');

    resultsContainer.innerHTML = `
        <div class="mb-2">
            <small class="text-muted">
                <i class="fas fa-info-circle"></i> 
                Se encontraron ${stations.length} estación${stations.length !== 1 ? 'es' : ''}
                ${hasMapCoordinates ? '' : ' (sin ubicaciones en mapa)'}
            </small>
        </div>
        ${stationsHTML}`;
    
    // Centrar mapa en las estaciones encontradas que tengan coordenadas
    if (firstCoordinates) {
        console.log('Centrando mapa en:', firstCoordinates.lat, firstCoordinates.lng);
        map.setView([firstCoordinates.lat, firstCoordinates.lng], 13);
    }
}

// Función auxiliar para escapar HTML
function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/'/g, "\\'");
}


// Función para mostrar salidas
async function showDepartures(stationId, stationName = '', latitude = null, longitude = null) {
    const departuresContainer = document.getElementById('departures-container');
    if (!departuresContainer) return;

    // Si hay coordenadas, actualizar el mapa (pero SIN hacer scroll)
    if (latitude && longitude && map) {
        map.setView([latitude, longitude], 15);
        
        // Abrir el popup del marcador correspondiente
        markers.forEach(marker => {
            const markerLatLng = marker.getLatLng();
            if (Math.abs(markerLatLng.lat - latitude) < 0.0001 && Math.abs(markerLatLng.lng - longitude) < 0.0001) {
                marker.openPopup();
            }
        });
    }

    departuresContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-3 text-muted">Cargando horarios...</p>
        </div>`;

    try {
        const response = await fetch(`${API_URL}/departures/${stationId}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Datos de salidas:', data);
        
        // El backend devuelve un objeto { station, departures, ... }
        const departures = Array.isArray(data) ? data : (data.departures || []);
        const station = data.station || { name: stationName, id: stationId };
        
        // Añadir coordenadas al objeto station si las tenemos
        if (latitude && longitude) {
            station.latitude = latitude;
            station.longitude = longitude;
        }
        
        displayDepartures(departures, station);
        
        // Scroll to departures section
        setTimeout(() => {
            departuresContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);

    } catch (error) {
        console.error('Error al cargar horarios:', error);
        departuresContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                <strong>Error al cargar los horarios</strong>
                <p class="mb-0 mt-2">${error.message}</p>
                ${error.message.includes('503') ? 
                    '<small class="mt-2 d-block">El servicio de BVG puede estar temporalmente no disponible. Intenta de nuevo en unos momentos.</small>' : 
                    ''}
            </div>`;
    }
}

// Función para mostrar los horarios
function displayDepartures(departures, station = {}) {
    const departuresContainer = document.getElementById('departures-container');
    
    if (!departures || !departures.length) {
        departuresContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-info-circle fa-3x text-muted mb-3"></i>
                <h6>No hay salidas programadas</h6>
                <p class="text-muted small">
                    ${station.name ? `No se encontraron próximas salidas para ${station.name}` : 'No hay horarios disponibles en este momento'}
                </p>
                <small class="text-muted">
                    Esto puede deberse a que no hay servicios programados en la próxima hora,
                    o el servicio puede estar temporalmente interrumpido.
                </small>
            </div>`;
        return;
    }

    // Obtener tipos de transporte únicos
    const transportTypes = {
        'subway': { icon: 'fa-subway', color: 'primary', label: 'Metro' },
        'train': { icon: 'fa-train', color: 'success', label: 'Tren' },
        'tram': { icon: 'fa-train-tram', color: 'warning', label: 'Tranvía' },
        'bus': { icon: 'fa-bus', color: 'info', label: 'Bus' },
        'regional': { icon: 'fa-train', color: 'danger', label: 'Regional' },
        'express': { icon: 'fa-train', color: 'dark', label: 'Express' }
    };

    const departuresList = departures.map((dep, index) => {
        const lineType = dep.line?.type?.toLowerCase() || 'bus';
        const transport = transportTypes[lineType] || transportTypes['bus'];
        
        // Formatear la hora
        let timeDisplay = 'N/A';
        if (dep.when) {
            try {
                const date = new Date(dep.when);
                const now = new Date();
                const diff = Math.floor((date - now) / 60000); // diferencia en minutos
                
                if (diff <= 0) {
                    timeDisplay = '<span class="badge bg-success">Ahora</span>';
                } else if (diff < 60) {
                    timeDisplay = `<span class="badge bg-primary">${diff} min</span>`;
                } else {
                    timeDisplay = date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                }
            } catch (e) {
                timeDisplay = dep.when;
            }
        }

        // ========== FEATURE #2: HIGHLIGHT DELAYS ==========
        // Información de retraso con highlight para retrasos mayores a 5 minutos
        let delayInfo = '';
        let delayClass = '';
        if (dep.delay) {
            // La API puede devolver delay en segundos o minutos, validar
            let delayMinutes = dep.delay;
            
            console.log(`Delay original para ${dep.line?.name}: ${dep.delay}`);
            
            // Si el delay es mayor a 60, probablemente está en segundos
            if (delayMinutes > 60) {
                delayMinutes = Math.floor(delayMinutes / 60);
                console.log(`  Convertido de segundos a minutos: ${delayMinutes}`);
            }
            
            // Solo mostrar retrasos razonables (entre 1 y 30 minutos)
            // Retrasos mayores a 30 minutos son poco comunes y probablemente errores
            if (delayMinutes > 0 && delayMinutes <= 30) {
                if (delayMinutes > 5) {
                    delayInfo = `<span class="badge bg-danger ms-2"><i class="fas fa-exclamation-triangle"></i> +${delayMinutes} min</span>`;
                    delayClass = 'border-danger border-start border-3';
                } else {
                    delayInfo = `<span class="badge bg-warning text-dark ms-2">+${delayMinutes} min</span>`;
                }
            } else if (delayMinutes > 30) {
                console.warn(`  Retraso ignorado (demasiado alto): ${delayMinutes} min`);
            }
        }

        return `
            <div class="departure-item animate-fade-in ${delayClass}" style="animation-delay: ${index * 0.03}s;">
                <div class="d-flex justify-content-between align-items-center p-2 border-bottom hover-highlight">
                    <div class="d-flex align-items-center flex-grow-1">
                        <div class="me-3">
                            <i class="fas ${transport.icon} text-${transport.color} fa-lg"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center">
                                <span class="badge bg-${transport.color} me-2">${dep.line?.name || 'N/A'}</span>
                                <strong class="me-2">${dep.direction || 'Destino desconocido'}</strong>
                                ${delayInfo}
                            </div>
                            ${dep.platform ? `<small class="text-muted">Andén: ${dep.platform}</small>` : ''}
                        </div>
                    </div>
                    <div class="text-end ms-3">
                        ${timeDisplay}
                    </div>
                </div>
            </div>`;
    }).join('');

    departuresContainer.innerHTML = `
        <div class="mb-3 pb-2 border-bottom">
            <h6 class="mb-1">
                ${station.name ? `<i class="fas fa-map-marker-alt text-primary"></i> ${station.name}` : 'Estación'}
            </h6>
            <small class="text-muted">
                <i class="fas fa-clock"></i> Próximas ${departures.length} salidas
                <span class="ms-2">
                    <i class="fas fa-sync-alt"></i> Actualizado: ${new Date().toLocaleTimeString('es-ES')}
                </span>
            </small>
        </div>
        <div class="departures-list" style="max-height: 400px; overflow-y: auto;">
            ${departuresList}
        </div>
        <div class="mt-3 text-center">
            <button class="btn btn-sm btn-outline-primary" onclick="showDepartures('${station.id}', '${station.name}', ${station.latitude || 'null'}, ${station.longitude || 'null'})">
                <i class="fas fa-sync-alt"></i> Actualizar
            </button>
        </div>`;
}

// Función para cargar estaciones populares
async function loadPopularStations() {
    const resultsContainer = document.getElementById('results-container');
    
    console.log('Iniciando carga de estaciones principales...');
    
    // Usar búsquedas genéricas que devuelvan más resultados
    const searches = ['Alexanderplatz', 'Hauptbahnhof', 'Zoo'];
    
    resultsContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-3 text-muted">Cargando estaciones principales...</p>
        </div>`;
    
    try {
        const allStations = [];
        
        // Buscar con términos más genéricos
        for (const searchTerm of searches) {
            try {
                console.log(`Buscando: ${searchTerm}`);
                const url = `${API_URL}/stations/search?q=${encodeURIComponent(searchTerm)}&results=5`;
                const response = await fetch(url);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log(`Datos recibidos para ${searchTerm}:`, data);
                    
                    // El backend devuelve { stations: [...], query: "..." }
                    let stationsList = [];
                    
                    if (Array.isArray(data)) {
                        stationsList = data;
                    } else if (data && Array.isArray(data.stations)) {
                        stationsList = data.stations;
                        console.log(`Extraídas ${stationsList.length} estaciones del objeto`);
                    } else {
                        console.warn(`Formato de respuesta desconocido para ${searchTerm}:`, typeof data);
                    }
                    
                    if (stationsList.length > 0) {
                        console.log(`Procesando ${stationsList.length} estaciones de ${searchTerm}`);
                        // Agregar TODAS las estaciones que vengan
                        stationsList.forEach((station, idx) => {
                            if (station && station.id && station.name) {
                                // Agregar coordenadas si vienen en location
                                if (station.location) {
                                    station.latitude = station.location.latitude;
                                    station.longitude = station.location.longitude;
                                }
                                allStations.push(station);
                                console.log(`  ✓ Agregada: ${station.name}`);
                            } else {
                                console.warn(`  ⚠ Estación ${idx} sin id o name:`, station);
                            }
                        });
                    }
                } else {
                    console.error(`Error HTTP ${response.status} para ${searchTerm}`);
                }
            } catch (e) {
                console.error(`Error cargando ${searchTerm}:`, e);
            }
            
            // Pequeña pausa
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        console.log(`Total de estaciones encontradas: ${allStations.length}`);
        
        if (allStations.length > 0) {
            // Eliminar duplicados por ID
            const uniqueStations = Array.from(
                new Map(allStations.map(s => [s.id, s])).values()
            );
            console.log(`Estaciones únicas: ${uniqueStations.length}`);
            displayResults(uniqueStations);
        } else {
            resultsContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    <strong>No se pudieron cargar las estaciones</strong>
                    <p class="mb-0 mt-2">Intenta buscar una estación específica como "Alexanderplatz".</p>
                </div>`;
        }
    } catch (error) {
        console.error('Error general al cargar estaciones:', error);
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                <strong>Error al cargar las estaciones</strong>
                <p class="mb-0 mt-2">${error.message}</p>
            </div>`;
    }
}

// ========== FEATURE #1: FAVORITES ==========
function updateFavoritesCount() {
    const favorites = getFavorites();
    const countElement = document.getElementById('favorites-count');
    if (countElement) {
        countElement.textContent = favorites.length;
    }
}

function displayFavorites() {
    const favorites = getFavorites();
    const resultsContainer = document.getElementById('results-container');
    
    console.log('Mostrando favoritos:', favorites);
    
    if (favorites.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info">
                <strong>No tienes estaciones favoritas</strong>
                <p class="mb-0 mt-2">Marca estaciones como favoritas haciendo clic en el botón de favorito</p>
            </div>`;
        return;
    }
    
    // Mostrar encabezado
    resultsContainer.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
            <h6 class="mb-0">Tus Favoritos (${favorites.length})</h6>
            <button class="btn btn-sm btn-outline-danger" onclick="clearFavorites()"
                    title="Eliminar todos los favoritos guardados">
                <i class="fas fa-trash"></i> Limpiar
            </button>
        </div>
        <div id="favorites-list"></div>`;
    
    // Usar displayResults pero agregando al contenedor específico
    const stationsHTML = favorites.map((station, index) => {
        console.log('Procesando favorito:', station);
        
        // Agregar marcador al mapa si tiene coordenadas
        if (station.latitude && station.longitude) {
            addMarkerToMap(station);
        }

        return `
            <div class="card mb-2 station-card animate-fade-in" data-station-id="${station.id}" style="animation-delay: ${index * 0.05}s;">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                <i class="fas fa-subway text-primary"></i> 
                                <strong>${station.name || 'Sin nombre'}</strong>
                            </h6>
                            ${station.id ? `<small class="text-muted">ID: ${station.id}</small>` : ''}
                        </div>
                        <button class="btn btn-sm btn-warning favorite-btn" 
                                onclick='toggleFavorite(${JSON.stringify(station)})'
                                title="Quitar de favoritos">
                            <i class="fas fa-star"></i>
                        </button>
                    </div>
                    <div class="mt-2 d-flex gap-2 flex-wrap">
                        <button class="btn btn-sm btn-primary" 
                                onclick="showDepartures('${station.id}', '${escapeHtml(station.name)}', ${station.latitude || 'null'}, ${station.longitude || 'null'})"
                                title="Ver próximas salidas de trenes, buses y tranvías">
                            <i class="fas fa-clock"></i> Horarios
                        </button>
                        ${station.latitude && station.longitude ? `
                            <button class="btn btn-sm btn-outline-secondary" 
                                    onclick="showOnMap(${station.latitude}, ${station.longitude}, '${escapeHtml(station.name)}')"
                                    title="Mostrar ubicación en el mapa y hacer zoom">
                                <i class="fas fa-map-marker-alt"></i> Ver en Mapa
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>`;
    }).join('');
    
    const favoritesList = document.getElementById('favorites-list');
    if (favoritesList) {
        favoritesList.innerHTML = stationsHTML;
    }
}

function clearFavorites() {
    if (confirm('¿Eliminar todas las estaciones favoritas?')) {
        localStorage.removeItem('favoriteStations');
        updateFavoritesCount();
        displayFavorites();
    }
}

function toggleFavorite(station) {
    if (isFavorite(station.id)) {
        removeFavorite(station.id);
    } else {
        addFavorite(station);
    }
    updateFavoritesCount();
    
    // Update the star icon in the UI
    const starBtn = document.querySelector(`[data-station-id="${station.id}"] .favorite-btn`);
    if (starBtn) {
        const icon = starBtn.querySelector('i');
        if (isFavorite(station.id)) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            starBtn.classList.remove('btn-outline-warning');
            starBtn.classList.add('btn-warning');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            starBtn.classList.remove('btn-warning');
            starBtn.classList.add('btn-outline-warning');
        }
    }
}

// ========== FEATURE #4: DARK MODE ==========
function loadThemePreference() {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Update button icon
    const btn = document.getElementById('dark-mode-toggle');
    if (btn) {
        btn.innerHTML = isDark 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

// ========== FEATURE #5: SEARCH HISTORY ==========
function displaySearchHistory() {
    const history = getSearchHistory();
    const searchInput = document.getElementById('search-input');
    
    if (history.length === 0) return;
    
    // Create dropdown if it doesn't exist
    let dropdown = document.getElementById('search-history-dropdown');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'search-history-dropdown';
        dropdown.className = 'search-history-dropdown';
        searchInput.parentNode.appendChild(dropdown);
    }
    
    dropdown.innerHTML = `
        <div class="dropdown-header d-flex justify-content-between align-items-center">
            <small class="text-muted">Búsquedas recientes</small>
            <button class="btn btn-sm btn-link text-danger p-0" onclick="clearSearchHistoryUI()">
                <i class="fas fa-trash"></i>
            </button>
        </div>
        ${history.map(term => `
            <div class="dropdown-item" onclick="selectHistoryItem('${term}')">
                <i class="fas fa-history"></i> ${term}
            </div>
        `).join('')}
    `;
    
    dropdown.style.display = 'block';
}

function selectHistoryItem(term) {
    const searchInput = document.getElementById('search-input');
    searchInput.value = term;
    hideSearchHistory();
    searchStation();
}

function hideSearchHistory() {
    const dropdown = document.getElementById('search-history-dropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

function clearSearchHistoryUI() {
    clearSearchHistory();
    hideSearchHistory();
}

// Add event listeners for search history
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.length < 2) {
            displaySearchHistory();
        }
    });
    
    searchInput.addEventListener('blur', () => {
        // Delay to allow click on dropdown items
        setTimeout(hideSearchHistory, 200);
    });
    
    // Click outside to close
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target)) {
            hideSearchHistory();
        }
    });
});

// ========== INITIALIZATION ==========
// Initialize map when page loads
initMap();

// Add event listeners
const searchInput = document.getElementById('search-input');
if (searchInput) {
    searchInput.addEventListener('input', debounce((e) => {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            searchStation(query);
        } else if (query.length === 0) {
            document.getElementById('results-container').innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <p>Busca una estación o muestra todas las estaciones disponibles</p>
                </div>`;
        }
    }, 500));
}

document.getElementById('show-all-stations').addEventListener('click', loadPopularStations);
document.getElementById('show-favorites').addEventListener('click', displayFavorites);
document.getElementById('center-map-btn').addEventListener('click', () => {
    map.setView([52.5200, 13.4050], 12);
});

// Initialize favorites count
updateFavoritesCount();

// ==================== RADAR DE VEHÍCULOS EN TIEMPO REAL ====================

// Colores por tipo de transporte
const VEHICLE_COLORS = {
    'bus': '#DC3545',        // Rojo
    'tram': '#28A745',       // Verde
    'subway': '#007BFF',     // Azul
    'suburban': '#FFC107',   // Amarillo
    'regional': '#6C757D',   // Gris
    'express': '#6F42C1'     // Púrpura
};

// Obtener color según el tipo de línea
function getVehicleColor(lineType) {
    return VEHICLE_COLORS[lineType] || '#6C757D';
}

// Crear icono personalizado para vehículos
function createVehicleIcon(line) {
    const color = getVehicleColor(line.product || line.type);
    const lineName = line.name || '?';
    
    return L.divIcon({
        className: 'vehicle-marker',
        html: `<div style="background-color: ${color}; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); white-space: nowrap;">
            ${lineName}
        </div>`,
        iconSize: [null, null],
        iconAnchor: [20, 15]
    });
}

// Limpiar marcadores de vehículos del mapa
function clearVehicleMarkers() {
    vehicleMarkers.forEach(marker => map.removeLayer(marker));
    vehicleMarkers = [];
}

// Obtener y mostrar vehículos en el radar
async function updateVehicleRadar() {
    try {
        // Obtener límites del mapa visible
        const bounds = map.getBounds();
        const north = bounds.getNorth();
        const south = bounds.getSouth();
        const west = bounds.getWest();
        const east = bounds.getEast();
        
        // Llamar al API
        const response = await fetch(
            `${API_URL}/radar/vehicles?north=${north}&south=${south}&west=${west}&east=${east}&duration=30&results=100`
        );
        
        if (!response.ok) {
            console.error('Error fetching radar data:', response.status);
            return;
        }
        
        const data = await response.json();
        
        // Limpiar marcadores anteriores
        clearVehicleMarkers();
        
        // Agregar nuevos marcadores
        if (data.vehicles && data.vehicles.length > 0) {
            data.vehicles.forEach(vehicle => {
                if (vehicle.location && vehicle.location.latitude && vehicle.location.longitude) {
                    const marker = L.marker(
                        [vehicle.location.latitude, vehicle.location.longitude],
                        { icon: createVehicleIcon(vehicle.line) }
                    );
                    
                    // Popup con información del vehículo
                    let popupContent = `
                        <div style="min-width: 200px;">
                            <h6 style="margin: 0 0 8px 0; color: ${getVehicleColor(vehicle.line.product || vehicle.line.type)};">
                                <strong>${vehicle.line.name || 'Vehículo'}</strong>
                            </h6>
                            <p style="margin: 4px 0;"><strong>Tipo:</strong> ${vehicle.line.product || vehicle.line.type || 'N/A'}</p>
                            ${vehicle.direction ? `<p style="margin: 4px 0;"><strong>Dirección:</strong> ${vehicle.direction}</p>` : ''}
                    `;
                    
                    if (vehicle.nextStopovers && vehicle.nextStopovers.length > 0) {
                        popupContent += '<p style="margin: 8px 0 4px 0;"><strong>Próximas paradas:</strong></p><ul style="margin: 0; padding-left: 20px;">';
                        vehicle.nextStopovers.slice(0, 3).forEach(stop => {
                            if (stop.stop && stop.stop.name) {
                                popupContent += `<li style="font-size: 12px;">${stop.stop.name}</li>`;
                            }
                        });
                        popupContent += '</ul>';
                    }
                    
                    popupContent += '</div>';
                    
                    marker.bindPopup(popupContent);
                    marker.addTo(map);
                    vehicleMarkers.push(marker);
                }
            });
            
            console.log(`Radar actualizado: ${data.vehicles.length} vehículos en el mapa`);
        }
        
    } catch (error) {
        console.error('Error updating vehicle radar:', error);
    }
}

// Activar/Desactivar radar
function toggleRadar() {
    isRadarActive = !isRadarActive;
    
    const radarBtn = document.getElementById('toggle-radar-btn');
    
    if (isRadarActive) {
        radarBtn.classList.remove('btn-outline-info');
        radarBtn.classList.add('btn-info');
        radarBtn.innerHTML = '<i class="fas fa-broadcast-tower"></i> Radar ON';
        
        // Actualizar inmediatamente
        updateVehicleRadar();
        
        // Actualizar cada 15 segundos
        radarUpdateInterval = setInterval(updateVehicleRadar, 15000);
        
        showNotification('Radar de vehículos activado', 'success');
    } else {
        radarBtn.classList.remove('btn-info');
        radarBtn.classList.add('btn-outline-info');
        radarBtn.innerHTML = '<i class="fas fa-broadcast-tower"></i> Radar OFF';
        
        // Detener actualizaciones
        if (radarUpdateInterval) {
            clearInterval(radarUpdateInterval);
            radarUpdateInterval = null;
        }
        
        // Limpiar vehículos del mapa
        clearVehicleMarkers();
        
        showNotification('Radar de vehículos desactivado', 'info');
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto-cerrar después de 3 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Load dark mode preference
loadThemePreference();