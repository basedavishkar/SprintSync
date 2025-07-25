import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from typing import Optional
import requests

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])

class SuggestRequest(BaseModel):
    title: Optional[str] = None
    mode: Optional[str] = "draft"  # "draft" or "plan"

class SuggestResponse(BaseModel):
    suggestion: str

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/suggest", response_model=SuggestResponse)
def ai_suggest(
    req: SuggestRequest, current_user=Depends(get_current_user)
):
    if OPENAI_API_KEY:
        # Real LLM call (OpenAI)
        if req.mode == "draft" and req.title:
            prompt = f"Draft a concise, clear task description for: {req.title}"
        else:
            prompt = f"Give a concise daily plan for user: {current_user.username}"
        try:
            response = requests.post(
                "https://api.openai.com/v1/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "text-davinci-003",
                    "prompt": prompt,
                    "max_tokens": 60,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            suggestion = data["choices"][0]["text"].strip()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM error: {e}")
        return SuggestResponse(suggestion=suggestion)
    else:
        # Deterministic stub for tests/CI
        if req.mode == "draft" and req.title:
            return SuggestResponse(suggestion=f"[STUB] Description for: {req.title}")
        else:
            return SuggestResponse(suggestion=f"[STUB] Plan for user: {current_user.username}") 