from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db

app = FastAPI(title="Intelligent Event Photo Retrieval System")

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

@app.on_event("shutdown")
async def shutdown():
    db.close()

@app.get("/")
async def root():
    return {"message": "Server is running and connected to MongoDB!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
