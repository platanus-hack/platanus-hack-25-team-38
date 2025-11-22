from fastapi import FastAPI
# from database import Base, engine
# from routers import auth
# from config import settings

app = FastAPI()

# Base.metadata.create_all(bind=engine)

@app.get("/")
async def health_check():
    return {"status": "healthy!"}

# Example router
# app.include_router(auth.router)