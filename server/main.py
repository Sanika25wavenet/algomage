from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db
from fastapi.staticfiles import StaticFiles
from routers import auth, uploads, events, search

app = FastAPI(title="Intelligent Event Photo Retrieval System")

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(events.router)
app.include_router(search.router)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.connect()
    print("DEBUG: Registered Routes:")
    for route in app.routes:
        print(f"DEBUG: {route.path} {route.methods}")

@app.on_event("shutdown")
async def shutdown():
    db.close()

@app.get("/")
async def root():
    return {"message": "Server is running and connected to MongoDB!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
