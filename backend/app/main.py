from fastapi import FastAPI

from app.auth.router import router as auth_router


app = FastAPI(title="PCOS Risk Assessment API")


app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "PCOS Risk Assessment API is running"}

 