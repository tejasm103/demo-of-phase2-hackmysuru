import re
import sqlite3
import pymysql
import pymysql.cursors
from pathlib import Path
from config import Config

_db_mode = None  # 'mysql' or 'sqlite'

def get_connection():
    global _db_mode
    # Attempt MySQL first if not forced to sqlite
    if _db_mode != 'sqlite':
        try:
            # Check if database exists or create it
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
            conn.select_db(Config.DB_NAME)
            _db_mode = 'mysql'
            return conn, 'mysql'
        except Exception as e:
            if not Config.USE_SQLITE_FALLBACK:
                raise e
            _db_mode = 'sqlite'

    # Fallback SQLite
    Config.SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    sqlite_conn = sqlite3.connect(str(Config.SQLITE_PATH), timeout=20.0, check_same_thread=False)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_conn.execute("PRAGMA foreign_keys = ON;")
    return sqlite_conn, 'sqlite'

def query_db(sql, params=None, one=False):
    conn, mode = get_connection()
    if params is None:
        params = ()

    if mode == 'mysql':
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                res = cur.fetchone() if one else cur.fetchall()
                return res
        finally:
            conn.close()
    else:
        # SQLite mode: convert %s to ?
        sqlite_sql = re.sub(r'%s', '?', sql)
        try:
            cur = conn.cursor()
            cur.execute(sqlite_sql, params)
            if one:
                row = cur.fetchone()
                return dict(row) if row else None
            else:
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

def execute_db(sql, params=None):
    conn, mode = get_connection()
    if params is None:
        params = ()

    if mode == 'mysql':
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.lastrowid
        finally:
            conn.close()
    else:
        sqlite_sql = re.sub(r'%s', '?', sql)
        try:
            cur = conn.cursor()
            cur.execute(sqlite_sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

def get_current_db_engine():
    global _db_mode
    if _db_mode is None:
        _, mode = get_connection()
        return mode
    return _db_mode

def init_db(force_reseed=False):
    """Initializes tables and seeds data if empty or forced."""
    conn, mode = get_connection()
    print(f"[*] Initializing AdaptiveLearn AI database using [{mode.upper()}] engine...")

    if mode == 'mysql':
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW TABLES LIKE 'users';")
                exists = cur.fetchone()
                if not exists or force_reseed:
                    with open(Config.SCHEMA_SQL_PATH, 'r', encoding='utf-8') as f:
                        schema_sql = f.read()
                    for statement in schema_sql.split(';'):
                        stmt = statement.strip()
                        if stmt and not stmt.upper().startswith("CREATE DATABASE") and not stmt.upper().startswith("USE "):
                            try:
                                cur.execute(stmt)
                            except Exception as ex:
                                pass

                    with open(Config.SEED_SQL_PATH, 'r', encoding='utf-8') as f:
                        seed_sql = f.read()
                    for statement in seed_sql.split(';'):
                        stmt = statement.strip()
                        if stmt and not stmt.upper().startswith("USE "):
                            try:
                                cur.execute(stmt)
                            except Exception as ex:
                                pass
                    print("[+] MySQL schema and seeds executed successfully.")
        finally:
            conn.close()
    else:
        # SQLite schema initialization
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            exists = cur.fetchone()
            if not exists or force_reseed:
                # Convert MySQL DDL to SQLite compatible
                with open(Config.SCHEMA_SQL_PATH, 'r', encoding='utf-8') as f:
                    schema_content = f.read()
                
                # Sanitize MySQL specific syntax for SQLite
                clean_ddl = schema_content
                clean_ddl = re.sub(r'CREATE DATABASE[^;]*;', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'USE [^;]*;', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'ENGINE=InnoDB[^;]*', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'DEFAULT CHARSET=[^\s;,]*', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'COLLATE=[^\s;,]*', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'\bINT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'\bAUTO_INCREMENT\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'\bAUTO_INCREMENT\b', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'ON UPDATE CURRENT_TIMESTAMP', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'ENUM\([^)]+\)', 'TEXT', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r'UNIQUE\s+KEY\s+[^\s(]+\s*\(', 'UNIQUE (', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r',?\s*INDEX\s+idx_[^\s,(]+(\s*\([^)]+\))?', '', clean_ddl, flags=re.IGNORECASE)
                clean_ddl = re.sub(r',\s*\)', ')', clean_ddl)

                for statement in clean_ddl.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        try:
                            cur.execute(stmt)
                        except Exception as e:
                            pass
                conn.commit()

                # Seed data
                with open(Config.SEED_SQL_PATH, 'r', encoding='utf-8') as f:
                    seed_content = f.read()
                clean_seed = re.sub(r'USE [^;]*;', '', seed_content, flags=re.IGNORECASE)
                clean_seed = re.sub(r'INSERT INTO `?([a-zA-Z0-9_]+)`?', r'INSERT OR IGNORE INTO \1', clean_seed, flags=re.IGNORECASE)
                for statement in clean_seed.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        try:
                            cur.execute(stmt)
                        except Exception as e:
                            pass
                conn.commit()
                print("[+] SQLite schema and seed data loaded successfully.")
        finally:
            conn.close()
