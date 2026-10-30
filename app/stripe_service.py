import stripe
from fastapi import HTTPException
from app.config import STRIPE_SECRET_KEY,STRIPE_WEBHOOK_SECRET,STRIPE_PRICE_ID_PRO,APP_BASE_URL
from app.db import connect
def checkout(tenant_id):
    if not all([STRIPE_SECRET_KEY,STRIPE_PRICE_ID_PRO]): raise HTTPException(503,"Stripe test credentials and Pro price ID are not configured")
    stripe.api_key=STRIPE_SECRET_KEY
    with connect() as c:
        t=c.execute("SELECT * FROM tenants WHERE id=?",(tenant_id,)).fetchone()
        if not t: raise HTTPException(404,"Tenant not found")
        customer=t["stripe_customer_id"]
        if not customer:
            obj=stripe.Customer.create(name=t["name"],metadata={"tenant_id":tenant_id})
            customer=obj.id
            c.execute("UPDATE tenants SET stripe_customer_id=? WHERE id=?",(customer,tenant_id))
    session=stripe.checkout.Session.create(mode="subscription",customer=customer,line_items=[{"price":STRIPE_PRICE_ID_PRO,"quantity":1}],success_url=APP_BASE_URL+"/billing/success?session_id={CHECKOUT_SESSION_ID}",cancel_url=APP_BASE_URL+"/billing/cancel",metadata={"tenant_id":tenant_id})
    return {"checkout_url":session.url,"session_id":session.id}
def handle_webhook(payload,signature):
    if not STRIPE_WEBHOOK_SECRET: raise HTTPException(503,"Stripe webhook secret is not configured")
    try:event=stripe.Webhook.construct_event(payload,signature,STRIPE_WEBHOOK_SECRET)
    except Exception: raise HTTPException(400,"Invalid Stripe webhook signature")
    eid=event["id"]; etype=event["type"]; obj=event["data"]["object"]
    with connect() as c:
        if c.execute("SELECT 1 FROM stripe_events WHERE event_id=?",(eid,)).fetchone():return {"received":True,"duplicate":True}
        if etype in ("checkout.session.completed","customer.subscription.updated","customer.subscription.deleted"):
            tenant_id=(obj.get("metadata") or {}).get("tenant_id")
            if not tenant_id and obj.get("customer"):
                t=c.execute("SELECT id FROM tenants WHERE stripe_customer_id=?",(obj["customer"],)).fetchone()
                tenant_id=t["id"] if t else None
            if tenant_id:
                active=etype!="customer.subscription.deleted" and obj.get("status","active") in ("active","trialing")
                plan="pro" if active else "free"
                status="active" if active else "inactive"
                c.execute("UPDATE tenants SET plan=?,status=? WHERE id=?",(plan,status,tenant_id))
                sub_id=obj.get("subscription") or obj.get("id")
                if sub_id:
                    c.execute("INSERT OR REPLACE INTO subscriptions(id,tenant_id,stripe_subscription_id,status,plan) VALUES(?,?,?,?,?)",(eid,tenant_id,sub_id,status,plan))
        c.execute("INSERT INTO stripe_events(event_id,event_type) VALUES(?,?)",(eid,etype))
    return {"received":True,"duplicate":False}
