"""
Data Manager for Rubik's Cube Recorder
Handles all data storage and retrieval operations
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path


class DataManager:
    """Manages data persistence for solve records and algorithms"""
    
    def __init__(self, data_dir="data"):
        """Initialize the data manager with a data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.solves_file = self.data_dir / "solves.csv"
        self.algorithms_file = self.data_dir / "algorithms.json"
        
        # Create files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Create data files if they don't exist"""
        if not self.solves_file.exists():
            pd.DataFrame(columns=[
                'timestamp', 'player_name', 'time', 'cube_type', 'scramble', 'notes'
            ]).to_csv(self.solves_file, index=False)
        
        if not self.algorithms_file.exists():
            with open(self.algorithms_file, 'w') as f:
                json.dump([], f)
    
    # ===== SOLVE RECORDS MANAGEMENT =====
    
    def add_solve(self, solve_record):
        """
        Add a new solve record
        
        Args:
            solve_record (dict): Dictionary containing solve information
                - timestamp: datetime
                - player_name: str
                - time: float (seconds)
                - cube_type: str
                - scramble: str
                - notes: str
        """
        try:
            df = self.load_data()
            new_record = pd.DataFrame([solve_record])
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(self.solves_file, index=False)
            return True
        except Exception as e:
            print(f"Error adding solve: {e}")
            return False
    
    def load_data(self):
        """
        Load all solve records
        
        Returns:
            pd.DataFrame: DataFrame containing all solve records
        """
        try:
            if os.path.exists(self.solves_file):
                df = pd.read_csv(self.solves_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    # Add player_name column if it doesn't exist (for backward compatibility)
                    if 'player_name' not in df.columns:
                        df['player_name'] = 'Anonymous'
                return df
            return pd.DataFrame(columns=[
                'timestamp', 'player_name', 'time', 'cube_type', 'scramble', 'notes'
            ])
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(columns=[
                'timestamp', 'player_name', 'time', 'cube_type', 'scramble', 'notes'
            ])
    
    def delete_solve(self, index):
        """
        Delete a solve record by index
        
        Args:
            index (int): Index of the record to delete
        """
        try:
            df = self.load_data()
            if 0 <= index < len(df):
                df = df.drop(index).reset_index(drop=True)
                df.to_csv(self.solves_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error deleting solve: {e}")
            return False
    
    def get_statistics(self, cube_type=None):
        """
        Get statistics for solve times
        
        Args:
            cube_type (str, optional): Filter by cube type
        
        Returns:
            dict: Dictionary containing various statistics
        """
        df = self.load_data()
        
        if df.empty:
            return None
        
        if cube_type:
            df = df[df['cube_type'] == cube_type]
        
        if df.empty:
            return None
        
        times = df['time'].values
        
        stats = {
            'count': len(times),
            'best': float(times.min()),
            'worst': float(times.max()),
            'mean': float(times.mean()),
            'median': float(pd.Series(times).median()),
            'std': float(times.std()) if len(times) > 1 else 0,
            'ao5': self._calculate_average_of(times, 5),
            'ao12': self._calculate_average_of(times, 12),
            'ao100': self._calculate_average_of(times, 100),
        }
        
        return stats
    
    def _calculate_average_of(self, times, n):
        """
        Calculate average of n (removing best and worst)
        
        Args:
            times (array): Array of times
            n (int): Number of solves to average
        
        Returns:
            float: Average time, or None if not enough data
        """
        if len(times) < n:
            return None
        
        last_n = times[-n:]
        # Remove best and worst
        trimmed = sorted(last_n)[1:-1]
        return float(sum(trimmed) / len(trimmed))
    
    def export_to_csv(self, filepath):
        """
        Export all solve data to a CSV file
        
        Args:
            filepath (str): Path to save the CSV file
        """
        try:
            df = self.load_data()
            df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    # ===== ALGORITHMS MANAGEMENT =====
    
    def add_algorithm(self, algorithm):
        """
        Add a new algorithm to the library
        
        Args:
            algorithm (dict): Dictionary containing algorithm information
                - name: str
                - notation: str
                - category: str
                - notes: str
                - date_added: datetime
        """
        try:
            algorithms = self.load_algorithms()
            # Convert datetime to string for JSON serialization
            if isinstance(algorithm.get('date_added'), datetime):
                algorithm['date_added'] = algorithm['date_added'].isoformat()
            
            algorithms.append(algorithm)
            
            with open(self.algorithms_file, 'w') as f:
                json.dump(algorithms, f, indent=2)
            return True
        except Exception as e:
            print(f"Error adding algorithm: {e}")
            return False
    
    def load_algorithms(self):
        """
        Load all algorithms from storage
        
        Returns:
            list: List of algorithm dictionaries
        """
        try:
            if os.path.exists(self.algorithms_file):
                with open(self.algorithms_file, 'r') as f:
                    algorithms = json.load(f)
                    # Convert date strings back to datetime
                    for algo in algorithms:
                        if 'date_added' in algo and isinstance(algo['date_added'], str):
                            algo['date_added'] = datetime.fromisoformat(algo['date_added'])
                    return algorithms
            return []
        except Exception as e:
            print(f"Error loading algorithms: {e}")
            return []
    
    def delete_algorithm(self, index):
        """
        Delete an algorithm by index
        
        Args:
            index (int): Index of the algorithm to delete
        """
        try:
            algorithms = self.load_algorithms()
            if 0 <= index < len(algorithms):
                algorithms.pop(index)
                
                # Convert datetime objects to strings for JSON
                for algo in algorithms:
                    if isinstance(algo.get('date_added'), datetime):
                        algo['date_added'] = algo['date_added'].isoformat()
                
                with open(self.algorithms_file, 'w') as f:
                    json.dump(algorithms, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error deleting algorithm: {e}")
            return False
    
    def search_algorithms(self, query, category=None):
        """
        Search algorithms by name or category
        
        Args:
            query (str): Search query
            category (str, optional): Filter by category
        
        Returns:
            list: Filtered list of algorithms
        """
        algorithms = self.load_algorithms()
        
        if category:
            algorithms = [a for a in algorithms if a['category'] == category]
        
        if query:
            query = query.lower()
            algorithms = [
                a for a in algorithms
                if query in a['name'].lower() or query in a['notation'].lower()
            ]
        
        return algorithms
    
    def get_recent_solves(self, n=10, cube_type=None):
        """
        Get the n most recent solves
        
        Args:
            n (int): Number of recent solves to return
            cube_type (str, optional): Filter by cube type
        
        Returns:
            pd.DataFrame: DataFrame with recent solves
        """
        df = self.load_data()
        
        if df.empty:
            return df
        
        if cube_type:
            df = df[df['cube_type'] == cube_type]
        
        return df.sort_values('timestamp', ascending=False).head(n)
    
    def get_personal_bests(self):
        """
        Get personal best times for each cube type
        
        Returns:
            dict: Dictionary mapping cube types to best times
        """
        df = self.load_data()
        
        if df.empty:
            return {}
        
        pbs = df.groupby('cube_type')['time'].min().to_dict()
        return pbs
