import pandas as pd
import numpy as np

def extract_features(candidate: dict, role_template: dict, jd_text: str = "") -> pd.Series:
    """
    Extract features from candidate profile dict for ML model inference/training.
    Returns a pandas Series with numerical features.
    """
    features = {}
    
    # 1. Experience
    req_years = role_template.get("required_years", 0)
    cand_years = candidate.get("experience_years", 0)
    features['exp_years'] = cand_years
    features['exp_gap'] = cand_years - req_years
    features['exp_ratio'] = cand_years / req_years if req_years > 0 else 1.0
    
    # 2. Skills
    cand_skills = set(s.lower() for s in candidate.get("skills", []))
    crit_skills = set(s.lower() for s in role_template.get("critical_skills", []))
    pref_certs = set(s.lower() for s in role_template.get("preferred_certs", []))
    
    features['num_skills'] = len(cand_skills)
    
    intersect_crit = cand_skills.intersection(crit_skills)
    features['critical_skill_match'] = len(intersect_crit)
    features['critical_skill_ratio'] = len(intersect_crit) / len(crit_skills) if len(crit_skills) > 0 else 0
    
    # 3. Projects & Companies
    features['num_projects'] = len(candidate.get("projects", []))
    features['num_companies'] = len(candidate.get("companies", []))
    
    avg_duration = 0
    companies = candidate.get("companies", [])
    if companies:
        avg_duration = sum(c.get("duration_months", 0) for c in companies) / len(companies)
    features['avg_tenure_months'] = avg_duration
    
    # 4. Education
    edu = candidate.get("education", {})
    features['gpa'] = edu.get("gpa", 0.0)
    features['is_stem'] = 1 if edu.get("is_stem", False) else 0
    
    # Degree level mapping
    deg_map = {"PhD": 4, "MTech": 3, "BTech": 2, "BSc": 2, "BDes": 2, "Diploma": 1}
    features['degree_level'] = deg_map.get(edu.get("degree", ""), 0)
    
    # 5. Certifications
    cand_certs = set(c.lower() for c in candidate.get("certifications", []))
    features['num_certs'] = len(cand_certs)
    features['pref_cert_match'] = len(cand_certs.intersection(pref_certs))
    
    # 6. Weights from role template (Contextual features)
    weights = role_template.get("competency_weights", {})
    features['weight_technical'] = weights.get("technical", 0.0)
    features['weight_experience'] = weights.get("experience", 0.0)
    features['weight_education'] = weights.get("education", 0.0)
    
    # Interaction terms
    features['exp_x_skill'] = features['exp_ratio'] * features['critical_skill_ratio']
    features['edu_x_skill'] = features['degree_level'] * features['critical_skill_ratio']
    
    return pd.Series(features)
