from threading import Lock

from fastapi import FastAPI, HTTPException

from query_layer.models import (
    AskRequest,
    AskResponse,
)
import traceback
from query_layer.service import ask_census_with_metadata
import time
from pathlib import Path

from fastapi.responses import FileResponse

WEB_DIR = Path(__file__).resolve().parent / "web"
INDEX_FILE = WEB_DIR / "index.html"


app = FastAPI(
    title="Pakistan Census Research API",
    version="0.1.0",
    description=(
        "Controlled natural-language access to validated "
        "Pakistan Census analytical models."
    ),
)

query_lock = Lock()


@app.get("/")
def home() -> FileResponse:
    return FileResponse(INDEX_FILE)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(request: AskRequest) -> AskResponse:
    started = time.perf_counter()
    try:
        with query_lock:
            (
                plan,
                result,
                answer,
                interpretation,
                timings,
            ) = ask_census_with_metadata(
                request.question,
                previous_query=request.previous_query,
            )

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Census query failed.",
        ) from exc

    elapsed_seconds = time.perf_counter() - started

    return AskResponse(
        status=plan.status,
        plan=plan,
        result=result,
        answer=answer,
        interpretation=interpretation,
        timings=timings,
        elapsed_seconds=elapsed_seconds,
    )