#!/usr/bin/env python3
"""
Simple database setup script for GridTrader Pro
This script creates all tables and initializes sample data
"""

import os
import sys
import time

# Add app directory to Python path
sys.path.insert(0, '/app')

def setup_database():
    """Set up database tables and sample data"""
    
    print("=== GridTrader Pro Database Setup ===")
    
    try:
        # Import database components
        print("Importing database modules...")
        from app.database import engine, Base, SessionLocal
        from app.models import (
            Users, UserProfiles, OAuthSessions, Portfolios, Positions,
            GridConfigs, GridLevels, AllocationTargets, Securities,
            PriceData, RealTimePrices, Alerts
        )
        
        print("Database modules imported successfully")
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Check for required tables
        required_tables = ['users', 'securities', 'portfolios', 'positions']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"ERROR: Missing required tables: {missing_tables}")
            return False
            
        print("All required tables created successfully!")
        
        # Initialize sample data
        if os.getenv('INIT_SAMPLE_DATA', 'true').lower() == 'true':
            print("Initializing sample data...")
            
            db = SessionLocal()
            try:
                # Check if securities already exist
                existing_count = db.query(Securities).count()
                print(f"Found {existing_count} existing securities")
                
                if existing_count == 0:
                    # Add sample securities
                    sample_securities = [
                        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
                        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
                        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
                        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
                        {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
                        {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'},
                        {'symbol': 'QQQ', 'name': 'Invesco QQQ ETF'},
                    ]
                    
                    for sec_data in sample_securities:
                        security = Securities(
                            symbol=sec_data['symbol'],
                            name=sec_data['name'],
                            currency='USD',
                            is_active=True
                        )
                        db.add(security)
                    
                    db.commit()
                    print(f"Added {len(sample_securities)} sample securities")
                else:
                    print("Sample data already exists")
                    
            except Exception as e:
                print(f"Error adding sample data: {e}")
                db.rollback()
            finally:
                db.close()
        
        print("=== Database setup completed successfully ===")
        return True
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
