from fastapi import FastAPI
import logging 
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.mongodb import connet_to_mongo,close_mongo_connection

from app.middleware.error_handler import register_exceptional_handlers
from app.middleware.logging_middleware import RequestloggingMiddleware
from app.routers import auth,employees

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

@asynccontextmanager

async def lifespan(app:FastAPI):
    connet_to_mongo()
    yield

    close_mongo_connection()

app=FastAPI(
    title="Employee Mangement API",
    description=(
        "Enterprise Workforce Management Backend. Provides JWT-secured "
        "authentication and full employee lifecycle management with "
        "role-based access control, search, filtering, pagination, "
        "sorting, and profile image uploads."
    ),
    version="1.0.0",
    contact={"name": "Aditya Dixit"},
    lifespan=lifespan,
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.add_middleware(RequestloggingMiddleware)

register_exceptional_handlers(app)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR),name="uploads")

app.include_router(auth.router)
app.include_router(employees.router)

@app.get('/',tags=['Health'],summary="Health check",description="Basic Health check for the API.")

async def root() ->dict:
    return{
        "success":True,
        "message":"Employee Management API is Running",
        "docs":"/docs",
    }

if __name__=="__main__":
    import uvicorn

    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)
    



