import os
import google.generativeai as genai
from datetime import datetime
from backend.ai_providers.base import AIProvider, ProviderHealth, ProviderStatus

class GoogleAIProvider(AIProvider):
    name = "google_ai"
    priority = 2
    
    _request_count = 0
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY", "")
        self.model_name = os.getenv("GOOGLE_AI_MODEL", "gemini-1.5-flash")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.free_limit = int(os.getenv("GOOGLE_AI_FREE_LIMIT", "1500"))

    async def generate_roadmap(self, skill_gaps: list[str], role: str, profile_summary: str, domain: str) -> str:
        prompt = (
            f"Role: {role}\n"
            f"Domain: {domain}\n"
            f"Profile Summary: {profile_summary}\n"
            f"Skill Gaps: {', '.join(skill_gaps)}\n\n"
            "Please generate a structured 30/60/90 day learning roadmap focusing on specific resources to address the skill gaps."
        )
        
        try:
            response = await self.model.generate_content_async(prompt)
            GoogleAIProvider._request_count += 1
            return response.text
        except Exception as e:
            raise e

    async def health_check(self) -> ProviderHealth:
        status = ProviderStatus.UNKNOWN
        error_msg = None
        try:
            # Lightweight check
            genai.get_model(f"models/{self.model_name}")
            status = ProviderStatus.AVAILABLE
        except Exception as e:
            status = ProviderStatus.UNAVAILABLE
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str:
                status = ProviderStatus.RATE_LIMITED
            error_msg = str(e)
            
        return ProviderHealth(
            provider_name=self.name,
            status=status,
            free_tier_used=GoogleAIProvider._request_count,
            free_tier_limit=self.free_limit,
            last_checked=datetime.utcnow(),
            error_message=error_msg
        )

    async def get_usage_stats(self) -> dict:
        return {
            "used": GoogleAIProvider._request_count,
            "limit": self.free_limit
        }
