import asyncio
from datetime import datetime, timedelta
from backend.ai_providers.base import AIProvider, ProviderHealth

class HealthChecker:
    def __init__(self):
        self._cache: dict[str, tuple[ProviderHealth, datetime]] = {}
        self._cache_ttl = 60  # Cache health check for 60 seconds

    async def check_all_providers(self, providers: list[AIProvider]) -> dict[str, ProviderHealth]:
        now = datetime.utcnow()
        results = {}
        
        for provider in providers:
            if provider.name in self._cache:
                cached_health, timestamp = self._cache[provider.name]
                if (now - timestamp).total_seconds() < self._cache_ttl:
                    results[provider.name] = cached_health
                    continue
                    
            # Need to fetch fresh health status
            health = await provider.health_check()
            self._cache[provider.name] = (health, now)
            results[provider.name] = health
            
        return results

    async def background_task(self, providers: list[AIProvider]):
        while True:
            await self.check_all_providers(providers)
            await asyncio.sleep(300)  # Check every 5 minutes

health_checker = HealthChecker()

def start_background_health_check(providers: list[AIProvider]):
    asyncio.create_task(health_checker.background_task(providers))
