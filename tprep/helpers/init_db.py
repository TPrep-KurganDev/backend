import os
import re
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL не может быть пустым")

match = re.match(r"postgresql\+psycopg2://(.*):(.*)@(.*):(\d+)/(.*)", DATABASE_URL)
if not match:
    raise ValueError("DATABASE_URL некорректен")
user, password, host, port, dbname = match.groups()

conn = psycopg2.connect(
    dbname="postgres", user=user, password=password, host=host, port=port
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
exists = cur.fetchone()
if not exists:
    cur.execute(f"CREATE DATABASE {dbname}")
    print(f"Database {dbname} created.")
else:
    print(f"Database {dbname} already exists.")

cur.close()
conn.close()

subprocess.run(["alembic", "upgrade", "head"])
print("Migrations applied successfully.")
