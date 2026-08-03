from typing import List, Dict, Any
from backend.schemas import CandidateProfileSchema

class RoadmapService:
    def generate(self, skill_gaps: List[Dict[str, Any]], profile: CandidateProfileSchema, role: str, provider: str = "internal") -> Dict[str, Any]:
        """
        Generate a learning roadmap based on skill gaps.
        """
        milestone_30 = []
        milestone_60 = []
        milestone_90 = []
        
        for gap in skill_gaps:
            if gap["category"] == "✅ MET":
                continue
                
            task = {
                "skill": gap["skill"],
                "resource_type": "Course",
                "estimated_hours": 20 if gap["is_critical"] else 10,
                "resource_url": f"https://learning.platform/search?q={gap['skill']}"
            }
            
            if gap["category"] == "⚠️ SOFT":
                milestone_30.append(task)
            elif gap["category"] == "❌ HARD":
                # Medium priority goes to 60 days, highest priority goes to 90 days? 
                # According to prompt: 30-day (quick wins: soft gaps), 60-day (medium: core skill gaps), 90-day (hard: critical gaps)
                if gap.get("priority_score", 0) > 0.8:
                    milestone_90.append(task)
                else:
                    milestone_60.append(task)
                    
        return {
            "role": role,
            "provider": provider,
            "milestones": {
                "30_days": {"title": "Quick Wins", "tasks": milestone_30},
                "60_days": {"title": "Core Skills", "tasks": milestone_60},
                "90_days": {"title": "Advanced/Critical Gaps", "tasks": milestone_90}
            }
        }
