#!/usr/bin/env python3
"""
Startup script for SleepFace backend with MongoDB Atlas
"""
import os
import uvicorn
from config import get_database_config

def main():
    """Start the server with Atlas configuration"""
    environment = os.getenv("ENVIRONMENT", "development")
    db_config = get_database_config()
    
    print("🚀 Starting SleepFace Backend")
    print(f"Environment: {environment}")
    print(f"Database: {db_config['database_name']} (MongoDB Atlas)")
    print(f"Server: http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    main()







