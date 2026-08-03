import logging
from typing import Any
from backend.ai_providers.base import AIProvider, ProviderStatus
from backend.ai_providers.openrouter import OpenRouterProvider
from backend.ai_providers.google_ai import GoogleAIProvider
from backend.ai_providers.rule_based import RuleBasedProvider
from backend.ai_providers.health_check import health_checker

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self, fallback_enabled: bool = True):
        self.fallback_enabled = fallback_enabled
        
        self.providers: list[AIProvider] = [
            OpenRouterProvider(),
            GoogleAIProvider(),
            RuleBasedProvider()
        ]
        
        # Ensure providers are sorted by priority (lowest integer is highest priority)
        self.providers.sort(key=lambda p: p.priority)

    async def route_request(self, **kwargs) -> tuple[str, str]:
        """
        Routes the request to generate a roadmap.
        Returns a tuple of (result_text, provider_name_used).
        """
        for provider in self.providers:
            # Skip non-rule-based providers if they aren't the primary and fallback is disabled
            if provider.name != "rule_based" and not self.fallback_enabled:
                if provider != self.providers[0]:
                    continue

            try:
                # Check health; rule_based is always considered available as fallback
                is_available = await provider.is_available()
                if is_available or provider.name == "rule_based":
                    logger.info(f"Attempting roadmap generation with provider: {provider.name}")
                    result = await provider.generate_roadmap(**kwargs)
                    return result, provider.name
            except Exception as e:
                logger.error(f"Provider {provider.name} failed: {e}")
                if not self.fallback_enabled:
                    break
                    
        # Ultimate fallback if loop exhausts and nothing returned
        rule_based = next((p for p in self.providers if p.name == "rule_based"), None)
        if rule_based:
            try:
                result = await rule_based.generate_roadmap(**kwargs)
                return result, rule_based.name
            except Exception as e:
                logger.error(f"Ultimate fallback to Rule based provider failed: {e}")
                
        return "Failed to generate roadmap. All providers are currently unavailable.", "none"
        
    async def get_status(self) -> dict[str, Any]:
        """
        Returns status of all providers for UI display.
        """
        health_results = await health_checker.check_all_providers(self.providers)
        return {name: health.status.value for name, health in health_results.items()}

# Singleton instance
ai_router = AIRouter()
