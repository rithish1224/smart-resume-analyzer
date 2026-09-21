import io
import re
import fitz
import docx
import spacy
from typing import Optional, List, Dict, Any
from backend.services.ocr_service import OCRService
from backend.models.schemas import CandidateProfileSchema

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not downloaded
            import spacy.cli as spacy_cli
            spacy_cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.ocr_service = OCRService()
        
        # Simple taxonomy fallback if taxonomy not provided
        self.skill_taxonomy = ["python", "java", "c++", "machine learning", "fastapi", "aws", "docker", "kubernetes", "sql", "nosql"]

    async def parse(self, file_bytes: bytes, filename: str) -> CandidateProfileSchema:
        """Parse a resume file (PDF, DOCX, TXT, Image) into a structured schema."""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        text = ""

        if ext == "pdf":
            text = self._parse_pdf(file_bytes)
        elif ext in ["docx", "doc"]:
            text = self._parse_docx(file_bytes)
        elif ext in ["txt"]:
            text = file_bytes.decode("utf-8", errors="ignore")
        elif ext in ["jpg", "jpeg", "png"]:
            text, _ = self.ocr_service.extract_text(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        return self._extract_information(text)

    def _parse_pdf(self, file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_blocks = []
        for page in doc:
            blocks = page.get_text("blocks")
            # Sort by vertical (y0) then horizontal (x0) to handle multi-column
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b in blocks:
                text_blocks.append(b[4])
        return "\n".join(text_blocks)

    def _parse_docx(self, file_bytes: bytes) -> str:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])

    def _segment_sections(self, text: str) -> Dict[str, str]:
        sections = {
            "EXPERIENCE": "",
            "EDUCATION": "",
            "SKILLS": "",
            "PROJECTS": "",
            "CERTIFICATIONS": "",
            "SUMMARY": ""
        }
        
        # Basic section header matching
        lines = text.split("\n")
        current_section = "SUMMARY"
        
        header_patterns = {
            "EXPERIENCE": re.compile(r"^(work\s+)?experience|employment|history$", re.I),
            "EDUCATION": re.compile(r"^education|academic|background$", re.I),
            "SKILLS": re.compile(r"^skills|technologies|core\s+competencies$", re.I),
            "PROJECTS": re.compile(r"^projects$", re.I),
            "CERTIFICATIONS": re.compile(r"^certifications|certificates$", re.I),
        }

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            
            matched = False
            for sec, pattern in header_patterns.items():
                if len(line_clean) < 30 and pattern.search(line_clean):
                    current_section = sec
                    matched = True
                    break
            
            if not matched:
                sections[current_section] += line_clean + "\n"
                
        return sections

    def _extract_information(self, text: str) -> CandidateProfileSchema:
        doc = self.nlp(text)
        
        # Email & Phone regex
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        email = emails[0] if emails else ""
        phone = phones[0] if phones else ""
        
        # First line heuristic for name
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        name = lines[0] if lines else ""
        if len(name) > 50 or re.search(r"\d", name):
            # Fallback to spacy PERSON entities
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if persons:
                name = persons[0]

        sections = self._segment_sections(text)
        
        # Extract skills (simple taxonomy matching)
        skills_found = []
        text_lower = text.lower()
        for skill in self.skill_taxonomy:
            if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
                skills_found.append(skill)
                
        # Simple extraction for other fields
        return CandidateProfileSchema(
            name=name,
            email=email,
            phone=phone,
            skills=list(set(skills_found)),
            experience_raw=sections.get("EXPERIENCE", ""),
            education_raw=sections.get("EDUCATION", ""),
            projects_raw=sections.get("PROJECTS", ""),
            certifications_raw=sections.get("CERTIFICATIONS", ""),
            raw_text=text
        )
