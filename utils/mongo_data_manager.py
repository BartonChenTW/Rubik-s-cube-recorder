"""
MongoDB Data Manager for Rubik's Cube Recorder
Handles all data storage and retrieval operations using MongoDB Atlas
"""

import pandas as pd
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import streamlit as st


# Cache MongoDB connection to avoid reconnecting on every interaction
@st.cache_resource
def get_mongodb_client(connection_string):
    """
    Get cached MongoDB client connection
    
    Args:
        connection_string (str): MongoDB Atlas connection string
    
    Returns:
        MongoClient: MongoDB client instance
    """
    try:
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=45000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        # Test connection
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error creating MongoDB client: {e}")
        return None


class MongoDataManager:
    """Manages data persistence for solve records and algorithms using MongoDB"""
    
    def __init__(self, connection_string=None):
        """
        Initialize the MongoDB data manager
        
        Args:
            connection_string (str): MongoDB Atlas connection string
        """
        # Get connection string from parameter, secrets, or session state
        self.connection_string = None
        
        if connection_string:
            self.connection_string = connection_string
        else:
            # Try to get from Streamlit secrets (safely)
            try:
                if hasattr(st, 'secrets') and 'mongodb' in st.secrets:
                    self.connection_string = st.secrets.mongodb.connection_string
            except Exception:
                pass
            
            # Fall back to session state
            if not self.connection_string:
                self.connection_string = st.session_state.get('mongodb_connection_string')
        
        self.client = None
        self.db = None
        self.solves_collection = None
        self.algorithms_collection = None
        
        if self.connection_string:
            self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            # Use cached client connection
            self.client = get_mongodb_client(self.connection_string)
            
            if not self.client:
                return False
            
            # Get database and collections
            self.db = self.client['rubiks_cube_recorder']
            self.solves_collection = self.db['solves']
            self.algorithms_collection = self.db['algorithms']
            
            # Create indexes for better performance (only if not exists)
            try:
                self.solves_collection.create_index([('timestamp', DESCENDING)], background=True)
                self.solves_collection.create_index('cube_type', background=True)
                self.solves_collection.create_index('player_name', background=True)
                self.algorithms_collection.create_index('category', background=True)
            except Exception:
                pass  # Indexes might already exist
            
            return True
        except ConnectionFailure as e:
            print(f"MongoDB connection error: {e}")
            return False
        except OperationFailure as e:
            print(f"MongoDB authentication error: {e}")
            print("\nTroubleshooting steps:")
            print("1. Check username/password in connection string")
            print("2. Verify database user exists in MongoDB Atlas")
            print("3. Check IP whitelist (add 0.0.0.0/0 for testing)")
            return False
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False
    
    def is_connected(self):
        """Check if connected to MongoDB"""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    # ===== SOLVE RECORDS MANAGEMENT =====
    
    def add_solve(self, solve_record):
        """
        Add a new solve record
        
        Args:
            solve_record (dict): Dictionary containing solve information
                - timestamp: datetime or str
                - player_name: str
                - time: float (seconds)
                - cube_type: str
                - method: str
                - scramble: str
                - notes: str
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Convert timestamp to datetime if it's a string
            if isinstance(solve_record.get('timestamp'), str):
                solve_record['timestamp'] = datetime.strptime(
                    solve_record['timestamp'], 
                    '%Y-%m-%d %H:%M:%S'
                )
            elif not isinstance(solve_record.get('timestamp'), datetime):
                solve_record['timestamp'] = datetime.now()
            
            # Ensure numeric time
            if isinstance(solve_record.get('time'), str):
                solve_record['time'] = float(solve_record['time'].replace('s', ''))
            
            # Insert into MongoDB
            self.solves_collection.insert_one(solve_record)
            return True
            
        except Exception as e:
            print(f"Error adding solve: {e}")
            return False
    
    def load_data(self):
        """
        Load all solve records with caching
        
        Returns:
            pd.DataFrame: DataFrame containing all solve records
        """
        if not self.is_connected():
            return pd.DataFrame(columns=[
                'timestamp', 'player_name', 'time', 'cube_type', 'method', 'scramble', 'notes'
            ])
        
        try:
            # Fetch all solves from MongoDB, sorted by timestamp descending
            solves = list(
                self.solves_collection.find(
                    {},
                    {'_id': 0}  # Exclude _id field for better performance
                ).sort('timestamp', DESCENDING)
            )
            
            if not solves:
                return pd.DataFrame(columns=[
                    'timestamp', 'player_name', 'time', 'cube_type', 'method', 'scramble', 'notes'
                ])
            
            # Convert to DataFrame
            df = pd.DataFrame(solves)
            
            # Ensure required columns exist
            required_columns = ['timestamp', 'player_name', 'time', 'cube_type', 'method', 'scramble', 'notes']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None if col != 'time' else 0.0
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Ensure time is numeric
            if 'time' in df.columns:
                df['time'] = pd.to_numeric(df['time'], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(columns=[
                'timestamp', 'player_name', 'time', 'cube_type', 'method', 'scramble', 'notes'
            ])
    
    def delete_solve(self, timestamp):
        """
        Delete a solve record by timestamp
        
        Args:
            timestamp (datetime or str): Timestamp of the record to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Convert string to datetime if needed
            if isinstance(timestamp, str):
                timestamp = pd.to_datetime(timestamp)
            
            result = self.solves_collection.delete_one({'timestamp': timestamp})
            return result.deleted_count > 0
            
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
        
        Returns:
            bool: True if successful, False otherwise
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
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Ensure date_added is datetime
            if 'date_added' in algorithm:
                if isinstance(algorithm['date_added'], str):
                    algorithm['date_added'] = datetime.fromisoformat(algorithm['date_added'])
                elif not isinstance(algorithm['date_added'], datetime):
                    algorithm['date_added'] = datetime.now()
            else:
                algorithm['date_added'] = datetime.now()
            
            # Check if algorithm already exists
            existing = self.algorithms_collection.find_one({'name': algorithm['name']})
            if existing:
                # Update instead of insert
                self.algorithms_collection.update_one(
                    {'name': algorithm['name']},
                    {'$set': algorithm}
                )
            else:
                self.algorithms_collection.insert_one(algorithm)
            
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
        if not self.is_connected():
            return []
        
        try:
            # Fetch algorithms without _id field for better performance
            algorithms = list(self.algorithms_collection.find({}, {'_id': 0}))
            return algorithms
            
        except Exception as e:
            print(f"Error loading algorithms: {e}")
            return []
    
    def delete_algorithm(self, name):
        """
        Delete an algorithm by name
        
        Args:
            name (str): Name of the algorithm to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.algorithms_collection.delete_one({'name': name})
            return result.deleted_count > 0
            
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
        if not self.is_connected():
            return []
        
        try:
            # Build query
            search_filter = {}
            
            if category:
                search_filter['category'] = category
            
            if query:
                # Case-insensitive regex search
                search_filter['$or'] = [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'notation': {'$regex': query, '$options': 'i'}}
                ]
            
            # Fetch without _id field
            algorithms = list(self.algorithms_collection.find(search_filter, {'_id': 0}))
            return algorithms
            
        except Exception as e:
            print(f"Error searching algorithms: {e}")
            return []
    
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
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()


def show_mongodb_config_ui():
    """Display MongoDB configuration UI in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ MongoDB Configuration")
    
    # Check if connection string is already set
    current_conn = st.session_state.get('mongodb_connection_string')
    
    if current_conn:
        # Test connection
        test_manager = MongoDataManager(current_conn)
        if test_manager.is_connected():
            st.sidebar.success("✅ Connected to MongoDB Atlas")
            
            if st.sidebar.button("🔄 Change Connection"):
                st.session_state['mongodb_connection_string'] = None
                st.rerun()
        else:
            st.sidebar.error("❌ Connection failed")
            if st.sidebar.button("🔄 Update Connection"):
                st.session_state['mongodb_connection_string'] = None
                st.rerun()
    else:
        with st.sidebar.expander("⚙️ Setup MongoDB", expanded=True):
            st.write("Enter your MongoDB Atlas connection string:")
            
            conn_string = st.text_input(
                "Connection String",
                type="password",
                placeholder="mongodb+srv://username:password@cluster.mongodb.net/",
                help="Get this from your MongoDB Atlas cluster",
                key="mongo_conn_input"
            )
            
            if st.button("Connect to MongoDB", key="connect_mongo"):
                if conn_string:
                    # Test connection
                    test_manager = MongoDataManager(conn_string)
                    if test_manager.is_connected():
                        st.session_state['mongodb_connection_string'] = conn_string
                        st.success("✅ Connected successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to connect. Check your connection string.")
                else:
                    st.error("❌ Please enter a connection string")
