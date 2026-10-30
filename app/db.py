import sqlite3
from pathlib import Path
from app.config import DATABASE_URL
def connect():
    # Starter uses SQLite for zero-cost local execution. PostgreSQL can replace this adapter.
    path=DATABASE_URL.replace("sqlite:///","")
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(path); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS plans(name TEXT PRIMARY KEY, api_limit INTEGER NOT NULL, token_limit INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS tenants(id TEXT PRIMARY KEY, name TEXT NOT NULL, plan TEXT NOT NULL DEFAULT 'free', status TEXT NOT NULL DEFAULT 'active', stripe_customer_id TEXT, FOREIGN KEY(plan) REFERENCES plans(name));
        CREATE TABLE IF NOT EXISTS subscriptions(id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, stripe_subscription_id TEXT UNIQUE, status TEXT NOT NULL, plan TEXT NOT NULL, FOREIGN KEY(tenant_id) REFERENCES tenants(id));
        CREATE TABLE IF NOT EXISTS usage_events(id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL, usage_type TEXT NOT NULL, quantity INTEGER NOT NULL, idempotency_key TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(tenant_id,idempotency_key), FOREIGN KEY(tenant_id) REFERENCES tenants(id));
        CREATE INDEX IF NOT EXISTS idx_usage_tenant_date ON usage_events(tenant_id,created_at);
        CREATE TABLE IF NOT EXISTS stripe_events(event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')
        c.executemany("INSERT OR IGNORE INTO plans VALUES(?,?,?)",[("free",1000,100000),("pro",100000,10000000)])
