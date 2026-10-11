import mysql.connector
from mysql.connector import pooling, Error
from flask import current_app, g
from contextlib import contextmanager
import datetime
from decimal import Decimal

_pool = None

def init_db_pool(config):
    """Initialize MySQL connection pool with application configuration."""
    global _pool
    try:
        pool_kwargs = {
            "pool_name": config.DB_POOL_NAME,
            "pool_size": min(config.DB_POOL_SIZE, 32),
            "pool_reset_session": True,
            "host": config.DB_HOST,
            "port": config.DB_PORT,
            "user": config.DB_USER,
            "password": config.DB_PASSWORD,
            "database": config.DB_NAME,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False
        }
        _pool = pooling.MySQLConnectionPool(**pool_kwargs)
    except Error as e:
        # Fallback or propagate
        print(f"Error initializing connection pool: {e}")
        _pool = None

def get_db_connection():
    """Get a connection from pool or create a fresh one."""
    global _pool
    if _pool:
        try:
            return _pool.get_connection()
        except Error:
            pass
    
    # Direct connection fallback
    return mysql.connector.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
        autocommit=False
    )

def serialize_row(row):
    """Serialize database types such as Date, Time, Decimal to standard JSON primitives."""
    if not isinstance(row, dict):
        return row
    serialized = {}
    for k, v in row.items():
        if isinstance(v, (datetime.date, datetime.datetime)):
            serialized[k] = v.isoformat()
        elif isinstance(v, datetime.timedelta):
            # Format timedelta (MySQL TIME) to HH:MM:SS
            total_seconds = int(v.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            serialized[k] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif isinstance(v, Decimal):
            serialized[k] = float(v)
        else:
            serialized[k] = v
    return serialized

def serialize_rows(rows):
    """Serialize a list of database rows."""
    return [serialize_row(r) for r in rows]

@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """Context manager for obtaining a database cursor and connection with safe cleanup."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
