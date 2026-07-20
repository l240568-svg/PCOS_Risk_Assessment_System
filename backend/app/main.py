from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.patients.router import router as patients_router
from app.users.router import router as users_router


app = FastAPI(title="PCOS Risk Assessment API")

@app.get('/')
def read_root():
    return {"message": "Welcome to the PCOS Risk Assessment API"}

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "PCOS Risk Assessment API is running"}

 