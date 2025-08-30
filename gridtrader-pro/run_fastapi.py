#!/usr/bin/env python3
"""
FastAPI startup script with proper error handling
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/app')

def start_fastapi():
    """Start FastAPI with proper error handling"""
    
    try:
        print("Starting FastAPI server...")
        
        # Import with error handling
        try:
            from app.main import app
            print("Successfully imported FastAPI app")
        except ImportError as e:
            print(f"Import error: {e}")
            # Try alternative import
            import app.main as main_module
            app = main_module.app
            print("Successfully imported FastAPI app (alternative method)")
        
        # Start uvicorn
        import uvicorn
        
        print("Starting uvicorn server on 127.0.0.1:8001")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"FastAPI startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_fastapi()
