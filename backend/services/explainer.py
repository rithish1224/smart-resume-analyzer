import pandas as pd
from typing import Dict, Any, List
try:
    import shap
except ImportError:
    shap = None

class SHAPExplainer:
    def explain(self, model: Any, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate SHAP explanations for the candidate features.
        """
        if model is None or shap is None:
            return {"base_score": 0.0, "waterfall": [], "top_positive": [], "top_negative": []}

        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features_df)
            
            # For a single prediction
            sv = shap_values[0] if isinstance(shap_values, list) else shap_values
            if len(sv.shape) > 1:
                sv = sv[0]
                
            base_value = explainer.expected_value
            if isinstance(base_value, list) or isinstance(base_value, np.ndarray):
                base_value = base_value[0]

            feature_names = features_df.columns.tolist()
            feature_values = features_df.iloc[0].tolist()
            
            # Map machine names to human readable
            name_mapping = {
                "skill_match_ratio": "Skill Match %",
                "experience_ratio": "Experience Match",
                "education_tier": "Education Level",
                "project_count": "Projects Completed",
                "jd_tfidf_similarity": "JD Similarity"
            }
            
            waterfall = []
            for i in range(len(feature_names)):
                name = feature_names[i]
                display = name_mapping.get(name, name.replace("_", " ").title())
                waterfall.append({
                    "feature": name,
                    "shap_value": float(sv[i]),
                    "feature_value": float(feature_values[i]),
                    "display_name": display,
                    "evidence": f"Impacted score by {float(sv[i]):.2f} based on value {float(feature_values[i]):.2f}"
                })
                
            # Sort by absolute SHAP value
            waterfall.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
            
            positives = sorted([x for x in waterfall if x["shap_value"] > 0], key=lambda x: x["shap_value"], reverse=True)
            negatives = sorted([x for x in waterfall if x["shap_value"] < 0], key=lambda x: x["shap_value"])
            
            return {
                "base_score": float(base_value),
                "waterfall": waterfall,
                "top_positive": positives[:3],
                "top_negative": negatives[:3]
            }
        except Exception as e:
            return {"error": str(e), "base_score": 0.0, "waterfall": [], "top_positive": [], "top_negative": []}
