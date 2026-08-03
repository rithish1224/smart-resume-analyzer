import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any
from xgboost import XGBRanker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.config import settings
from backend.schemas import CandidateProfileSchema

class CandidateScorer:
    def __init__(self):
        self.model = None
        model_path = getattr(settings, "MODEL_PATH", "xgb_ranker.json")
        if os.path.exists(model_path):
            try:
                self.model = XGBRanker()
                self.model.load_model(model_path)
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None

        self.role_templates = {}
        self.skill_taxonomy = []
        
        self._load_data()

    def _load_data(self):
        # Mock load from data directory
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        templates_path = os.path.join(data_dir, "role_templates.json")
        taxonomy_path = os.path.join(data_dir, "skill_taxonomy.json")
        
        if os.path.exists(templates_path):
            with open(templates_path, "r") as f:
                self.role_templates = json.load(f)
        else:
            self.role_templates = {"software_engineer": {"skills": ["python", "java", "sql"], "years_required": 3}}
            
        if os.path.exists(taxonomy_path):
            with open(taxonomy_path, "r") as f:
                self.skill_taxonomy = json.load(f)

    def _extract_features(self, profile: CandidateProfileSchema, role: str, jd_text: str, domain: str) -> Dict[str, float]:
        features = {}
        role_data = self.role_templates.get(role, {"skills": [], "years_required": 1})
        req_skills = set([s.lower() for s in role_data.get("skills", [])])
        cand_skills = set([s.lower() for s in profile.skills])
        
        # Skill Match Ratio
        intersection = req_skills.intersection(cand_skills)
        features["skill_match_ratio"] = len(intersection) / len(req_skills) if req_skills else 1.0
        
        # Required Skill Coverage
        features["required_skill_coverage"] = features["skill_match_ratio"] # Simplified
        
        # Recency Weighted Score (Mock implementation)
        features["recency_weighted_score"] = len(cand_skills) * 0.8
        
        features["missing_critical_count"] = max(0, len(req_skills) - len(intersection))
        
        cand_years = getattr(profile, "experience_years", 2)
        req_years = role_data.get("years_required", 1)
        features["experience_ratio"] = cand_years / req_years if req_years else 1.0
        
        features["tenure_stability_index"] = 2.0 / (1.5 + 1)
        features["career_progression"] = 2.0
        features["employment_gap_months"] = 0.0
        features["education_tier"] = 3.0 # Masters
        features["gpa_normalized"] = 0.8
        features["is_stem_field"] = 1.0
        features["project_count"] = len(profile.projects_raw.split("\n")) if profile.projects_raw else 0
        features["tech_diversity_score"] = min(1.0, len(cand_skills) / 20.0)
        features["cert_count"] = len(profile.certifications_raw.split("\n")) if profile.certifications_raw else 0
        features["cert_relevance_score"] = 0.5
        
        # TF-IDF
        if jd_text and profile.raw_text:
            vec = TfidfVectorizer(stop_words='english')
            tfidf = vec.fit_transform([jd_text, profile.raw_text])
            features["jd_tfidf_similarity"] = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        else:
            features["jd_tfidf_similarity"] = 0.0
            
        features["domain_match_flag"] = 1.0 if domain.lower() in profile.raw_text.lower() else 0.0
        features["domain_experience_years"] = cand_years if features["domain_match_flag"] else 0.0
        features["skill_count"] = len(cand_skills)
        features["education_institution_tier"] = 0.7
        
        return features

    def score(self, profile: CandidateProfileSchema, role: str, jd_text: str, domain: str) -> Dict[str, Any]:
        features = self._extract_features(profile, role, jd_text, domain)
        
        # Rule-based score
        rule_score = (
            features["skill_match_ratio"] * 30 +
            min(1.0, features["experience_ratio"]) * 30 +
            (features["education_tier"] / 4.0) * 25 +
            min(1.0, features["project_count"] / 5.0) * 15
        )
        
        alpha = 0.7
        if self.model:
            # Mock XGBoost prediction
            df = pd.DataFrame([features])
            xgb_raw = self.model.predict(df)[0]
            # Sigmoid normalization mock
            xgb_score = (1 / (1 + np.exp(-xgb_raw))) * 100
        else:
            xgb_score = rule_score
            alpha = 0.0
            
        final_score = (alpha * xgb_score) + ((1 - alpha) * rule_score)
        
        return {
            "final_score": min(100.0, max(0.0, final_score)),
            "confidence": 0.85,
            "shortlist_decision": final_score > 70.0,
            "features": features,
            "rule_scores": rule_score,
            "competency_scores": {
                "technical": features["skill_match_ratio"] * 100,
                "experience": min(100.0, features["experience_ratio"] * 100),
                "education": (features["education_tier"] / 4.0) * 100,
                "projects": min(100.0, features["project_count"] * 20),
                "certifications": min(100.0, features["cert_count"] * 25),
                "communication": 80.0
            }
        }
