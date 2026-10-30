import os
from dotenv import load_dotenv
load_dotenv()
STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY","")
STRIPE_WEBHOOK_SECRET=os.getenv("STRIPE_WEBHOOK_SECRET","")
STRIPE_PRICE_ID_PRO=os.getenv("STRIPE_PRICE_ID_PRO","")
APP_BASE_URL=os.getenv("APP_BASE_URL","http://localhost:8000")
DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./data/billing.db")
# Illustrative pinned prices; integer micro-dollars per 1M tokens.
PRICING={
    "input_per_million_micro_usd": 1_000_000,
    "cached_input_per_million_micro_usd": 250_000,
    "output_per_million_micro_usd": 4_000_000,
}
PLANS={
    "free":{"api_calls":1000,"ai_tokens":100_000},
    "pro":{"api_calls":100_000,"ai_tokens":10_000_000},
}
