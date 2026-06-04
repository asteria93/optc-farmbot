"""
Database initialization script
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialize MongoDB"""
    try:
        import pymongo
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/optc_farmbot')
        client = pymongo.MongoClient(mongodb_uri)
        db = client.optc_farmbot
        
        # Create collections
        db.accounts.create_index("username", unique=True)
        db.farming_sessions.create_index("account_id")
        db.farming_history.create_index("account_id")
        
        logger.info("MongoDB initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {str(e)}")
        return False

def init_sqlite():
    """Initialize SQLite database"""
    try:
        import sqlite3
        
        db_path = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///optc_farmbot.db').replace('sqlite:///', '')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                berry INTEGER DEFAULT 0,
                gold INTEGER DEFAULT 0,
                experience INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farming_sessions (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                strategy TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_runs INTEGER DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farming_history (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                session_id TEXT,
                farm_type TEXT NOT NULL,
                target TEXT NOT NULL,
                berries_earned INTEGER DEFAULT 0,
                gold_earned INTEGER DEFAULT 0,
                experience_earned INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (session_id) REFERENCES farming_sessions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("SQLite database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing SQLite: {str(e)}")
        return False

def init_redis():
    """Initialize Redis"""
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        client = redis.from_url(redis_url)
        
        # Test connection
        client.ping()
        
        logger.info("Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Redis: {str(e)}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing OPTC Farming Bot database...")
    print("-" * 50)
    
    # Try to initialize MongoDB first, fall back to SQLite
    mongo_success = init_mongodb()
    if not mongo_success:
        print("MongoDB not available, using SQLite")
        sqlite_success = init_sqlite()
        if sqlite_success:
            print("✓ SQLite database initialized")
    else:
        print("✓ MongoDB initialized")
    
    # Try Redis
    redis_success = init_redis()
    if redis_success:
        print("✓ Redis connected")
    else:
        print("⚠ Redis not available (optional)")
    
    print("-" * 50)
    print("Database initialization complete!")
