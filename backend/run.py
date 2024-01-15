import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        uvicorn.run(app, host="localhost", port=8000),
        reload = True,
        app = "main:app",
        log_level=logging.INFO,
        use_colors=True
    )
