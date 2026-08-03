import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import ndcg_score, roc_auc_score, average_precision_score

def compute_metrics(y_true, y_score, k=10):
    if len(np.unique(y_true)) < 2:
        return None
        
    ndcg_5 = ndcg_score(np.asarray([y_true]), np.asarray([y_score]), k=5)
    ndcg_10 = ndcg_score(np.asarray([y_true]), np.asarray([y_score]), k=10)
    
    # Precision@5
    sorted_indices = np.argsort(y_score)[::-1]
    top_5 = y_true[sorted_indices][:5]
    prec_5 = np.sum(top_5) / 5.0
    
    ap = average_precision_score(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)
    
    return {
        "ndcg@5": ndcg_5,
        "ndcg@10": ndcg_10,
        "precision@5": prec_5,
        "map": ap,
        "auc": auc
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(os.path.dirname(base_dir), "backend", "models", "trained", "xgb_ranker.json")
    data_path = os.path.join(base_dir, "training_features.csv")
    
    if not os.path.exists(model_path):
        print("Model not found. Run train_xgboost.py first.")
        return
        
    model = xgb.XGBRanker()
    model.load_model(model_path)
    
    df = pd.read_csv(data_path)
    features = [c for c in df.columns if c not in ['domain', 'group', 'is_shortlisted']]
    
    df['group'] = df['domain'].astype('category').cat.codes
    df = df.sort_values(by='group').reset_index(drop=True)
    
    X = df[features]
    y = df['is_shortlisted']
    groups = df.groupby('group').size().values
    
    preds = model.predict(X)
    
    print("\n--- Detailed Evaluation Report ---")
    all_metrics = []
    
    start_idx = 0
    for i, g_size in enumerate(groups):
        end_idx = start_idx + g_size
        y_g = y.iloc[start_idx:end_idx].values
        p_g = preds[start_idx:end_idx]
        
        m = compute_metrics(y_g, p_g)
        if m:
            all_metrics.append(m)
            
        start_idx = end_idx
        
    avg_metrics = {k: np.mean([m[k] for m in all_metrics]) for k in all_metrics[0].keys()}
    for k, v in avg_metrics.items():
        print(f"{k.upper()}: {v:.4f}")
        
    print("\n--- SHAP Feature Importance Summary ---")
    importances = model.feature_importances_
    feat_imp = pd.DataFrame({"Feature": features, "Importance": importances})
    feat_imp = feat_imp.sort_values(by="Importance", ascending=False)
    for idx, row in feat_imp.iterrows():
        print(f"{row['Feature']:<25}: {row['Importance']:.4f}")

if __name__ == "__main__":
    main()
