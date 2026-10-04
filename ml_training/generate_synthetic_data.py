Repo: "Smart Competency Diagnostic" on Windows
(C:\projects\ml project). Python 3.12, FastAPI,
XGBoost XGBRanker in ml_training/.

Goal: freeze the current baseline and measure how
good the model really is. This is an evaluation
task. Do NOT retrain or overwrite
backend/models/trained/xgb_ranker.json or
model_version.json.

Phase 0: Setup
- Create git branch "ml-upgrade".
- Install the spaCy model:
  python -m spacy download en_core_web_sm
  and add it to backend/requirements.txt notes,
  the README, and the Dockerfile.

Phase 1: Freeze baseline
- Copy xgb_ranker.json and model_version.json to
  backend/models/trained/baseline_v1/.
- Create docs/baseline.md with: algorithm and
  hyperparameters (rank:ndcg, 200 trees, depth 5,
  lr 0.05, subsample 0.8, colsample 0.8, seed 42),
  the 5 features (exp_years, skill_match_ratio,
  num_projects, num_certs, gpa), dataset (500
  synthetic profiles, 8 domains), how labels are
  made (75th percentile of a heuristic score:
  30% skill, 30% experience, 25% education,
  15% projects plus noise), and the reported
  metrics: NDCG@5 0.9836, NDCG@10 0.9533,
  P@5 0.9750, MAP 0.8903, ROC-AUC 0.9485.
  Label them clearly "in-sample, synthetic labels,
  no holdout".
- Fix README overclaims: it says "over 20
  features" but training uses 5. List the real
  features, and mark the data as synthetic.

Phase 2: Honest evaluation
Create ml_training/honest_eval.py (new file):
a) Synthetic holdout: split training_features.csv
   80/20 within each domain, train a fresh model in
   memory with the same hyperparameters on the 80%,
   and report NDCG@5/10, P@5, ROC-AUC on the 20%.
b) Real-data test: load the Hugging Face dataset
   "cnamuangtoun/resume-job-description-fit"
   using the datasets library. Check its columns
   and license first, and print them. Map labels
   No Fit=0, Potential Fit=1, Good Fit=2.
   Reuse the existing parsing/feature code
   (feature_engineering.py and backend/services)
   to compute the same 5 features from the real
   resume and JD text. Features that cannot be
   extracted (for example gpa) stay NaN. Report the
   extraction coverage per feature.
   Score the real pairs with the saved baseline
   model and report ROC-AUC (Good vs. rest) and
   Spearman correlation with labels. Report
   NDCG@k only for JDs that have 2 or more resumes
   with differing labels, and print how many
   qualify.
c) Baselines on the same real test pairs:
   random scores, and TF-IDF cosine similarity
   between resume and JD. Same metrics.
d) Write docs/honest_eval.md with one comparison
   table: synthetic in-sample vs. synthetic holdout
   vs. real data vs. TF-IDF vs. random, plus
   notes on limitations.

Rules:
- Report numbers exactly as measured. Do not tune
  anything to make results look better.
- If the dataset cannot be downloaded, print
  manual instructions and skip only that part.
- New files only, except the README fix. Write down
  every assumption. Small commits per phase.

When done, print the comparison table and STOP.
Do not start any upgrade work.import json
import random
import csv
import math
import os
import numpy as np

DOMAINS_DISTR = {
    "software_engineer": 80,
    "data_analyst": 65,
    "ml_engineer": 70,
    "web_developer": 65,
    "cybersecurity": 55,
    "cloud_engineer": 55,
    "ui_ux": 55,
    "devops": 55
}

NAMES = ["Aarav Patel", "Vihaan Sharma", "Vivaan Kumar", "Aditya Singh", "Reyansh Gupta", 
         "Ayaan Desai", "Rudra Reddy", "Arjun Rao", "Siddharth Joshi", "Kian Mehta",
         "Diya Patel", "Isha Sharma", "Ananya Kumar", "Aadhya Singh", "Pari Gupta",
         "Navya Desai", "Myra Reddy", "Sara Rao", "Kyra Joshi", "Meera Mehta",
         "Rahul Verma", "Sneha Kapoor", "Amit Malhotra", "Pooja Singh", "Rajesh Yaday"]
