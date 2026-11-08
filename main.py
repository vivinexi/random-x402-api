
import os
import random

from fastapi import FastAPI, Query
from x402.http import (
    FacilitatorConfig,
    HTTPFacilitatorClient,
    PaymentOption,
)
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.schemas import Network
from x402.server import x402ResourceServer

PAY_TO = os.environ["PAY_TO"]
FACILITATOR_URL = os.getenv(
    "FACILITATOR_URL",
    "https://facilitator.payai.network"
)
PRICE = os.getenv("API_PRICE", "$0.001")

NETWORK: Network = "eip155:8453"

app = FastAPI(
    title="Random Data API",
    description="Paid Random Data API powered by x402",
    version="1.0.0"
)

facilitator = HTTPFacilitatorClient(
    FacilitatorConfig(url=FACILITATOR_URL)
)

server = x402ResourceServer(facilitator)
server.register(NETWORK, ExactEvmServerScheme())

routes = {
    "GET /random": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=PAY_TO,
                price=PRICE,
                network=NETWORK,
            )
        ],
        mime_type="application/json",
        description="Generate random numbers",
    ),
    "GET /quote": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=PAY_TO,
                price=PRICE,
                network=NETWORK,
            )
        ],
        mime_type="application/json",
        description="Get a random inspirational quote",
    ),
}

app.add_middleware(
    PaymentMiddlewareASGI,
    routes=routes,
    server=server
)

QUOTES = [
    {
        "text": "Never stop learning.",
        "author": "Unknown"
    },
    {
        "text": "Success starts with action.",
        "author": "Unknown"
    },
    {
        "text": "Small steps lead to big results.",
        "author": "Unknown"
    },
    {
        "text": "Believe in yourself.",
        "author": "Unknown"
    },
    {
        "text": "Dream big and work hard.",
        "author": "Unknown"
    },
]

@app.get("/")
async def home():
    return {
        "name": "Random Data API",
        "version": "1.0.0",
        "network": "Base Mainnet",
        "payment": "USDC x402",
        "endpoints": [
            "/health",
            "/random?count=3",
            "/quote"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/random")
async def random_numbers(
    count: int = Query(default=1, ge=1, le=10)
):
    return {
        "count": count,
        "numbers": [
            random.randint(0, 1000000)
            for _ in range(count)
        ]
    }

@app.get("/quote")
async def random_quote():
    return random.choice(QUOTES)
