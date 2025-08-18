# ============================
# ETL: JSON → CSV → PostgreSQL (Cloud + Local)
# Modular, beginner-friendly, and heavily commented
# ============================

# 1) Imports we need
import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# 2) ---- Settings / Config ----
#    You can change folders here and keep the rest of the code the same.

# Where to save final CSV backups (local folder).
PROCESSED_CSV_DIR = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/processed_csv"
# Where to save null summary reports (local folder).
REPORTS_DIR       = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/PhonePe_Dashboard/reports"

# Make sure folders exist (creates them if not present).
os.makedirs(PROCESSED_CSV_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Database connections (SQLAlchemy URLs)
CLOUD_DB_URL = "postgresql://neondb_owner:npg_Izljkf3nApt4@ep-flat-dust-a1evsgfm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
LOCAL_DB_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/postgres"

# PostgreSQL schema (public is fine unless you use a custom schema)
DB_SCHEMA = "public"

# 3) ---- Table list (the nine tables you track) ----

# This is where all your JSON files live
BASE_DATA_PATH = "/Users/macbook/Desktop/DS_Project/Phone_pe_pluse/pulse/data"

TABLES_CONFIG = [
    {
        "name": "aggregated_insurance",
        "json_root": f"{BASE_DATA_PATH}/aggregated/insurance/country/india/state/"
    },
    {
        "name": "aggregated_transactions",
        "json_root": f"{BASE_DATA_PATH}/aggregated/transaction/country/india/state/"
    },
    {
        "name": "aggregated_user",
        "json_root": f"{BASE_DATA_PATH}/aggregated/user/country/india/state/"
    },
    {
        # NOTE: This table is derived from the 'top/insurance' data path
        "name": "insurance_data",
        "json_root": f"{BASE_DATA_PATH}/top/insurance/country/india/state/"
    },
    {
        "name": "insurance_hover",
        "json_root": f"{BASE_DATA_PATH}/map/insurance/hover/country/india/state/"
    },
    {
        "name": "map_transaction_hover",
        "json_root": f"{BASE_DATA_PATH}/map/transaction/hover/country/india/state/"
    },
    {
        "name": "map_user",
        "json_root": f"{BASE_DATA_PATH}/map/user/hover/country/india/state/"
    },
    {
        "name": "top_transaction",
        "json_root": f"{BASE_DATA_PATH}/top/transaction/country/india/state/"
    },
    {
        # NOTE: This table name in SQL is different from the path's name ('user')
        "name": "top_user_by_pincode",
        "json_root": f"{BASE_DATA_PATH}/top/user/country/india/state/"
    },
]
# NOTE: If your JSON lives as single files (not folders), set json_root to that file path directly.

# 4) ---- Helper: Create a SQLAlchemy engine safely ----
def make_engine(db_url: str) -> Engine:
    """
    Create a SQLAlchemy Engine using the given database URL.
    This object manages the connection pool and lets pandas to_sql talk to the DB.
    """
    # echo=False keeps logs quiet; set True to debug SQL statements
    return create_engine(db_url, echo=False, future=True)

# 5) ---- Helper: Read JSON into a DataFrame ----
def read_json_to_df(json_path_or_dir: str) -> pd.DataFrame:
    """
    Reads JSON data into a DataFrame.
    - If you pass a folder, it will read ALL .json files inside and stack them into one table.
    - If you pass a single file, it reads that file only.
    The function tries to be flexible with nested JSON by normalizing records when needed.
    """
    def _read_one(fp: str) -> pd.DataFrame:
        # Read one JSON file as python object
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If the JSON is a list of dicts -> DataFrame directly
        if isinstance(data, list):
            return pd.json_normalize(data)
        # If the JSON is a dict -> try to find records inside, else flatten whole dict into one row
        elif isinstance(data, dict):
            # Heuristic: look for common keys holding records
            candidate_keys = ["data", "records", "rows", "items", "transactions", "users", "list"]
            for k in candidate_keys:
                if k in data and isinstance(data[k], list):
                    return pd.json_normalize(data[k])
            # Fallback: normalize entire dict (single row)
            return pd.json_normalize(data)
        else:
            # Unknown structure -> return empty frame to avoid crashing
            return pd.DataFrame()

    # If it's a folder, read all JSON files inside
    if os.path.isdir(json_path_or_dir):
        json_files = sorted(glob.glob(os.path.join(json_path_or_dir, "*.json")))
        frames = [_read_one(fp) for fp in json_files]
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    else:
        # It's a single file
        df = _read_one(json_path_or_dir)

    return df

# 6) ---- Helper: Clean column names and trim strings ----
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Makes the DataFrame DB-friendly:
    - Strips whitespace around string values
    - Converts column names to snake_case (letters, numbers, and underscores only)
    """
    # Trim whitespace for object (string-like) columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype("string").str.strip()

    # Simple snake_case for column names
    def snake(name: str) -> str:
        # Replace spaces and hyphens with underscores and lower-case everything
        s = "".join(ch if ch.isalnum() else "_" for ch in name)
        s = "_".join(filter(None, s.split("_")))  # collapse multiple underscores
        return s.lower()

    df.columns = [snake(c) for c in df.columns]
    return df

# 7) ---- Helper: Save CSV and Null Summary ----
def save_csv_and_nulls(df: pd.DataFrame, table_name: str) -> str:
    """
    Saves the DataFrame to a CSV file in PROCESSED_CSV_DIR and creates
    a null-values summary report in REPORTS_DIR.
    Returns the CSV path.
    """
    # Where we store CSV backup
    csv_path = os.path.join(PROCESSED_CSV_DIR, f"{table_name}.csv")
    df.to_csv(csv_path, index=False)

    # Compute null summary
    nulls = df.isnull().sum()

    # Print to console (as you prefer)
    print("\n🧮 Null Values Summary:", f"({table_name})")
    print(nulls)

    # Also save to a small text file for auditing
    report_path = os.path.join(REPORTS_DIR, f"{table_name}__null_summary.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Null Values Summary for table: {table_name}\n")
        f.write(nulls.to_string())

    return csv_path

# 8) ---- Helper: Write DataFrame to a Database table ----
def df_to_database(
    df: pd.DataFrame,
    table_name: str,
    engine: Engine,
    schema: str = "public",
    chunksize: int = 10_000,
) -> None:
    """
    Bulk-inserts the DataFrame into the given PostgreSQL database.
    - Uses pandas to_sql for simplicity (beginner-friendly).
    - method='multi' sends many rows per INSERT for speed.
    - if_exists='append' will CREATE the table automatically if it doesn't exist, else append rows.
    """
    # Pandas will try to infer dtypes. For stricter control, pass a dtype mapping via the dtype= parameter.
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="append",   # auto-creates table if needed, else appends
        index=False,          # don't write DataFrame index as a column
        chunksize=chunksize,  # controls batch size
        method="multi",       # multi-row INSERTs for better speed
    )

# 9) ---- Optional: Tiny raw SQLAlchemy example (just to show usage) ----
def table_rowcount(engine: Engine, table_name: str, schema: str = "public") -> int:
    """
    Example of using raw SQLAlchemy text() to run a simple SQL query.
    Useful to quickly verify inserts without leaving Python.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text(f'SELECT COUNT(*) FROM "{schema}"."{table_name}";')
        )
        count = result.scalar()
        return int(count) if count is not None else 0
    
