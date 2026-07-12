import os
import time
import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google import genai
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="VidInsight Commercial Core Engine", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class ResearchRequest(BaseModel):
    video_url: str
    language: str

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "Gemini-2.5-Flash-Enterprise"}

async def get_gemini_report(video_url: str, target_language: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key missing on server setup!")
    
    client = genai.Client(api_key=api_key)
    prompt = f"Analyze this YouTube URL directly: {video_url}. Generate a 100-year deep historical research and truth verification report strictly in the '{target_language}' language. Structure it with Executive Summary, 100-Year History, Technical Verification, and Damage Risk Mitigation Solutions."
    
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    )
    return response.text

@app.post("/api/v1/analyze")
@limiter.limit("30/minute")
async def analyze_video(request: ResearchRequest, fastapi_req: Request):
    if not request.video_url or not request.language:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    try:
        start_time = time.time()
        report_output = await get_gemini_report(request.video_url, request.language)
        execution_time = time.time() - start_time
        return {
            "status": "success",
            "latency_seconds": round(execution_time, 2),
            "report": report_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enterprise Engine Failure: {str(e)}")
