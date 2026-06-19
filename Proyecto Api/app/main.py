import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.adapters.inbound.rest.router import router
from app.adapters.outbound.database.sqlite_repository import SQLiteWeatherRepository
from app.adapters.outbound.http.open_meteo_adapter import HttpOpenMeteoAdapter
from app.domain.weather_service import WeatherService

app = FastAPI(
    title="Weather System (Hexagonal Architecture)",
    description="A hexagonal system consuming local SQLite db and syncing with Open-Meteo API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection Configuration on Startup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "openmeteo_clima.db")

@app.on_event("startup")
def startup_event():
    # Instantiate Outbound Adapters
    repository = SQLiteWeatherRepository(db_path=DB_PATH)
    open_meteo_client = HttpOpenMeteoAdapter()
    
    # Instantiate Domain Service (Inbound Port Implementation)
    weather_service = WeatherService(repository=repository, open_meteo_client=open_meteo_client)
    
    # Store in application state so it can be retrieved by routers via Depends
    app.state.weather_service = weather_service

# Include REST API Router
app.include_router(router)

# Mount Static Files (Frontend UI)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_index():
    """
    Serves the main frontend dashboard at the root URL.
    """
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Weather API. Frontend static files are not yet created."}
