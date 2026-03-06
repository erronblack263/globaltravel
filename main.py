from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from core.config import settings
from core.database import engine
from models import Base

# Import v1 routers
from api.v1.auth import router as auth_router
from api.v1.resorts import router as resorts_router
from api.v1.destinations import router as destinations_router
from api.v1.bookings import router as bookings_router
from api.v1.resort_bookings import router as resort_bookings_router
from api.v1.destination_bookings import router as destination_bookings_router
from api.v1.payments import router as payments_router
from api.v1.admin import router as admin_router
from api.v1.tickets import router as tickets_router
from api.v1.users import router as users_router
from api.controllers.test_router import test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: clean up resources
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A comprehensive travel booking API for resorts and destinations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(resorts_router, prefix="/api/v1")
app.include_router(destinations_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(resort_bookings_router, prefix="/api/v1")
app.include_router(destination_bookings_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(test_router, prefix="/api/v1/test")

# Mount static files for images
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Global Travel API",
        "docs": "/docs",
        "test_endpoints": {
            "basic_test": "/api/v1/test/basic-test",
            "simple_test": "/api/v1/test/simple-test",
            "test_endpoint": "/api/v1/test/test-endpoint",
            "another_test": "/api/v1/test/another-test"
        },
        "redoc": "/redoc",
        "api_versions": {
            "v1": "/api/v1"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "debug": settings.DEBUG
    }


@app.get("/api/v1")
async def api_info():
    """API v1 information."""
    return {
        "version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "resorts": "/api/v1/resorts",
            "destinations": "/api/v1/destinations",
            "bookings": "/api/v1/bookings",
            "payments": "/api/v1/payments"
        },
        "documentation": "/docs"
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return HTTPException(status_code=404, detail="Resource not found")


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