# 10) ---- Full pipeline for one table ----
def process_one_table(table_name: str, json_root: str, cloud_engine: Engine, local_engine: Engine) -> None:
    """
    End-to-end steps for a single table:
    1) Read JSON(s) -> DataFrame
    2) Clean up (columns, whitespace)
    3) Save CSV (backup) + null summary
    4) Insert into CLOUD database
    5) Insert into LOCAL database (backup)
    """
    print(f"\n==== Processing table: {table_name} ====")

    # Step 1: Read JSON to DataFrame
    df = read_json_to_df(json_root)
    if df.empty:
        print(f"⚠️  No data found for {table_name} in {json_root}. Skipping.")
        return

    # Step 2: Clean it up
    df = clean_dataframe(df)

    # Step 3: Save CSV + null summary
    csv_path = save_csv_and_nulls(df, table_name)
    print(f"💾 CSV saved to: {csv_path}")

    # Step 4: Insert into CLOUD database
    print("☁️  Inserting into CLOUD (Neon) ...")
    df_to_database(df, table_name, cloud_engine, schema=DB_SCHEMA)
    cloud_count = table_rowcount(cloud_engine, table_name, schema=DB_SCHEMA)
    print(f"✅ Cloud insert complete. Rowcount now: {cloud_count}")

    # Step 5: Insert into LOCAL database (backup)
    print("💻 Inserting into LOCAL (backup) ...")
    df_to_database(df, table_name, local_engine, schema=DB_SCHEMA)
    local_count = table_rowcount(local_engine, table_name, schema=DB_SCHEMA)
    print(f"✅ Local insert complete. Rowcount now: {local_count}")

# 11) ---- Orchestrate all tables ----
def run_all_tables(tables_config):
    """
    Creates both DB engines and runs the pipeline for each table in tables_config.
    """
    # Create engines once (reused for all tables)
    cloud_engine = make_engine(CLOUD_DB_URL)
    local_engine = make_engine(LOCAL_DB_URL)

    for cfg in tables_config:
        name = cfg["name"]
        json_root = cfg["json_root"]
        process_one_table(name, json_root, cloud_engine, local_engine)

    # Dispose engines (closes pooled connections)
    cloud_engine.dispose()
    local_engine.dispose()

# ====== HOW TO RUN (uncomment when ready) ======
# 1) Fill TABLES_CONFIG paths above.
# 2) Then run:
# run_all_tables(TABLES_CONFIG)
