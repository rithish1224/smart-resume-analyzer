from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ProviderStatus(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

@dataclass
class ProviderHealth:
    provider_name: str
    status: ProviderStatus
    free_tier_used: int
    free_tier_limit: int
    last_checked: datetime
    error_message: str | None = None

class AIProvider(ABC):
    name: str
    priority: int  # Lower = higher priority
    
    @abstractmethod
    async def generate_roadmap(self, skill_gaps: list[str], role: str, profile_summary: str, domain: str) -> str: ...
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth: ...
    
    @abstractmethod
    async def get_usage_stats(self) -> dict: ...
    
    async def is_available(self) -> bool:
        health = await self.health_check()
        return health.status == ProviderStatus.AVAILABLE
