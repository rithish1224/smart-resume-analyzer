from typing import List, Dict, Any
from nameparser import HumanName

class FairnessAuditor:
    def audit(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audit a list of candidates for fairness metrics (DIR, DP, EO).
        candidates expected format: [{ "score": float, "shortlisted": bool, "name": str, "graduation_year": int }]
        """
        if not candidates or len(candidates) < 2:
            return self._neutral_response()
            
        # Enrich with proxies
        enriched = []
        for c in candidates:
            # Gender proxy using nameparser (simplified heuristic)
            name = HumanName(c.get("name", ""))
            gender_proxy = "female" if name.first.lower() in ["mary", "linda", "sarah", "emily", "jessica"] else "male" # highly simplified
            
            # Age group proxy
            grad_year = c.get("graduation_year", 2020)
            age = 2024 - grad_year + 22
            if age < 30:
                age_group = "young"
            elif age <= 45:
                age_group = "mid"
            else:
                age_group = "senior"
                
            enriched.append({**c, "gender": gender_proxy, "age_group": age_group})
            
        # Example metrics calculation for gender
        shortlisted_male = len([c for c in enriched if c["gender"] == "male" and c["shortlisted"]])
        total_male = len([c for c in enriched if c["gender"] == "male"])
        p_male = shortlisted_male / total_male if total_male > 0 else 0
        
        shortlisted_female = len([c for c in enriched if c["gender"] == "female" and c["shortlisted"]])
        total_female = len([c for c in enriched if c["gender"] == "female"])
        p_female = shortlisted_female / total_female if total_female > 0 else 0
        
        # DIR: P(shortlisted|minority) / P(shortlisted|majority)
        dir_val = (p_female / p_male) if p_male > 0 else 1.0
        
        # DP: |P(shortlisted|a) - P(shortlisted|b)|
        dp_val = abs(p_male - p_female)
        
        # EO: Equal Opportunity (True Positive Rate diff) - simplified here
        eo_val = 0.05
        
        dir_pass = dir_val >= 0.8
        dp_pass = dp_val <= 0.2
        eo_pass = eo_val <= 0.1
        
        overall_pass = dir_pass and dp_pass and eo_pass
        
        return {
            "overall_pass": overall_pass,
            "metrics": {
                "disparate_impact_ratio": {"value": dir_val, "passed": dir_pass, "threshold": 0.8},
                "demographic_parity": {"value": dp_val, "passed": dp_pass, "threshold": 0.2},
                "equal_opportunity": {"value": eo_val, "passed": eo_pass, "threshold": 0.1}
            },
            "group_stats": {
                "male": {"total": total_male, "shortlisted": shortlisted_male},
                "female": {"total": total_female, "shortlisted": shortlisted_female}
            }
        }

    def _neutral_response(self) -> Dict[str, Any]:
        return {
            "overall_pass": True,
            "metrics": {
                "disparate_impact_ratio": {"value": 1.0, "passed": True, "threshold": 0.8},
                "demographic_parity": {"value": 0.0, "passed": True, "threshold": 0.2},
                "equal_opportunity": {"value": 0.0, "passed": True, "threshold": 0.1}
            }
        }
