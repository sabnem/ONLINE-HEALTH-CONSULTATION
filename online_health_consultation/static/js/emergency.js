// Emergency Services JavaScript

// Initialize map and places service
let map;
let service;
let currentInfoWindow = null;

// Debug function to log errors
function logError(error, context) {
    console.error(`Emergency Services Error (${context}):`, error);
    const errorMessage = document.createElement('div');
    errorMessage.className = 'alert alert-danger mt-2';
    errorMessage.textContent = `Error: ${error.message || error}`;
    document.getElementById('debug-info')?.appendChild(errorMessage);
}

// Function to validate Google Maps API
function validateGoogleMaps() {
    if (typeof google === 'undefined') {
        throw new Error('Google Maps API not loaded. Please check your API key.');
    }
    if (typeof google.maps === 'undefined') {
        throw new Error('Google Maps API not initialized properly.');
    }
    if (typeof google.maps.places === 'undefined') {
        throw new Error('Google Places API not loaded. Make sure "places" library is included.');
    }
    return true;
}

// Function to get user's current location and find nearby hospitals
function findNearbyHospitals() {
    const hospitalsList = document.getElementById('hospitalsList');
    
    // Add debug information container
    if (!document.getElementById('debug-info')) {
        const debugInfo = document.createElement('div');
        debugInfo.id = 'debug-info';
        debugInfo.className = 'mt-3';
        hospitalsList.parentNode.appendChild(debugInfo);
    }

    hospitalsList.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Finding nearby hospitals...</p></div>';

    // Validate Google Maps API
    try {
        validateGoogleMaps();
    } catch (error) {
        logError(error, 'API Validation');
        hospitalsList.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        return;
    }

    // Check if geolocation is supported
    if (!navigator.geolocation) {
        const error = new Error('Geolocation is not supported by your browser');
        logError(error, 'Geolocation Support');
        hospitalsList.innerHTML = '<div class="alert alert-danger">' + error.message + '</div>';
        return;
    }

    // Get current position
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Create the places request
            const location = new google.maps.LatLng(lat, lng);
            const request = {
                location: location,
                radius: '5000', // Search within 5km
                type: ['hospital']
            };

            // Initialize map
            map = new google.maps.Map(document.getElementById('map'), {
                center: location,
                zoom: 13
            });

            // Create places service
            service = new google.maps.places.PlacesService(map);
            
            // Perform nearby search
            service.nearbySearch(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    displayHospitals(results);
                } else {
                    hospitalsList.innerHTML = '<div class="alert alert-danger">Error: Could not find nearby hospitals</div>';
                }
            });
        },
        (error) => {
            let errorMessage = 'Error getting your location: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Location permission denied. Please enable location services.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Request timed out.';
                    break;
                default:
                    errorMessage += 'An unknown error occurred.';
            }
            hospitalsList.innerHTML = `<div class="alert alert-danger">${errorMessage}</div>`;
        }
    );
}

// Function to display hospitals in the list
function displayHospitals(hospitals) {
    const hospitalsList = document.getElementById('hospitalsList');
    let userLocation = map.getCenter();
    
    if (hospitals.length === 0) {
        hospitalsList.innerHTML = '<div class="alert alert-warning">No hospitals found in your area</div>';
        return;
    }

    // Create map container if it doesn't exist
    if (!document.getElementById('map')) {
        const mapDiv = document.createElement('div');
        mapDiv.id = 'map';
        mapDiv.style.height = '300px';
        mapDiv.style.marginBottom = '20px';
        mapDiv.className = 'rounded';
        hospitalsList.parentNode.insertBefore(mapDiv, hospitalsList);
    }

    // Create list container
    let html = '<div class="list-group">';
    
    // Add hospitals to list
    hospitals.forEach((hospital) => {
        const rating = hospital.rating ? `${hospital.rating} ⭐` : 'No rating';
        const distance = google.maps.geometry.spherical.computeDistanceBetween(
            hospital.geometry.location,
            map.getCenter()
        );
        const distanceKm = (distance / 1000).toFixed(1);
        
        // Create Google Maps directions URL
        const directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLocation.lat()},${userLocation.lng()}&destination=${hospital.geometry.location.lat()},${hospital.geometry.location.lng()}&travelmode=driving`;
        
        html += `
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between mb-2">
                    <h6 class="mb-1">${hospital.name}</h6>
                    <small>${distanceKm} km</small>
                </div>
                <p class="mb-1">${hospital.vicinity}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small>${rating}</small>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" onclick="showHospitalDetails('${hospital.place_id}')">
                            <i class="fas fa-info-circle"></i> Details
                        </button>
                        <a href="${directionsUrl}" target="_blank" class="btn btn-sm btn-success">
                            <i class="fas fa-directions"></i> Get Directions
                        </a>
                    </div>
                </div>
            </div>
        `;

        // Add marker to map with info window
        const marker = new google.maps.Marker({
            position: hospital.geometry.location,
            map: map,
            title: hospital.name
        });

        // Add click listener to marker
        marker.addListener('click', () => {
            if (currentInfoWindow) {
                currentInfoWindow.close();
            }
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div style="max-width: 200px;">
                        <h6>${hospital.name}</h6>
                        <p class="mb-2">${hospital.vicinity}</p>
                        <a href="${directionsUrl}" target="_blank" class="btn btn-sm btn-success">
                            <i class="fas fa-directions"></i> Get Directions
                        </a>
                    </div>
                `
            });
            infoWindow.open(map, marker);
            currentInfoWindow = infoWindow;
        });
    });

    html += '</div>';
    hospitalsList.innerHTML = html;
}

// Function to show detailed hospital information
function showHospitalDetails(placeId) {
    const request = {
        placeId: placeId,
        fields: ['name', 'formatted_address', 'formatted_phone_number', 'opening_hours', 'website', 'rating', 'reviews', 'geometry']
    };

    service.getDetails(request, (place, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            // Close previous info window if open
            if (currentInfoWindow) {
                currentInfoWindow.close();
            }

            // Get user's location for directions
            const userLocation = map.getCenter();
            const directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLocation.lat()},${userLocation.lng()}&destination=${place.geometry.location.lat()},${place.geometry.location.lng()}&travelmode=driving`;

            // Create content for info window
            let content = `
                <div style="max-width: 300px;">
                    <h5>${place.name}</h5>
                    <p><i class="fas fa-map-marker-alt"></i> ${place.formatted_address}</p>
            `;

            if (place.formatted_phone_number) {
                content += `<p><i class="fas fa-phone"></i> <a href="tel:${place.formatted_phone_number}">${place.formatted_phone_number}</a></p>`;
            }

            if (place.website) {
                content += `<p><i class="fas fa-globe"></i> <a href="${place.website}" target="_blank">Visit Website</a></p>`;
            }

            if (place.opening_hours) {
                content += '<p><i class="fas fa-clock"></i> ';
                content += place.opening_hours.isOpen() ? 
                    '<span class="text-success">Open Now</span>' : 
                    '<span class="text-danger">Closed</span>';
                content += '</p>';
            }

            // Add directions button
            content += `
                <div class="mt-3">
                    <a href="${directionsUrl}" target="_blank" class="btn btn-success btn-sm w-100">
                        <i class="fas fa-directions"></i> Get Directions
                    </a>
                </div>
            `;

            content += '</div>';

            // Create and show info window
            const infoWindow = new google.maps.InfoWindow({
                content: content
            });

            infoWindow.setPosition(place.geometry.location);
            infoWindow.open(map);
            currentInfoWindow = infoWindow;

            // Pan map to the hospital location
            map.panTo(place.geometry.location);
        }
    });
}
