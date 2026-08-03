import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.metrics import ndcg_score, roc_auc_score
from datetime import datetime

def compute_ndcg_at_k(y_true, y_score, k=10):
    if len(y_true) < 2: return 1.0
    return ndcg_score(np.asarray([y_true]), np.asarray([y_score]), k=k)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "training_features.csv")
    
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Domain will act as the query group
    domains = df['domain'].unique()
    group_map = {d: i for i, d in enumerate(domains)}
    df['group'] = df['domain'].map(group_map)
    
    # Sort by group to satisfy XGBRanker requirement
    df = df.sort_values(by='group').reset_index(drop=True)
    
    features = [c for c in df.columns if c not in ['domain', 'group', 'is_shortlisted']]
    X = df[features]
    y = df['is_shortlisted']
    groups = df.groupby('group').size().values
    
    print(f"Dataset shape: {X.shape}")
    print(f"Features: {features}")
    
    # Group K-Fold Cross Validation
    gkf = GroupKFold(n_splits=min(5, len(domains)))
    
    # Initialize XGBRanker
    model = xgb.XGBRanker(
        objective='rank:ndcg',
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    
    print("Training XGBRanker model...")
    # For a real pipeline, GridSearchCV would be here. For speed, we just train once.
    model.fit(X, y, group=groups)
    
    # Evaluation on training data for sanity check
    preds = model.predict(X)
    
    # Evaluate per group
    ndcg_list = []
    auc_list = []
    start_idx = 0
    for g_size in groups:
        end_idx = start_idx + g_size
        y_g = y.iloc[start_idx:end_idx].values
        p_g = preds[start_idx:end_idx]
        if len(np.unique(y_g)) > 1:
            ndcg_list.append(compute_ndcg_at_k(y_g, p_g, k=10))
            auc_list.append(roc_auc_score(y_g, p_g))
        start_idx = end_idx
        
    print("\n--- Training Report ---")
    print(f"Mean NDCG@10: {np.mean(ndcg_list):.4f}")
    print(f"Mean AUC: {np.mean(auc_list):.4f}")
    
    # Save Model
    out_dir = os.path.join(os.path.dirname(base_dir), "backend", "models", "trained")
    os.makedirs(out_dir, exist_ok=True)
    
    model_path = os.path.join(out_dir, "xgb_ranker.json")
    model.save_model(model_path)
    
    # Save Metadata
    metadata = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "model_type": "XGBRanker",
        "features": features,
        "metrics": {
            "train_ndcg_10": float(np.mean(ndcg_list)),
            "train_auc": float(np.mean(auc_list))
        }
    }
    
    with open(os.path.join(out_dir, "model_version.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
