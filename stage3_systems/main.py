
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from stage3_systems.database import Base, engine
from stage3_systems import models
from stage3_systems.routers.auth import router as auth_router
from stage3_systems.routers.shipments import router as shipments_router
from stage3_systems.routers.admin import router as admin_router
from stage3_systems.routers.agents import router as agents_router


def migrate_legacy_shipments():
    # create_all does not add columns to existing SQLite tables.
    inspector = inspect(engine)

    if "shipments" in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns("shipments")
        }

        if "owner_user_id" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE shipments "
                        "ADD COLUMN owner_user_id INTEGER REFERENCES users(id)"
                    )
                )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_legacy_shipments()
    yield


# Create FastAPI application
app = FastAPI(
    title="SmartLogistics AI API",
    description="Authenticated shipment booking and tracking API.",
    version="2.0.0",
    lifespan=lifespan,
)


# CORS configuration
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173,"
            "http://localhost:5500,"
            "http://127.0.0.1:5500"
        ),
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API home route
@app.get("/")
def home():
    return {
        "message": "Welcome to SmartLogistics AI API",
        "status": "running",
        "documentation": "/docs",
    }


# Register API routers
app.include_router(auth_router)
app.include_router(shipments_router)
app.include_router(admin_router)
app.include_router(agents_router)
