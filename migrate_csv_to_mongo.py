"""
CSV to MongoDB Migration Utility
Migrates existing CSV data to MongoDB Atlas
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from utils.mongo_data_manager import MongoDataManager


def migrate_csv_to_mongodb(connection_string):
    """
    Migrate data from CSV files to MongoDB
    
    Args:
        connection_string (str): MongoDB Atlas connection string
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDataManager(connection_string)
        
        if not mongo_manager.is_connected():
            return False, "Failed to connect to MongoDB", {}
        
        stats = {
            'solves_migrated': 0,
            'algorithms_migrated': 0,
            'errors': []
        }
        
        # Migrate solves
        csv_path = Path("data/solves.csv")
        if csv_path.exists():
            print("Migrating solves from CSV...")
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                try:
                    # Clean the data
                    solve_record = {
                        'timestamp': pd.to_datetime(row['timestamp']),
                        'player_name': row.get('player_name', 'Anonymous'),
                        'time': float(str(row['time']).replace('s', '')),
                        'cube_type': row.get('cube_type', '3x3'),
                        'method': row.get('method', 'None'),
                        'scramble': row.get('scramble', ''),
                        'notes': row.get('notes', '')
                    }
                    
                    # Convert NaN to None
                    for key, value in solve_record.items():
                        if pd.isna(value):
                            solve_record[key] = None if key != 'time' else 0.0
                    
                    if mongo_manager.add_solve(solve_record):
                        stats['solves_migrated'] += 1
                    else:
                        stats['errors'].append(f"Failed to migrate solve: {row['timestamp']}")
                        
                except Exception as e:
                    stats['errors'].append(f"Error processing solve {row.get('timestamp', 'unknown')}: {str(e)}")
            
            print(f"✓ Migrated {stats['solves_migrated']} solves")
        else:
            print("No solves.csv found, skipping...")
        
        # Migrate algorithms
        json_path = Path("data/algorithms.json")
        if json_path.exists():
            print("Migrating algorithms from JSON...")
            with open(json_path, 'r') as f:
                algorithms = json.load(f)
            
            for algo in algorithms:
                try:
                    # Ensure date_added is datetime
                    if 'date_added' in algo:
                        if isinstance(algo['date_added'], str):
                            algo['date_added'] = datetime.fromisoformat(algo['date_added'])
                    else:
                        algo['date_added'] = datetime.now()
                    
                    if mongo_manager.add_algorithm(algo):
                        stats['algorithms_migrated'] += 1
                    else:
                        stats['errors'].append(f"Failed to migrate algorithm: {algo.get('name', 'unknown')}")
                        
                except Exception as e:
                    stats['errors'].append(f"Error processing algorithm {algo.get('name', 'unknown')}: {str(e)}")
            
            print(f"✓ Migrated {stats['algorithms_migrated']} algorithms")
        else:
            print("No algorithms.json found, skipping...")
        
        # Close connection
        mongo_manager.close()
        
        success_message = f"Migration completed!\n"
        success_message += f"- Solves migrated: {stats['solves_migrated']}\n"
        success_message += f"- Algorithms migrated: {stats['algorithms_migrated']}\n"
        
        if stats['errors']:
            success_message += f"\n⚠️ Encountered {len(stats['errors'])} errors"
        
        return True, success_message, stats
        
    except Exception as e:
        return False, f"Migration failed: {str(e)}", {}


def main():
    """Main migration script"""
    print("=" * 60)
    print("CSV to MongoDB Migration Utility")
    print("=" * 60)
    print()
    
    # Try to get connection string from secrets.toml
    connection_string = None
    secrets_path = Path(".streamlit/secrets.toml")
    
    if secrets_path.exists():
        print("Found .streamlit/secrets.toml file")
        try:
            import toml
            secrets = toml.load(secrets_path)
            if 'mongodb' in secrets and 'connection_string' in secrets['mongodb']:
                connection_string = secrets['mongodb']['connection_string']
                print("Using connection string from secrets.toml")
        except Exception as e:
            print(f"Could not read secrets.toml: {e}")
    
    if not connection_string:
        # Get MongoDB connection string from user input
        connection_string = input("Enter your MongoDB Atlas connection string: ").strip()
        
        if not connection_string:
            print("❌ No connection string provided. Exiting.")
            return
    
    print()
    print("Starting migration...")
    print()
    
    success, message, stats = migrate_csv_to_mongodb(connection_string)
    
    print()
    print("=" * 60)
    if success:
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
        print(message)
        
        if stats.get('errors'):
            print("\nErrors encountered:")
            for error in stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(stats['errors']) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more errors")
    else:
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print(message)
    
    print()
    print("Note: Your CSV files have NOT been deleted.")
    print("You can keep them as a backup.")


if __name__ == "__main__":
    main()
