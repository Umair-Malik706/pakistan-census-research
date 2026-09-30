from threading import Lock

from fastapi import FastAPI, HTTPException

from query_layer.models import (
    AskRequest,
    AskResponse,
)
from query_layer.service import ask_census


app = FastAPI(
    title="Pakistan Census Research API",
    version="0.1.0",
    description=(
        "Controlled natural-language access to validated "
        "Pakistan Census analytical models."
    ),
)

query_lock = Lock()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(request: AskRequest) -> AskResponse:
    try:
        with query_lock:
            plan, result, answer = ask_census(
                request.question
            )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Census query failed.",
        ) from exc

    return AskResponse(
        status=plan.status,
        plan=plan,
        result=result,
        answer=answer,
    )