import psycopg2
import pandas as pd

NEON_CONN = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_Izljkf3nApt4",
    "host": "ep-flat-dust-a1evsgfm-pooler.ap-southeast-1.aws.neon.tech",
    "port": "5432",
    "sslmode": "require"
}

LOCAL_CONN = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    try:
        # Try connecting to Neon first
        conn = psycopg2.connect(**NEON_CONN)
        print("✅ Connected to Neon Cloud DB")
        return conn
    except Exception as e:
        print(f"⚠️ Neon connection failed: {e}")
        print("🔄 Switching to Local DB...")
        # Fallback to local DB
        return psycopg2.connect(**LOCAL_CONN)

def run_query(query):
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df
