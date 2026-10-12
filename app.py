from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl

from modules.scraper import ScrapeError
from modules.file_extractor import FileExtractionError, extract_file_text, posting_from_text
from score_url import score_live_posting
from scoring import score_posting

app = FastAPI(title="InternWorth API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
FRONTEND = Path(__file__).parent / "frontend"
app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")

CACHE_TTL_SECONDS = 15 * 60
_url_cache: dict[str, tuple[float, dict]] = {}


class UrlRequest(BaseModel):
    url: HttpUrl


class PostingRequest(BaseModel):
    title: str = Field(default="Internship opportunity", max_length=200)
    company: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=200)
    stipend: str = Field(default="", max_length=200)
    description: str = Field(min_length=20, max_length=30000)
    company_info: str = Field(default="", max_length=5000)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "cache_entries": len(_url_cache)}


@app.post("/score")
def score_url(payload: UrlRequest) -> dict:
    url = str(payload.url)
    if urlparse(url).scheme not in {"http", "https"}:
        raise HTTPException(status_code=422, detail="Please submit an http or https URL.")
    cached = _url_cache.get(url)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return {**cached[1], "cached": True}
    try:
        result = score_live_posting(url)
    except ScrapeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    _url_cache[url] = (time.time(), result)
    return {**result, "cached": False}


@app.post("/score/manual")
def score_manual(payload: PostingRequest) -> dict:
    return {**score_posting(payload.model_dump()), "cached": False, "manual": True}


@app.post("/score/file")
async def score_file(file: UploadFile = File(...)) -> dict:
    filename = file.filename or "upload"
    try:
        text = extract_file_text(filename, await file.read())
        result = score_posting(posting_from_text(text))
    except FileExtractionError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {**result, "cached": False, "uploaded_file": filename}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")
