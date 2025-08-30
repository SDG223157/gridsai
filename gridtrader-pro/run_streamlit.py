#!/usr/bin/env python3
"""
Streamlit startup script with proper error handling
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, '/app')

def start_streamlit():
    """Start Streamlit with proper error handling"""
    
    try:
        print("Starting Streamlit server...")
        
        # Import streamlit
        import streamlit.web.cli as stcli
        
        print("Starting Streamlit on 127.0.0.1:8502")
        
        # Set up arguments for streamlit
        sys.argv = [
            "streamlit",
            "run",
            "/app/streamlit_app.py",
            "--server.port=8502",
            "--server.address=127.0.0.1",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        stcli.main()
        
    except Exception as e:
        print(f"Streamlit startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_streamlit()
