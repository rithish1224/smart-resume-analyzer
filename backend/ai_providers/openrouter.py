import os
import openai
from datetime import datetime
from backend.ai_providers.base import AIProvider, ProviderHealth, ProviderStatus

class OpenRouterProvider(AIProvider):
    name = "openrouter"
    priority = 1
    
    _request_count = 0
    
    def __init__(self):
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-pro")
        self.free_limit = int(os.getenv("OPENROUTER_FREE_LIMIT", "1000"))
        
        self.client = openai.AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    async def generate_roadmap(self, skill_gaps: list[str], role: str, profile_summary: str, domain: str) -> str:
        prompt = (
            f"Role: {role}\n"
            f"Domain: {domain}\n"
            f"Profile Summary: {profile_summary}\n"
            f"Skill Gaps: {', '.join(skill_gaps)}\n\n"
            "Please generate a structured 30/60/90 day learning roadmap focusing on specific resources to address the skill gaps."
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            OpenRouterProvider._request_count += 1
            return response.choices[0].message.content or ""
        except openai.RateLimitError:
            raise
        except openai.APIError:
            raise

    async def health_check(self) -> ProviderHealth:
        status = ProviderStatus.UNKNOWN
        error_msg = None
        try:
            # Lightweight check: models list
            await self.client.models.list()
            status = ProviderStatus.AVAILABLE
        except openai.RateLimitError as e:
            status = ProviderStatus.RATE_LIMITED
            error_msg = str(e)
        except Exception as e:
            status = ProviderStatus.UNAVAILABLE
            error_msg = str(e)
            
        return ProviderHealth(
            provider_name=self.name,
            status=status,
            free_tier_used=OpenRouterProvider._request_count,
            free_tier_limit=self.free_limit,
            last_checked=datetime.utcnow(),
            error_message=error_msg
        )

    async def get_usage_stats(self) -> dict:
        return {
            "used": OpenRouterProvider._request_count,
            "limit": self.free_limit
        }
