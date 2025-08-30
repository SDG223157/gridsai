#!/usr/bin/env python3
"""
Database initialization script for GridTrader Pro
Creates all tables and handles MySQL compatibility
"""

from database import engine, Base
from models import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("Database initialization completed successfully")
    else:
        print("Database initialization failed")
        exit(1)
