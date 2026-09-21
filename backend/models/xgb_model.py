import os
import json
import logging
import xgboost as xgb
import pandas as pd
from typing import Any, Tuple

logger = logging.getLogger(__name__)

class XGBRankerModel:
    """Wrapper class for XGBoost Ranker model."""
    
    def __init__(self):
        self.model: xgb.Booster | None = None
        self.classifier: Any | None = None
        self.feature_names: list[str] = []
        self.version: str = ''
        self.model_kind: str = "ranker"
        
    def load(self, model_path: str) -> bool:
        """Load the XGBoost model from the specified path."""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"Model path does not exist: {model_path}")
                return False
                
            metadata_path = os.path.join(os.path.dirname(model_path), "model_version.json")
            metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

            if metadata.get("model_type") == "XGBClassifier":
                self.classifier = xgb.XGBClassifier()
                self.classifier.load_model(model_path)
                self.model = None
                self.model_kind = "classifier"
            else:
                self.model = xgb.Booster()
                self.model.load_model(model_path)
                self.classifier = None
                self.model_kind = "ranker"
            
            # Assuming we save some metadata along with the model
            meta_path = model_path.replace('.json', '_meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    self.feature_names = meta.get('feature_names', [])
                    self.version = meta.get('version', metadata.get('version', 'unknown'))
            else:
                self.feature_names = (
                    getattr(self.classifier, "feature_names_in_", None)
                    or getattr(self.model, "feature_names", None)
                    or metadata.get("features", [])
                )
                self.version = metadata.get("version", "1.0.0")
                
            logger.info(f"Loaded XGBRanker model v{self.version} from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading XGBoost model: {e}")
            return False
            
    def predict(self, features: pd.DataFrame) -> Tuple[float, float]:
        """
        Predict rank score for candidate features.
        Returns:
            Tuple[float, float]: (rank_score_0_to_100, confidence_0_to_1)
        """
        if not self.is_loaded():
            raise ValueError("Model is not loaded. Call load() first.")
            
        try:
            if self.classifier is not None:
                raw_scores = self.classifier.predict_proba(features)[:, 1]
                score_100 = float(raw_scores[0]) * 100
                confidence = abs(float(raw_scores[0]) - 0.5) * 2
                return round(score_100, 2), round(confidence, 4)

            dmatrix = xgb.DMatrix(features)
            raw_scores = self.model.predict(dmatrix)
            
            # Convert raw ranking score to 0-100 range (assuming sigmoidal or min-max normalization)
            # This is a placeholder logic for demonstration
            raw_score = float(raw_scores[0]) if len(raw_scores) > 0 else 0.0
            
            # Simulated normalization to 0-100
            score_100 = min(max(raw_score * 20 + 50, 0), 100) 
            
            # Simulated confidence based on score distance from decision boundary
            confidence = 0.85 # Placeholder
            
            return round(score_100, 2), confidence
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.0, 0.0
            
    def get_feature_importances(self) -> dict:
        """Get feature importances from the loaded model."""
        if not self.is_loaded():
            return {}
            
        try:
            importance = self.model.get_score(importance_type='weight')
            return importance
        except Exception as e:
            logger.error(f"Error getting feature importances: {e}")
            return {}
            
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded."""
        return self.model is not None or self.classifier is not None

# Singleton instance
xgb_model = XGBRankerModel()
