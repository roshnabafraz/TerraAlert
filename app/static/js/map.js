document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("location-map");
    const homeMapElement = document.getElementById("home-map");
    const locationInput = document.getElementById("location");
    const useLocationBtn = document.getElementById("use-location");
    const locationForm = document.querySelector(".location-form");

    // create main dashboard map if element exists
    let map = null;
    if (mapElement) {
        map = L.map("location-map").setView([30, 69], 5);
    }

    // optionally create home map (read-only)
    let homeMap = null;
    if (homeMapElement) {
        homeMap = L.map("home-map").setView([30, 69], 5);
    }

    if (!map && !homeMap) {
        return;
    }

    // helper to add tilelayer to given map instance
    function addTiles(m) {
        // Use an English‑label light basemap from Esri so
        // country and city names remain readable at higher zoom.
        L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            {
                attribution:
                    "Tiles &copy; OpenStreetMap contributors",
                maxZoom: 20,
            }
        ).addTo(m);
        // ensure proper sizing if map is hidden initially
        setTimeout(() => m.invalidateSize(), 100);
        window.addEventListener('resize', () => setTimeout(() => m.invalidateSize(), 100));
    }

    // If the map container size changes after init (common on responsive/mobile),
    // force Leaflet to recalc its layout.
    function observeMapResize(el, m) {
        if (!el || !m) return;
        if (typeof ResizeObserver === "undefined") return;

        let t = null;
        const ro = new ResizeObserver(() => {
            if (t) window.clearTimeout(t);
            t = window.setTimeout(() => m.invalidateSize(), 80);
        });
        ro.observe(el);
    }

    if (map) {
        addTiles(map);
        observeMapResize(mapElement, map);
    }
    if (homeMap) {
        addTiles(homeMap);
        observeMapResize(homeMapElement, homeMap);
    }



    let marker = null;
    let permanentMarker = null;
    const USER_ID = "default_user"; // In production, this would come from user session
    const HOME_RISK_ALERT_THRESHOLD_PERCENT = 20;

    // Load and display permanent location on both maps (dashboard & home)
    function loadPermanentLocation() {
        fetch(`/api/permanent-location?user_id=${USER_ID}`)
            .then(r => {
                if (r.ok) return r.json();
                throw new Error("No permanent location");
            })
            .then(data => {
                displayPermanentMarker(data.latitude, data.longitude, data.location_name);
                if (homeMap) {
                    // also show on home map
                    L.marker([data.latitude, data.longitude])
                        .addTo(homeMap)
                        .bindPopup(`<b>Permanent Location</b><br>${data.location_name || ""}`);
                    homeMap.setView([data.latitude, data.longitude], 10);
                }
                // update button state if present
                const btn = document.getElementById("set-permanent-btn");
                if (btn) {
                    btn.textContent = "✓ Set as Permanent";
                    btn.style.background = "var(--low)";
                }

                // Home page risk notification (only after permanent location is available)
                if (homeMap) {
                    showHomeRiskNotification(data);
                } else {
                    showDashboardRiskIndicator(data);
                }
            })
            .catch(e => {
                console.log("No permanent location set");
            });
    }

    function buildRiskLocationText(permanentLocation) {
        // Risk filtering is text-based (not geo-distance). For coordinates, the
        // match works best when we use the exact saved `location_name` string.
        const locName = permanentLocation && permanentLocation.location_name;
        if (typeof locName === "string") {
            const trimmed = locName.trim();
            if (trimmed) return trimmed;
        }

        const lat = permanentLocation && permanentLocation.latitude;
        const lng = permanentLocation && permanentLocation.longitude;
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
            // Match dashboard/map input formatting (4 decimals).
            return `${Number(lat).toFixed(4)},${Number(lng).toFixed(4)}`;
        }

        return null;
    }

    function showHomeRiskNotification(permanentLocation) {
        const container = document.getElementById("home-risk-notification");
        if (!container) return;

        const locationText = buildRiskLocationText(permanentLocation);
        if (!locationText) return;

        fetch(`/api/risk?location=${encodeURIComponent(locationText)}`)
            .then(r => r.json())
            .then(data => {
                const overall = data && data.risk_summary && data.risk_summary.overall;
                const pctRaw = overall && overall.percentage;
                const pct = typeof pctRaw === "number" ? pctRaw : parseFloat(pctRaw);

                if (!Number.isFinite(pct)) return;

                // Useful for debugging whether the notification should appear.
                console.log("Home risk check", {
                    locationText,
                    percentage: pct,
                    level: overall && overall.level,
                    top_type: overall && overall.top_type,
                });

                if (pct >= HOME_RISK_ALERT_THRESHOLD_PERCENT) {
                    const level = overall && overall.level ? overall.level : "low";
                    const topType = overall && overall.top_type ? overall.top_type : "unknown";

                    container.className = `alert ${level}`;
                    container.style.display = "block";
                    container.innerHTML = `
                        <strong>Heads up:</strong> Elevated disaster risk detected for your permanent location.
                        <div style="margin-top: 6px; color: var(--muted);">
                            Estimated risk: ${pct}%.
                            Top type: ${topType}.
                        </div>
                        <div style="margin-top: 8px;">
                            <a href="/guidance" style="color: var(--text); font-weight: 600;">View awareness guidance</a>
                        </div>
                    `;
                } else {
                    container.style.display = "none";
                }
            })
            .catch(() => {
                // If risk calculation fails (e.g., network issue), do not block Home page.
                console.error("Home risk fetch failed");
                container.style.display = "none";
            });
    }

    function showDashboardRiskIndicator(permanentLocation) {
        const container = document.getElementById("dashboard-risk-indicator");
        if (!container) return;

        const locationText = buildRiskLocationText(permanentLocation);
        if (!locationText) return;

        // Start hidden while we compute.
        container.style.display = "none";

        fetch(`/api/risk?location=${encodeURIComponent(locationText)}`)
            .then(r => r.json())
            .then(data => {
                const overall = data && data.risk_summary && data.risk_summary.overall;
                const pctRaw = overall && overall.percentage;
                const pct = typeof pctRaw === "number" ? pctRaw : parseFloat(pctRaw);

                if (!overall || !Number.isFinite(pct)) return;

                const level = overall.level || "low";
                const label = level === "high" ? "High Risk" : level === "medium" ? "Medium Risk" : "Safe";

                container.classList.remove("low", "medium", "high");
                container.classList.add(level);
                container.innerHTML = `
                    <span class="live-main">${label}</span>
                    <span class="live-sub">${pct}%</span>
                `;
                container.style.display = "inline-flex";
            })
            .catch(() => {
                container.style.display = "none";
            });
    }

    // Display permanent location marker (with different color)
    function displayPermanentMarker(lat, lng, name) {
        if (map) {
            if (permanentMarker) {
                map.removeLayer(permanentMarker);
            }
            permanentMarker = L.marker([lat, lng], {
                icon: L.icon({
                  iconUrl: "/static/images/permanent-marker.svg",
                    iconSize: [25, 25],
                    iconAnchor: [12, 12],
                }),
            })
                .addTo(map)
                .bindPopup(`<b>📍 Permanent Location</b><br>${name}`);
        }
    }

    // Click on map to select location (only if dashboard map exists)
    if (map) {
        map.on("click", (e) => {
            const { lat, lng } = e.latlng;
            updateLocation(lat, lng);
        });
    }

    // Use current location button
    if (useLocationBtn) {
        useLocationBtn.addEventListener("click", () => {
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by this browser.");
                return;
            }

            useLocationBtn.disabled = true;
            useLocationBtn.textContent = "Getting location...";

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    updateLocation(latitude, longitude);
                    map.setView([latitude, longitude], 12);
                    useLocationBtn.disabled = false;
                    useLocationBtn.textContent = "Use My Location";
                },
                () => {
                    alert("Unable to retrieve your location.");
                    useLocationBtn.disabled = false;
                    useLocationBtn.textContent = "Use My Location";
                }
            );
        });
    }

    // Update location input and marker
    function updateLocation(lat, lng) {
        const formattedLocation = `${lat.toFixed(4)},${lng.toFixed(4)}`;
        locationInput.value = formattedLocation;

        // Remove existing marker
        if (marker) {
            map.removeLayer(marker);
        }

        // Add new marker
        marker = L.marker([lat, lng])
            .addTo(map)
            .bindPopup(`<b>Selected Location</b><br>Latitude: ${lat.toFixed(4)}<br>Longitude: ${lng.toFixed(4)}`)
            .openPopup();

        // Center map on marker
        map.setView([lat, lng], 12);
    }

    // set-permanent button listener (makes sense after updateLocation so lat/lng defined)
    const permBtn = document.getElementById("set-permanent-btn");
    if (permBtn) {
        permBtn.addEventListener("click", () => {
            const loc = locationInput.value.trim();
            if (!loc) {
                alert("Please select a location first.");
                return;
            }
            const coords = loc.split(",").map(c => parseFloat(c));
            if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
                window.setAsPermanent(coords[0], coords[1], loc);
            } else {
                // if user typed a name, we can reuse geocode to get lat/lng
                geocodeLocation(loc);
                // when geocode completes, setAsPermanent is invoked via updateLocation? not exactly
                // so we can store lastName and call inside updateLocation
                lastPermanentName = loc;
            }
        });
    }

    // remember name when geocoding for permanent set
    let lastPermanentName = null;

    // modify updateLocation to optionally apply lastPermanentName
    const originalUpdate = updateLocation;
    updateLocation = function(lat, lng) {
        originalUpdate(lat, lng);
        if (lastPermanentName) {
            window.setAsPermanent(lat, lng, lastPermanentName);
            lastPermanentName = null;
        }
    };

    // Prevent form from reloading page on submit - let it submit normally but keep marker
    if (locationForm) {
        locationForm.addEventListener("submit", (e) => {
            const location = locationInput.value.trim();
            if (!location) {
                e.preventDefault();
                alert("Please select a location or enter coordinates.");
                return;
            }
            // Allow form submission to proceed
        });
    }

    // Handle manual input in location field
    if (locationInput) {
        locationInput.addEventListener("change", () => {
            const location = locationInput.value.trim();
            if (!location) return;

            // Check if it's coordinates format (lat,lon)
            const coordMatch = location.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
            if (coordMatch) {
                const lat = parseFloat(coordMatch[1]);
                const lng = parseFloat(coordMatch[2]);
                if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
                    updateLocation(lat, lng);
                    return;
                }
            }

            // Otherwise, treat as city/location name and use geocoding
            geocodeLocation(location);
        });
    }

    const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";
    // Geocode location by name using Nominatim
    function geocodeLocation(locationName) {
        const searchQuery = locationName + ", Pakistan";
        fetch(
    `${NOMINATIM_URL}?q=${encodeURIComponent(searchQuery)}&format=json&limit=1`
)
            .then((response) => response.json())
            .then((data) => {
                if (data && data.length > 0) {
                    const result = data[0];
                    const lat = parseFloat(result.lat);
                    const lng = parseFloat(result.lon);
                    updateLocation(lat, lng);
                } else {
                    // Try without Pakistan restriction
                   fetch(
    `${NOMINATIM_URL}?q=${encodeURIComponent(locationName)}&format=json&limit=1`
)
                        .then((response) => response.json())
                        .then((data) => {
                            if (data && data.length > 0) {
                                const result = data[0];
                                const lat = parseFloat(result.lat);
                                const lng = parseFloat(result.lon);
                                updateLocation(lat, lng);
                            } else {
                                alert(
                                    `Location "${locationName}" not found. Please enter valid coordinates or city name.`
                                );
                            }
                        })
                        .catch(() => {
                            alert("Error searching for location. Please try again.");
                        });
                }
            })
            .catch(() => {
                alert("Error searching for location. Please try again.");
            });
    }

    // If there's an initial location (dashboard page only), load it on the map
    if (locationInput && locationInput.value) {
        const coords = locationInput.value.split(",").map((c) => parseFloat(c.trim()));
        if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
            updateLocation(coords[0], coords[1]);
        }
    }

    // Load permanent location on page load
    loadPermanentLocation();

    // Expose functions globally for HTML
    window.setAsPermanent = function(lat, lng, name) {
        fetch("/api/permanent-location", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: USER_ID,
                latitude: lat,
                longitude: lng,
                location_name: name
            })
        })
        .then(r => r.json())
        .then(data => {
            displayPermanentMarker(lat, lng, name);
            if (homeMap) {
                // update home map marker as well
                L.marker([lat, lng])
                    .addTo(homeMap)
                    .bindPopup(`<b>Permanent Location</b><br>${name}`);
                homeMap.setView([lat, lng], 10);
            }
            const btn = document.getElementById("set-permanent-btn");
            if (btn) {
                btn.textContent = "✓ Set as Permanent";
                btn.style.background = "var(--low)";
            }
            // Update dashboard risk pill immediately after saving.
            showDashboardRiskIndicator({ latitude: lat, longitude: lng, location_name: name });
            alert(`Permanent location set to: ${name}`);
        })
        .catch(e => {
            alert("Error saving permanent location: " + e.message);
        });
    };

    window.removePermanent = function() {
        fetch("/api/permanent-location", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: USER_ID
            })
        })
        .then(r => r.json())
        .then(data => {
            if (permanentMarker) {
                map.removeLayer(permanentMarker);
            }
            if (homeMap && typeof homeMap.eachLayer === 'function') {
                // remove all markers from homeMap (could be improved)
                homeMap.eachLayer(layer => {
                    if (layer instanceof L.Marker) {
                        homeMap.removeLayer(layer);
                    }
                });
            }
            const btn = document.getElementById("set-permanent-btn");
            if (btn) {
                btn.textContent = "Set as Permanent Location";
                btn.style.background = "var(--accent)";
            }
            const remBtn = document.getElementById("remove-permanent-btn");
            if (remBtn) {
                remBtn.remove();
            }
            alert("Permanent location removed");
        })
        .catch(e => {
            alert("Error removing permanent location: " + e.message);
        });
    };

    // attach remove button listener if it exists
    const remBtn = document.getElementById("remove-permanent-btn");
    if (remBtn) {
        remBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to remove your permanent location?')) {
                window.removePermanent();
            }
        });
    }
});
