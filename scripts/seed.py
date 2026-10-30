from app.db import init_db,connect
init_db()
with connect() as c:
    c.execute("INSERT OR IGNORE INTO tenants(id,name) VALUES('demo-tenant','Demo Tenant')")
print("Seeded demo-tenant on Free plan")
