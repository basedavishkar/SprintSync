import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.database_models import User
from google import genai

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])


class SuggestRequest(BaseModel):
    title: str = None
    mode: str = "draft"  # "draft" or "plan"


class SuggestResponse(BaseModel):
    suggestion: str


def get_gemini_client():
    """Get Gemini client with API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    return genai.Client(api_key=api_key)


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_task(
    req: SuggestRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered task suggestion endpoint."""
    
    # Check if we have API key for real AI calls
    gemini_client = get_gemini_client()
    
    use_real_ai = os.getenv("USE_REAL_AI", "false").lower() == "true"
    
    if gemini_client and use_real_ai:
        # Real AI call with Gemini 2.5 Flash
        try:
            if req.mode == "draft" and req.title:
                title = req.title
                prompt = f"""Draft a professional task description for: {title}
                
                Requirements:
                - Be concise but comprehensive
                - Focus on technical implementation details
                - Use professional language
                - Include acceptance criteria if relevant
                
                Description:"""
                
                response = gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                return SuggestResponse(suggestion=response.text)
            else:
                username = current_user.username
                prompt = f"""Create a concise daily plan for user {username}.
                
                Focus on:
                - Priority tasks for today
                - Time estimates
                - Key deliverables
                - Blockers to address
                
                Daily Plan:"""
                
                response = gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                return SuggestResponse(suggestion=response.text)
                
        except Exception:
            # Fallback to stub if AI call fails
            if req.mode == "draft" and req.title:
                return SuggestResponse(
                    suggestion=f"[FALLBACK] Description for: {req.title}"
                )
            else:
                username = current_user.username
                return SuggestResponse(
                    suggestion=f"[FALLBACK] Plan for user: {username}"
                )
    
    # Deterministic stub for tests/CI
    if req.mode == "draft" and req.title:
        return SuggestResponse(
            suggestion=f"[STUB] Description for: {req.title}"
        )
    else:
        username = current_user.username
        return SuggestResponse(
            suggestion=f"[STUB] Plan for user: {username}"
        ) 