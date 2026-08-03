import json
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
