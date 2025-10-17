#!/usr/bin/env python3
"""
Startup script for SleepFace backend
Supports different environments: development, production
"""
import os
import sys
import uvicorn
from config import ENVIRONMENT, API_HOST, API_PORT, DEBUG, get_database_config

def main():
    """Main startup function"""
    print(f"🚀 Starting SleepFace backend in {ENVIRONMENT} mode")
    
    # Print configuration
    db_config = get_database_config()
    print(f"📊 Database: {db_config['database_name']} at {db_config['mongo_url']}")
    print(f"🌐 Server: {API_HOST}:{API_PORT}")
    print(f"🐛 Debug: {DEBUG}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )

if __name__ == "__main__":
    main()







