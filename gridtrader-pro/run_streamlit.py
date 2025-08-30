#!/usr/bin/env python3
"""
Streamlit startup script with comprehensive error handling
"""

import sys
import os
import time

# Ensure proper Python path
sys.path.insert(0, '/app')
os.chdir('/app')

def start_streamlit():
    """Start Streamlit with comprehensive error handling"""
    
    print("=== Starting Streamlit Dashboard ===")
    
    try:
        # Test basic imports
        print("Testing Streamlit imports...")
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        # Test if streamlit_app.py exists and is readable
        if os.path.exists('/app/streamlit_app.py'):
            print("✅ streamlit_app.py found")
            with open('/app/streamlit_app.py', 'r') as f:
                content = f.read()
                print(f"✅ streamlit_app.py readable ({len(content)} characters)")
        else:
            print("❌ streamlit_app.py not found")
        
        # Try to start Streamlit
        print("Starting Streamlit server on 127.0.0.1:8502")
        
        # Method 1: Using subprocess for better control
        try:
            import subprocess
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                "/app/streamlit_app.py",
                "--server.port=8502",
                "--server.address=127.0.0.1", 
                "--server.headless=true",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false",
                "--logger.level=info"
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
        except Exception as e:
            print(f"❌ Subprocess method failed: {e}")
            
            # Method 2: Direct CLI import
            print("Trying direct CLI import...")
            import streamlit.web.cli as stcli
            
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
        print(f"❌ Streamlit startup error: {e}")
        import traceback
        traceback.print_exc()
        
        # Wait before exiting to see logs
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    start_streamlit()
