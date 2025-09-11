"""
Alternative entry point for the Configuration Service
This file imports the app from main.py for deployment purposes
"""
from main import app

# This allows the service to be run with: uvicorn app:app
if __name__ == "__main__":
    import uvicorn
    from config import service_config
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=service_config.service_port,
        reload=service_config.debug
    )