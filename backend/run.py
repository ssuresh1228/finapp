import uvicorn
from main import app
<<<<<<< HEAD
import logging

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="localhost", 
        port=8000, 
        reload=True,
        log_level='trace',
        use_colors=True
    ),
=======

if __name__ == "__main__":
    uvicorn.run(
        uvicorn.run(app, host="localhost", port=8000),
        reload = True,
        app = "main:app",
        log_level=logging.INFO,
        use_colors=True
    )
>>>>>>> main
