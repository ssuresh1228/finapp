from fastapi import FastAPI 

app = FastAPI()

@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message" : "root endpoint: this is the main entrypoint to the rest of the app"}