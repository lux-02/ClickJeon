from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routers.analyze import router as analyze_router
from utils.rate_limit import get_client_ip

limiter = Limiter(key_func=get_client_ip)

app = FastAPI(title="ClickJeon API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://[a-z]+",
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

app.include_router(analyze_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


