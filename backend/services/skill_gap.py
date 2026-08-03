from typing import List, Dict, Any
from backend.schemas import CandidateProfileSchema

class SkillGapAnalyzer:
    def analyze(self, profile: CandidateProfileSchema, role: str, domain: str, feature_importances: Dict[str, float]) -> List[Dict[str, Any]]:
        # Mock role template data
        role_templates = {
            "software_engineer": {
                "critical": ["python", "sql", "api"],
                "optional": ["docker", "kubernetes", "aws"]
            }
        }
        
        template = role_templates.get(role, {"critical": [], "optional": []})
        req_critical = set([s.lower() for s in template.get("critical", [])])
        req_optional = set([s.lower() for s in template.get("optional", [])])
        
        cand_skills = set([s.lower() for s in profile.skills])
        
        gaps = []
        
        # Analyze critical gaps
        for skill in req_critical:
            if skill not in cand_skills:
                gaps.append({
                    "skill": skill,
                    "category": "❌ HARD",
                    "priority_score": 0.9,
                    "is_critical": True,
                    "description": f"Critical missing skill: {skill}"
                })
            else:
                gaps.append({
                    "skill": skill,
                    "category": "✅ MET",
                    "priority_score": 0.0,
                    "is_critical": True,
                    "description": f"Skill met: {skill}"
                })
                
        # Analyze optional gaps
        for skill in req_optional:
            if skill not in cand_skills:
                gaps.append({
                    "skill": skill,
                    "category": "⚠️ SOFT",
                    "priority_score": 0.5,
                    "is_critical": False,
                    "description": f"Optional missing skill: {skill}"
                })
                
        # Sort by priority
        gaps.sort(key=lambda x: x["priority_score"], reverse=True)
        return gaps
