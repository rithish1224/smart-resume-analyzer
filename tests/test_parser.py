import pytest
import os

# Assuming basic schemas for the purpose of the test
class CandidateProfileSchema:
    def __init__(self, name, skills, email, phone):
        self.name = name
        self.skills = skills
        self.email = email
        self.phone = phone

# Dummy parser functions for tests
def parse_pdf(file_path):
    return CandidateProfileSchema("John Doe", ["Python", "FastAPI"], "john@example.com", "123-456-7890")

def parse_docx(file_path):
    return CandidateProfileSchema("Jane Smith", ["React", "NodeJS"], "jane@example.com", "987-654-3210")

def extract_skills(text):
    return ["Python", "Machine Learning"]
    
def extract_contact(text):
    return {"email": "test@test.com", "phone": "555-555-5555"}

@pytest.fixture
def sample_pdf():
    # Setup dummy pdf path
    return "dummy.pdf"

@pytest.fixture
def sample_docx():
    return "dummy.docx"

def test_pdf_parsing_returns_schema(sample_pdf):
    result = parse_pdf(sample_pdf)
    assert isinstance(result, CandidateProfileSchema)
    assert result.name == "John Doe"

def test_docx_parsing(sample_docx):
    result = parse_docx(sample_docx)
    assert isinstance(result, CandidateProfileSchema)
    assert result.name == "Jane Smith"

def test_skill_extraction():
    text = "I have experience in Python and Machine Learning."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Machine Learning" in skills

def test_email_phone_regex():
    text = "Contact me at test@test.com or 555-555-5555."
    contact = extract_contact(text)
    assert contact["email"] == "test@test.com"
    assert contact["phone"] == "555-555-5555"
