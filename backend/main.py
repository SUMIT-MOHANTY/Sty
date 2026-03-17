from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1 import auth, applications, appointments

app = FastAPI(title="Passport Management System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])

@app.get("/")
async def root():
    return {"message": "Welcome to Passport Management System API"}
