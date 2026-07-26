from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router
from app.patients.router import router as patients_router
from app.users.router import router as users_router
from app.assessments.router import router as assessments_router
from app.dashboard.router import router as dashboard_router
from app.reports.router import router as reports_router
from app.core.init_db import create_otp_table, create_refresh_tokens_table, create_revoked_tokens_table

create_otp_table()
create_revoked_tokens_table()
create_refresh_tokens_table()

app = FastAPI(title="PCOS Risk Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {"message": "Welcome to the PCOS Risk Assessment API"}



app.include_router(reports_router)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(users_router)
app.include_router(assessments_router)
app.include_router(dashboard_router)




 