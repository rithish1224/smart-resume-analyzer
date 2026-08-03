import pytest

# Dummy scorer functions for tests
def extract_features(profile):
    return {"experience_years": 5, "education_level": 3, "skill_match": 0.8}

def rule_based_score(features):
    return min((features["experience_years"] * 10) + (features["skill_match"] * 100), 100)

def should_shortlist(score):
    return score >= 75.0

def test_feature_extraction():
    profile = {"skills": ["Python"], "experience": "5 years"}
    features = extract_features(profile)
    assert "experience_years" in features
    assert features["experience_years"] == 5

def test_rule_based_scoring():
    features = {"experience_years": 2, "education_level": 2, "skill_match": 0.5}
    score = rule_based_score(features)
    assert score == 70.0

def test_score_range():
    features_high = {"experience_years": 20, "skill_match": 1.0, "education_level": 4}
    score_high = rule_based_score(features_high)
    assert score_high <= 100.0
    
    features_low = {"experience_years": 0, "skill_match": 0.0, "education_level": 1}
    score_low = rule_based_score(features_low)
    assert score_low >= 0.0

def test_shortlist_decision_threshold():
    assert should_shortlist(80.0) is True
    assert should_shortlist(70.0) is False
    assert should_shortlist(75.0) is True
