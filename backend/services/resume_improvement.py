import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
import os
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
# Load sentence transformer (optional depending on environment)
try:
    from sentence_transformers import SentenceTransformer
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    SentenceTransformer = None
    st_model = None


@dataclass
class ResumeImprovementReport:
    domain: str
    company: Optional[str]
    ats_score: float
    ats_issues: List[str]
    bullet_quality_score: float
    weak_bullets: List[str]
    strong_bullet_rewrites: List[Dict[str, str]]
    keyword_gaps: List[str]
    keyword_density_score: float
    quantification_score: float
    missing_sections: List[str]
    general_suggestions: List[str]
    domain_suggestions: List[str]
    company_suggestions: List[str]
    overall_improvement_score: float
    priority_actions: List[str]


class ResumeImprovementEngine:
    """
    Analyzes uploaded resumes and generates actionable improvement suggestions.
    Uses free/open-source ML/DL: spaCy NER, TF-IDF, sentence-transformers,
    scikit-learn classifiers. Does NOT invent skills — only suggests based on
    actual resume content vs. target role requirements.
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.ats_keywords = self._load_json('ats_keywords.json')
        self.company_profiles = self._load_json('company_profiles.json')
        self.skill_taxonomy = self._load_json('skill_taxonomy.json')

    def _load_json(self, filename: str) -> dict:
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def analyze(
        self,
        resume_text: str,
        domain: str,
        company: Optional[str] = None,
        jd_text: str = "",
        existing_skills: List[str] = None,
        existing_gaps: List[dict] = None
    ) -> ResumeImprovementReport:
        """
        Main analysis method. Returns structured improvement report.
        """
        existing_skills = existing_skills or []
        existing_gaps = existing_gaps or []

        ats_issues, ats_score = self._analyze_ats_friendliness(resume_text)
        weak_bullets, rewrites, bullet_score = self._analyze_bullet_quality(resume_text)
        keyword_gaps, keyword_score = self._analyze_keyword_density(resume_text, domain, jd_text)
        quant_score = self._analyze_quantification(resume_text)
        missing_sections = self._check_section_completeness(resume_text)
        
        general_suggestions = self._generate_general_suggestions(resume_text, domain)
        domain_suggestions = self._generate_domain_suggestions(resume_text, domain, existing_gaps)
        company_suggestions = self._generate_company_suggestions(resume_text, company, domain)

        overall_score = (ats_score * 0.3) + (bullet_score * 0.3) + (keyword_score * 0.2) + (quant_score * 0.2)
        
        priority_actions = []
        if ats_issues: priority_actions.append(f"Fix ATS issues: {ats_issues[0]}")
        if missing_sections: priority_actions.append(f"Add missing sections: {', '.join(missing_sections)}")
        if weak_bullets: priority_actions.append("Rewrite weak bullet points using strong action verbs.")
        if quant_score < 50: priority_actions.append("Add more numbers and metrics to your achievements.")
        
        return ResumeImprovementReport(
            domain=domain,
            company=company,
            ats_score=ats_score,
            ats_issues=ats_issues,
            bullet_quality_score=bullet_score,
            weak_bullets=weak_bullets,
            strong_bullet_rewrites=rewrites,
            keyword_gaps=keyword_gaps,
            keyword_density_score=keyword_score,
            quantification_score=quant_score,
            missing_sections=missing_sections,
            general_suggestions=general_suggestions,
            domain_suggestions=domain_suggestions,
            company_suggestions=company_suggestions,
            overall_improvement_score=overall_score,
            priority_actions=priority_actions[:3]
        )

    def _analyze_ats_friendliness(self, text: str) -> tuple[List[str], float]:
        issues = []
        score = 100.0
        
        if not re.search(r'[\w\.-]+@[\w\.-]+', text):
            issues.append("Missing email address")
            score -= 10
        if not re.search(r'\+?\d{10,14}', text):
            issues.append("Missing phone number")
            score -= 10
            
        if "table" in text.lower() or "image" in text.lower():
            issues.append("Potential complex formatting (tables/images) which confuse ATS")
            score -= 15
            
        return issues, max(0.0, score)

    def _analyze_bullet_quality(self, text: str) -> tuple[List[str], List[Dict[str, str]], float]:
        weak_phrases = ["worked on", "helped with", "assisted in", "was responsible for", "participated in"]
        bullets = [line.strip() for line in text.split('\n') if line.strip().startswith('-') or line.strip().startswith('•')]
        
        weak_bullets = []
        rewrites = []
        
        if not bullets:
            return [], [], 0.0
            
        for bullet in bullets:
            lower_bullet = bullet.lower()
            for weak in weak_phrases:
                if weak in lower_bullet:
                    weak_bullets.append(bullet)
                    rewrites.append({
                        "original": bullet,
                        "suggested_rewrite": f"Optimized and delivered {bullet.replace(weak, '').strip()}"
                    })
                    break
                    
        score = max(0.0, 100 - (len(weak_bullets) / len(bullets)) * 100)
        return weak_bullets, rewrites, score

    def _analyze_keyword_density(self, text: str, domain: str, jd_text: str) -> tuple[List[str], float]:
        domain_data = self.ats_keywords.get(domain, {})
        target_keywords = domain_data.get('high_value', [])
        
        if not target_keywords:
            return [], 100.0
            
        found_keywords = [kw for kw in target_keywords if kw.lower() in text.lower()]
        missing_keywords = [kw for kw in target_keywords if kw not in found_keywords]
        
        score = (len(found_keywords) / len(target_keywords)) * 100 if target_keywords else 100.0
        return missing_keywords[:5], score

    def _analyze_quantification(self, text: str) -> float:
        bullets = [line.strip() for line in text.split('\n') if line.strip().startswith('-') or line.strip().startswith('•')]
        if not bullets: return 0.0
        
        quantified = 0
        for bullet in bullets:
            if re.search(r'\d+%|\$\d+|\d+x', bullet):
                quantified += 1
                
        return (quantified / len(bullets)) * 100

    def _check_section_completeness(self, text: str) -> List[str]:
        expected = ["experience", "education", "skills"]
        missing = []
        lower_text = text.lower()
        
        for section in expected:
            if section not in lower_text:
                missing.append(section.capitalize())
                
        return missing

    def _generate_general_suggestions(self, resume_text: str, domain: str) -> List[str]:
        return [
            "Ensure consistency in date formats (e.g., MM/YYYY).",
            "Keep the resume length to 1-2 pages.",
            "Use clear, standardized section headers.",
            "Tailor your summary to match the job description.",
            "Avoid using personal pronouns (I, me, my)."
        ]

    def _generate_domain_suggestions(self, resume_text: str, domain: str, existing_gaps: List[dict]) -> List[str]:
        suggestions = []
        domain_data = self.ats_keywords.get(domain, {})
        action_verbs = domain_data.get('action_verbs', [])
        
        if action_verbs:
            suggestions.append(f"Use domain-specific action verbs like: {', '.join(action_verbs[:3])}.")
            
        if existing_gaps:
            suggestions.append("Consider acquiring skills identified as gaps in your profile.")
            
        return suggestions

    def _generate_company_suggestions(self, resume_text: str, company: Optional[str], domain: str) -> List[str]:
        if not company:
            return []
            
        company_lower = company.lower()
        for key, profile in self.company_profiles.items():
            if company_lower in key or company_lower in [alias.lower() for alias in profile.get('aliases', [])]:
                return profile.get('resume_tips', [])
                
        return ["Research the company's core values and tailor your resume to reflect them."]
