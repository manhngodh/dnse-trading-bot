import uvicorn
from main import app

if __name__ == "__main__":
    # In development mode, enable hot reloading
    # Host 0.0.0.0 makes the server accessible from outside the container
    uvicorn.run("main:app", host='0.0.0.0', port=5000, reload=True, log_level="info")
