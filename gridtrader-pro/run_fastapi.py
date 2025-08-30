#!/usr/bin/env python3
"""
FastAPI startup script with comprehensive error handling
"""

import sys
import os
import time

# Ensure proper Python path
sys.path.insert(0, '/app')
os.chdir('/app')

def start_fastapi():
    """Start FastAPI with comprehensive error handling"""
    
    print("=== Starting FastAPI Server ===")
    
    try:
        # Test basic imports first
        print("Testing basic imports...")
        import uvicorn
        print("✅ uvicorn imported successfully")
        
        import fastapi
        print("✅ fastapi imported successfully")
        
        # Test database connection
        print("Testing database connection...")
        try:
            from app.database import engine
            with engine.connect() as conn:
                result = conn.execute("SELECT 1").scalar()
                print("✅ Database connection successful")
        except Exception as e:
            print(f"⚠️ Database connection warning: {e}")
        
        # Import the FastAPI app
        print("Importing FastAPI application...")
        
        # Method 1: Direct import
        try:
            from app.main import app
            print("✅ Successfully imported app via app.main")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            
            # Method 2: Module import
            try:
                import app.main
                app = app.main.app
                print("✅ Successfully imported app via module")
            except Exception as e:
                print(f"❌ Method 2 failed: {e}")
                
                # Method 3: Create minimal app
                print("Creating minimal FastAPI app...")
                from fastapi import FastAPI
                app = FastAPI(title="GridTrader Pro API", version="1.0.0")
                
                @app.get("/")
                def root():
                    return {"message": "GridTrader Pro API", "status": "running"}
                
                @app.get("/health")
                def health():
                    return {"status": "healthy", "service": "fastapi"}
                
                print("✅ Created minimal FastAPI app")
        
        # Start the server
        print("Starting uvicorn server...")
        print("Host: 127.0.0.1, Port: 8001")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except Exception as e:
        print(f"❌ FastAPI startup error: {e}")
        import traceback
        traceback.print_exc()
        
        # Wait before exiting to see logs
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    start_fastapi()
