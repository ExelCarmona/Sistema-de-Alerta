// MeteoHex - Weather Dashboard Frontend Logic

document.addEventListener("DOMContentLoaded", () => {
    // API base URL (relative to serve locally)
    const API_BASE = "/api";

    // DOM Elements
    const locationsList = document.getElementById("locations-list");
    const addLocationForm = document.getElementById("add-location-form");
    const inputLat = document.getElementById("input-lat");
    const inputLon = document.getElementById("input-lon");
    const addError = document.getElementById("add-error");
    const locationsLoader = document.getElementById("locations-loader");
    const btnAdd = document.getElementById("btn-add");

    const noLocationSelected = document.getElementById("no-location-selected");
    const weatherDisplay = document.getElementById("weather-display");

    const locationName = document.getElementById("location-name");
    const btnSync = document.getElementById("btn-sync");
    const syncIcon = document.getElementById("sync-icon");
    const currentEmoji = document.getElementById("current-emoji");
    const currentTemp = document.getElementById("current-temp");
    const currentDesc = document.getElementById("current-desc");
    const metaCoords = document.getElementById("meta-coords");
    const metaElevation = document.getElementById("meta-elevation");
    const metaTimezone = document.getElementById("meta-timezone");

    const statHumidity = document.getElementById("stat-humidity");
    const statWind = document.getElementById("stat-wind");
    const statTime = document.getElementById("stat-time");

    const toast = document.getElementById("toast");
    const toastMessage = document.getElementById("toast-message");

    // State Variables
    let selectedLocationId = null;
    let hourlyChartInstance = null;
    let dailyChartInstance = null;

    // Helper: Show Toast Notification
    function showToast(message, isError = false) {
        toastMessage.textContent = message;
        if (isError) {
            toast.classList.add("error");
        } else {
            toast.classList.remove("error");
        }
        toast.classList.add("show");
        
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3500);
    }

    // API: Fetch and render locations list
    async function loadLocations() {
        locationsLoader.classList.remove("hidden");
        try {
            const response = await fetch(`${API_BASE}/locations`);
            if (!response.ok) throw new Error("No se pudieron cargar las ubicaciones.");
            const locations = await response.json();
            
            locationsList.innerHTML = "";
            if (locations.length === 0) {
                locationsList.innerHTML = `<li class="loader">Ninguna zona registrada</li>`;
            } else {
                locations.forEach(loc => {
                    const li = document.createElement("li");
                    li.className = `location-item ${selectedLocationId === loc.id ? 'active' : ''}`;
                    li.dataset.id = loc.id;
                    
                    li.innerHTML = `
                        <div class="loc-details">
                            <span class="loc-title">Ubicación #${loc.id}</span>
                            <span class="loc-coords">Lat: ${loc.latitud.toFixed(3)} | Lon: ${loc.longitud.toFixed(3)}</span>
                        </div>
                        <i class="fa-solid fa-chevron-right loc-chevron"></i>
                    `;
                    
                    li.addEventListener("click", () => selectLocation(loc.id));
                    locationsList.appendChild(li);
                });
            }
        } catch (error) {
            console.error(error);
            showToast(error.message, true);
        } finally {
            locationsLoader.classList.add("hidden");
        }
    }

    // Action: Select location
    async function selectLocation(id) {
        selectedLocationId = id;
        
        // Highlight active sidebar item
        document.querySelectorAll(".location-item").forEach(item => {
            if (parseInt(item.dataset.id) === id) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        // Load weather details
        await loadWeatherData(id);
    }

    // API: Load weather details & draw charts
    async function loadWeatherData(id) {
        try {
            // Show loader/spinner indicators if needed
            const response = await fetch(`${API_BASE}/locations/${id}/weather`);
            if (!response.ok) throw new Error("Error al obtener los datos del clima.");
            const weather = await response.json();

            // Populate current conditions card
            locationName.textContent = `Ubicación #${weather.location.id}`;
            metaCoords.textContent = `${weather.location.latitud.toFixed(4)}°, ${weather.location.longitud.toFixed(4)}°`;
            metaElevation.textContent = weather.location.elevacion !== null ? weather.location.elevacion : "--";
            metaTimezone.textContent = weather.location.zona_horaria || "--";

            if (weather.current) {
                currentEmoji.textContent = weather.current.clima_info.emoji;
                currentTemp.textContent = weather.current.temperatura_2m.toFixed(1);
                currentDesc.textContent = weather.current.clima_info.description;
                statHumidity.textContent = `${weather.current.humedad_relativa_2m}%`;
                statWind.textContent = `${weather.current.velocidad_viento_10m} km/h`;
                
                // Format ISO time nicely
                const rawTime = weather.current.tiempo; // "YYYY-MM-DDTHH:MM"
                const formattedTime = rawTime.replace("T", " ");
                statTime.textContent = formattedTime;
            } else {
                currentEmoji.textContent = "❓";
                currentTemp.textContent = "--";
                currentDesc.textContent = "Sin datos actuales";
                statHumidity.textContent = "-- %";
                statWind.textContent = "-- km/h";
                statTime.textContent = "--";
            }

            // Draw Charts
            renderHourlyChart(weather.hourly);
            renderDailyChart(weather.daily);

            // Toggle views with nice transition
            noLocationSelected.classList.add("hidden");
            weatherDisplay.classList.add("show");
        } catch (error) {
            console.error(error);
            showToast(error.message, true);
        }
    }

    // Chart.js: Render 24h Hourly Forecast
    function renderHourlyChart(hourlyData) {
        // Slice next 24 points to represent a single day
        const next24 = hourlyData.slice(0, 24);
        
        const labels = next24.map(h => {
            const timePart = h.tiempo.split("T")[1]; // "HH:MM"
            return timePart;
        });
        const temps = next24.map(h => h.temperatura_2m);
        const rainProbs = next24.map(h => h.probabilidad_precipitacion);

        if (hourlyChartInstance) {
            hourlyChartInstance.destroy();
        }

        const ctx = document.getElementById("hourlyChart").getContext("2d");
        
        // Custom gradients
        const tempGradient = ctx.createLinearGradient(0, 0, 0, 300);
        tempGradient.addColorStop(0, 'rgba(6, 182, 212, 0.45)');
        tempGradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

        hourlyChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Temperatura (°C)',
                        data: temps,
                        borderColor: '#06b6d4',
                        borderWidth: 3,
                        backgroundColor: tempGradient,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Probabilidad Lluvia (%)',
                        data: rainProbs,
                        borderColor: 'rgba(99, 102, 241, 0.5)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        backgroundColor: 'transparent',
                        fill: false,
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f3f4f6', font: { family: 'Inter' } }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' },
                        title: { display: true, text: 'Temperatura (°C)', color: '#06b6d4' }
                    },
                    y1: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#9ca3af' },
                        title: { display: true, text: 'Lluvia (%)', color: '#6366f1' },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    // Chart.js: Render 7 Day Forecast
    function renderDailyChart(dailyData) {
        const labels = dailyData.map(d => {
            const [, month, day] = d.fecha.split("-");
            return `${day}/${month}`;
        });
        const tempsMax = dailyData.map(d => d.temperatura_2m_max);
        const tempsMin = dailyData.map(d => d.temperatura_2m_min);
        const rainSums = dailyData.map(d => d.suma_precipitacion);

        if (dailyChartInstance) {
            dailyChartInstance.destroy();
        }

        const ctx = document.getElementById("dailyChart").getContext("2d");

        dailyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        type: 'line',
                        label: 'Temp Máx (°C)',
                        data: tempsMax,
                        borderColor: '#ef4444',
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.3,
                        order: 1
                    },
                    {
                        type: 'line',
                        label: 'Temp Mín (°C)',
                        data: tempsMin,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.3,
                        order: 2
                    },
                    {
                        type: 'bar',
                        label: 'Precipitación (mm)',
                        data: rainSums,
                        backgroundColor: 'rgba(6, 182, 212, 0.3)',
                        borderColor: '#06b6d4',
                        borderWidth: 1,
                        borderRadius: 5,
                        order: 3,
                        yAxisID: 'yPrecip'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f3f4f6', font: { family: 'Inter' } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' },
                        title: { display: true, text: 'Temperatura (°C)', color: '#f3f4f6' }
                    },
                    yPrecip: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#9ca3af' },
                        title: { display: true, text: 'Lluvia (mm)', color: '#06b6d4' }
                    }
                }
            }
        });
    }

    // Action: Sync selected location
    btnSync.addEventListener("click", async () => {
        if (!selectedLocationId) return;

        syncIcon.classList.add("spinning");
        btnSync.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/locations/${selectedLocationId}/sync`, {
                method: "POST"
            });
            if (!response.ok) throw new Error("No se pudo sincronizar la información.");
            
            showToast("Datos actualizados desde Open-Meteo correctamente.");
            await loadWeatherData(selectedLocationId);
        } catch (error) {
            console.error(error);
            showToast(error.message, true);
        } finally {
            syncIcon.classList.remove("spinning");
            btnSync.disabled = false;
        }
    });

    // Form: Submit add location
    addLocationForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const lat = parseFloat(inputLat.value);
        const lon = parseFloat(inputLon.value);
        
        addError.classList.add("hidden");
        btnAdd.disabled = true;
        btnAdd.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Guardando...`;

        try {
            const response = await fetch(`${API_BASE}/locations`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ latitud: lat, longitud: lon })
            });

            if (!response.ok) {
                const errDetail = await response.json();
                throw new Error(errDetail.detail || "Error al añadir la ubicación.");
            }

            const newLoc = await response.json();
            
            showToast(`Ubicación #${newLoc.id} añadida y sincronizada.`);
            inputLat.value = "";
            inputLon.value = "";
            
            // Reload side list and select new location
            await loadLocations();
            await selectLocation(newLoc.id);
        } catch (error) {
            console.error(error);
            addError.textContent = error.message;
            addError.classList.remove("hidden");
            showToast("Error al registrar ubicación", true);
        } finally {
            btnAdd.disabled = false;
            btnAdd.innerHTML = `<i class="fa-solid fa-plus"></i> Añadir`;
        }
    });

    // Initial Loading calls
    loadLocations();
});
