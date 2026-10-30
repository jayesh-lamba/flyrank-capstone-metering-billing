from datetime import datetime, timezone
from fastapi import HTTPException
from app.db import connect
from app.config import PLANS, PRICING
def current_month_start():
    return datetime.now(timezone.utc).strftime("%Y-%m-01 00:00:00")
def usage_totals(tenant_id):
    with connect() as c:
        rows=c.execute("SELECT usage_type,COALESCE(SUM(quantity),0) n FROM usage_events WHERE tenant_id=? AND created_at>=? GROUP BY usage_type",(tenant_id,current_month_start())).fetchall()
    return {r["usage_type"]:int(r["n"]) for r in rows}
def record(tenant_id,usage_type,quantity,key):
    if usage_type not in ("api_calls","ai_tokens"): raise HTTPException(422,"usage_type must be api_calls or ai_tokens")
    with connect() as c:
        tenant=c.execute("SELECT * FROM tenants WHERE id=?",(tenant_id,)).fetchone()
        if not tenant: raise HTTPException(404,"Tenant not found")
        old=c.execute("SELECT * FROM usage_events WHERE tenant_id=? AND idempotency_key=?",(tenant_id,key)).fetchone()
        if old: return {"event_id":old["id"],"duplicate":True,"quantity":old["quantity"],"usage_type":old["usage_type"]}
        limits=PLANS[tenant["plan"]]
        used=usage_totals(tenant_id).get(usage_type,0)
        if used+quantity>limits[usage_type]:
            code=402 if tenant["status"]!="active" else 429
            raise HTTPException(code,detail={"message":"Plan quota exceeded" if code==429 else "Subscription inactive; upgrade or renew","used":used,"requested":quantity,"limit":limits[usage_type]})
        try:
            cur=c.execute("INSERT INTO usage_events(tenant_id,usage_type,quantity,idempotency_key) VALUES(?,?,?,?)",(tenant_id,usage_type,quantity,key))
            return {"event_id":cur.lastrowid,"duplicate":False,"quantity":quantity,"usage_type":usage_type}
        except Exception:
            old=c.execute("SELECT * FROM usage_events WHERE tenant_id=? AND idempotency_key=?",(tenant_id,key)).fetchone()
            if old:return {"event_id":old["id"],"duplicate":True,"quantity":old["quantity"],"usage_type":old["usage_type"]}
            raise
def token_cost_micro_usd(input_tokens,cached_input_tokens,output_tokens,reasoning_tokens):
    # Cached input is a subset of input, not an extra category. Reasoning is a subset of output.
    fresh=max(0,input_tokens-cached_input_tokens)
    billable_output=output_tokens
    p=PRICING
    return (fresh*p["input_per_million_micro_usd"] + cached_input_tokens*p["cached_input_per_million_micro_usd"] + billable_output*p["output_per_million_micro_usd"])//1_000_000
