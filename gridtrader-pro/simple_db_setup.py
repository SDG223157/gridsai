#!/usr/bin/env python3
"""
Simple database setup using direct SQL commands
No complex imports or dependencies
"""

import os
import mysql.connector
from mysql.connector import Error

def setup_database():
    """Set up database using direct SQL commands"""
    
    print("=== Simple Database Setup ===")
    
    try:
        # Database connection parameters
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'default'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'autocommit': True
        }
        
        print(f"Connecting to MySQL at {config['host']}:{config['port']}")
        print(f"Database: {config['database']}, User: {config['user']}")
        
        # Connect to database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Connected to database successfully")
        
        # Read and execute SQL file
        sql_file = '/app/create_tables.sql'
        print(f"Executing SQL from {sql_file}")
        
        with open(sql_file, 'r') as file:
            sql_content = file.read()
        
        # Split SQL commands and execute each one
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for i, command in enumerate(commands):
            try:
                if command:
                    cursor.execute(command)
                    print(f"Executed command {i+1}/{len(commands)}")
            except Error as e:
                if "already exists" not in str(e):
                    print(f"Warning executing command {i+1}: {e}")
        
        # Verify tables were created
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"Database setup completed successfully!")
        print(f"Created/verified {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Verify sample data
        cursor.execute("SELECT COUNT(*) FROM securities")
        securities_count = cursor.fetchone()[0]
        print(f"Securities table has {securities_count} records")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Setup error: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    exit(0 if success else 1)
