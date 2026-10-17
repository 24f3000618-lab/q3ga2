import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# ====== CHANGE THIS to your logged-in email, exactly as shown ======
EMAIL = "24f3000618@ds.study.iitm.ac.in"
# ===================================================================

ALLOWED_ORIGIN = "https://dash-wqf5el.example.com"

app = FastAPI()

# The bouncer: only ALLOWED_ORIGIN gets in. No "*" wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# The name-tag stamper. It's added AFTER the CORS bouncer on purpose,
# so it wraps around everything and stamps preflight replies too.
@app.middleware("http")
async def add_tracking_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
def stats(values: str = ""):
    try:
        numbers = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")

    if not numbers:
        raise HTTPException(status_code=400, detail="provide at least one value")

    total = sum(numbers)
    count = len(numbers)
    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count,
    }