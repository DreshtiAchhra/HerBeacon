"""FastAPI HTTP bridge for the existing HerBeacon analysis engine."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.pipeline import HerBeaconAnalysisEngine


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    conversation_id: str = Field(default="custom_text", min_length=1, max_length=200)


class MessageAnalysisRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., min_length=1)
    conversation_id: str = Field(default="custom_conversation", min_length=1, max_length=200)


app = FastAPI(
    title="HerBeacon Behavioural Safety API",
    version="1.0.0",
    description="A thin HTTP bridge over the existing HerBeacon AI engine.",
)

configured_origins = os.getenv(
    "HERBEACON_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "herbeacon-api"}


@app.post("/api/analyze/text")
def analyze_text(request: TextAnalysisRequest) -> Dict[str, Any]:
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Conversation text cannot be empty.")
    try:
        return HerBeaconAnalysisEngine().analyze_text(
            request.text,
            conversation_id=request.conversation_id,
        )
    except (ValueError, TypeError, OSError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=f"Conversation could not be analyzed: {exc}") from exc


@app.post("/api/analyze")
def analyze(request: TextAnalysisRequest) -> Dict[str, Any]:
    """Primary text-analysis endpoint used by the React client."""
    return analyze_text(request)


@app.post("/api/analyze/messages")
def analyze_messages(request: MessageAnalysisRequest) -> Dict[str, Any]:
    if not request.messages:
        raise HTTPException(status_code=422, detail="At least one message is required.")
    try:
        return HerBeaconAnalysisEngine().analyze_messages(
            request.messages,
            conversation_id=request.conversation_id,
        )
    except (ValueError, TypeError, OSError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=f"Messages could not be analyzed: {exc}") from exc


@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A conversation file is required.")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=422, detail="Uploaded conversation is empty.")
    suffix = Path(file.filename).suffix or ".txt"
    temporary_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary.write(contents)
            temporary_path = temporary.name
        result = HerBeaconAnalysisEngine().analyze_file(temporary_path)
        if isinstance(result, dict):
            result["conversation_id"] = file.filename
        return result
    except (ValueError, TypeError, OSError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=f"File could not be analyzed: {exc}") from exc
    finally:
        if temporary_path:
            try:
                Path(temporary_path).unlink(missing_ok=True)
            except OSError:
                pass
