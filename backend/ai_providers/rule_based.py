import json
import os
from datetime import datetime
from backend.ai_providers.base import AIProvider, ProviderHealth, ProviderStatus

class RuleBasedProvider(AIProvider):
    name = "rule_based"
    priority = 3
    
    def __init__(self):
        self.course_catalog_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "course_catalog.json")
        self.role_templates_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "role_templates.json")
        self._load_data()

    def _load_data(self):
        self.catalog = {}
        if os.path.exists(self.course_catalog_path):
            with open(self.course_catalog_path, "r") as f:
                self.catalog = json.load(f)
                
        self.templates = {}
        if os.path.exists(self.role_templates_path):
            with open(self.role_templates_path, "r") as f:
                self.templates = json.load(f)

    async def generate_roadmap(self, skill_gaps: list[str], role: str, profile_summary: str, domain: str) -> str:
        roadmap = f"# Offline Learning Roadmap for {role} ({domain})\n\n"
        
        roadmap += "## 30 Days (Foundations)\n"
        for gap in skill_gaps[:2]:
            roadmap += f"- Learn {gap}: Focus on core concepts and basic applications.\n"
            
        roadmap += "\n## 60 Days (Intermediate)\n"
        for gap in skill_gaps[2:4]:
            roadmap += f"- Deep dive into {gap}: Work on hands-on exercises.\n"
            
        roadmap += "\n## 90 Days (Advanced)\n"
        for gap in skill_gaps[4:]:
            roadmap += f"- Master {gap}: Build a comprehensive project integrating these skills.\n"
            
        return roadmap

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.name,
            status=ProviderStatus.AVAILABLE,
            free_tier_used=0,
            free_tier_limit=0, # Logically unlimited
            last_checked=datetime.utcnow(),
            error_message=None
        )

    async def get_usage_stats(self) -> dict:
        return {
            "used": 0,
            "limit": "unlimited"
        }
