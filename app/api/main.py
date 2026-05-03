from fastapi import FastAPI
from app.api.club_routes import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def root():
    # todo: set up DB
    return {"message": "Server started"}

