import uvicorn
from main import app
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