DEGREES = ["BTech", "MTech", "PhD", "Diploma", "BSc", "BDes"]
UNIVERSITIES = ["IIT Bombay", "IIT Delhi", "BITS Pilani", "NIT Trichy", "Anna University", "VIT Vellore", "Manipal University", "Delhi University"]

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_candidates():
    # Load requirements
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    taxonomy = load_json(os.path.join(base_dir, "backend", "data", "skill_taxonomy.json"))
    role_templates = load_json(os.path.join(base_dir, "backend", "data", "role_templates.json"))

    candidates = []
    
    for domain, count in DOMAINS_DISTR.items():
        template = role_templates[domain]
        domain_skills = taxonomy[domain]
        all_domain_skills = domain_skills.get("critical", []) + domain_skills.get("important", []) + domain_skills.get("nice_to_have", [])
        
        for _ in range(count):
            name = random.choice(NAMES) + " " + str(random.randint(1,1000))
            email = name.lower().replace(" ", ".") + "@example.com"
            exp_years = random.randint(0, 12)
            
            # Skills
            num_skills = random.randint(5, 15)
            skills = random.sample(all_domain_skills, min(num_skills, len(all_domain_skills)))
            
            # Education
            edu_year = random.randint(2015, 2024)
            degree = random.choice(DEGREES)
            gpa = round(random.uniform(6.0, 9.5), 2)
            
            # Companies
            companies = []
            if exp_years > 0:
                companies.append({
                    "name": "TechCorp India",
                    "role": "Engineer",
                    "duration_months": exp_years * 12,
                    "skills_used": random.sample(skills, min(3, len(skills)))
                })
                
            # Projects
            projects = []
            for i in range(random.randint(0, 3)):
                projects.append({
                    "name": f"Project {i}",
                    "tech_stack": random.sample(skills, min(2, len(skills))),
                    "description": "Implemented core features."
                })
            
            # Calculate Proxy Score
            # Skill match
            crit_skills = set(template["critical_skills"])
            has_crit = set(skills).intersection(crit_skills)
            skill_score = len(has_crit) / len(crit_skills) if crit_skills else 0
            
            # Exp ratio
            exp_score = min(exp_years / template["required_years"], 1.5) if template["required_years"] > 0 else 1.0
            
            # Edu
            edu_score = 1.0 if gpa > 7.5 else 0.5
            
            # Projects
            proj_score = min(len(projects) / 3, 1.0)
            
            noise = np.random.normal(0, 0.1)
            raw_score = (skill_score * 0.3) + (exp_score * 0.3) + (edu_score * 0.25) + (proj_score * 0.15) + noise
            
            candidate = {
                "name": name,
                "email": email,
                "phone": "+91" + str(random.randint(1000000000, 9999999999)),
                "domain": domain,
                "education": {
                    "degree": degree,
                    "institution": random.choice(UNIVERSITIES),
                    "gpa": gpa,
                    "year": edu_year,
                    "is_stem": True if degree in ["BTech", "MTech"] else False
                },
                "experience_years": exp_years,
                "companies": companies,
                "skills": skills,
                "certifications": random.sample(template.get("preferred_certs", []), random.randint(0, min(2, len(template.get("preferred_certs", []))))),
                "projects": projects,
                "raw_score": raw_score
            }
            candidates.append(candidate)
            
    # Compute threshold per domain for top 25% (score > 75th percentile)
    domain_scores = {}
    for c in candidates:
        domain_scores.setdefault(c["domain"], []).append(c["raw_score"])
        
    thresholds = {d: np.percentile(scores, 75) for d, scores in domain_scores.items()}
    
    for c in candidates:
        c["is_shortlisted"] = 1 if c["raw_score"] > thresholds[c["domain"]] else 0
        del c["raw_score"]
        
    return candidates

def extract_features_dummy(c, t):
    crit_skills = set(t.get("critical_skills", []))
    c_skills = set(c["skills"])
    return {
        "exp_years": c["experience_years"],
        "skill_match_ratio": len(c_skills.intersection(crit_skills)) / len(crit_skills) if crit_skills else 0,
        "num_projects": len(c["projects"]),
        "num_certs": len(c["certifications"]),
        "gpa": c["education"]["gpa"],
        "is_shortlisted": c["is_shortlisted"],
        "domain": c["domain"]
    }

if __name__ == "__main__":
    candidates = generate_candidates()
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    
    # Save JSON
    with open(os.path.join(out_dir, "synthetic_candidates.json"), "w") as f:
        json.dump(candidates, f, indent=2)
        
    # Generate CSV Features
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    role_templates = load_json(os.path.join(base_dir, "backend", "data", "role_templates.json"))
    
    csv_rows = []
    for c in candidates:
        row = extract_features_dummy(c, role_templates[c["domain"]])
        csv_rows.append(row)
        
    keys = csv_rows[0].keys()
    with open(os.path.join(out_dir, "training_features.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"Generated {len(candidates)} candidates.")
