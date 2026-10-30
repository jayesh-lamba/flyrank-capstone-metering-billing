import os,tempfile,unittest
from fastapi.testclient import TestClient
from app import config
# isolate test database
_tmp=tempfile.mktemp(suffix=".db")
config.DATABASE_URL="sqlite:///"+_tmp
from app.main import app
client=TestClient(app)
class BillingTests(unittest.TestCase):
    def setUp(self):
        with client:
            pass
        client.post("/tenants",json={"id":"t1","name":"Tenant One"})
    def test_idempotency(self):
        body={"tenant_id":"t1","usage_type":"api_calls","quantity":1,"idempotency_key":"same"}
        a=client.post("/usage/record",json=body).json();b=client.post("/usage/record",json=body).json()
        self.assertFalse(a["duplicate"]);self.assertTrue(b["duplicate"])
        self.assertEqual(client.get("/usage/t1").json()["api_calls"]["used"],1)
    def test_quota_boundary(self):
        client.post("/usage/record",json={"tenant_id":"t1","usage_type":"api_calls","quantity":1000,"idempotency_key":"bulk"})
        r=client.post("/usage/record",json={"tenant_id":"t1","usage_type":"api_calls","quantity":1,"idempotency_key":"over"})
        self.assertEqual(r.status_code,429)
    def test_money_math(self):
        # 800 fresh input + 200 cached input; 100 output incl. reasoning tokens
        self.assertEqual(__import__("app.billing",fromlist=["token_cost_micro_usd"]).token_cost_micro_usd(1000,200,100,40),800+50+400)
if __name__=="__main__":unittest.main()
