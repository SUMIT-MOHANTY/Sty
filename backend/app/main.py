from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.utils.database import engine
from app.models.user import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Passport Portal API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Passport Portal API"}
