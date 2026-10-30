from fastapi import FastAPI,HTTPException,Request,Header
from app.db import init_db,connect
from app.schemas import TenantIn,UsageIn,GenerateIn
from app.billing import record,usage_totals,token_cost_micro_usd
from app.config import PLANS
from app.stripe_service import checkout,handle_webhook
app=FastAPI(title="Usage Metering & Billing Engine",version="1.0.0")
@app.on_event("startup")
def startup():init_db()
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/plans")
def plans():return PLANS
@app.post("/tenants")
def create_tenant(x:TenantIn):
    with connect() as c:
        try:c.execute("INSERT INTO tenants(id,name) VALUES(?,?)",(x.id,x.name))
        except Exception:raise HTTPException(409,"Tenant ID already exists")
    return {"id":x.id,"name":x.name,"plan":"free","status":"active"}
@app.post("/usage/record")
def record_usage(x:UsageIn):return record(x.tenant_id,x.usage_type,x.quantity,x.idempotency_key)
@app.get("/usage/{tenant_id}")
def get_usage(tenant_id:str):
    with connect() as c:
        t=c.execute("SELECT * FROM tenants WHERE id=?",(tenant_id,)).fetchone()
    if not t:raise HTTPException(404,"Tenant not found")
    used=usage_totals(tenant_id); limits=PLANS[t["plan"]]
    return {"tenant_id":tenant_id,"plan":t["plan"],"status":t["status"],"api_calls":{"used":used.get("api_calls",0),"limit":limits["api_calls"]},"ai_tokens":{"used":used.get("ai_tokens",0),"limit":limits["ai_tokens"]}}
@app.post("/generate")
def generate(x:GenerateIn):
    token_total=x.input_tokens+x.output_tokens # reasoning included in output; cached input included in input
    token_cost=token_cost_micro_usd(x.input_tokens,x.cached_input_tokens,x.output_tokens,x.reasoning_tokens)
    api=record(x.tenant_id,"api_calls",1,x.idempotency_key+":api")
    tokens=record(x.tenant_id,"ai_tokens",token_total,x.idempotency_key+":tokens") if token_total else {"duplicate":False,"quantity":0}
    return {"accepted":True,"usage":{"api":api,"tokens":tokens},"estimated_cost_micro_usd":token_cost}
@app.post("/billing/checkout")
def create_checkout(tenant_id:str):return checkout(tenant_id)
@app.post("/webhooks/stripe")
async def stripe_webhook(request:Request,stripe_signature:str=Header(default="",alias="Stripe-Signature")):
    return handle_webhook(await request.body(),stripe_signature)
