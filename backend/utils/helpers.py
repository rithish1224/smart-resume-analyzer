import uuid
from datetime import date
from dateutil import parser
import re

def generate_uuid() -> str:
    return str(uuid.uuid4())

def normalize_skill(skill: str) -> str:
    if not skill:
        return ""
    # Lowercase and strip whitespace
    return " ".join(skill.lower().strip().split())

def calculate_years_experience(dates: list) -> float:
    # Mock implementation of years experience calculation
    if not dates or len(dates) < 2:
        return 0.0
    
    try:
        start_date = parse_date_string(dates[0])
        end_date = parse_date_string(dates[1])
        if start_date and end_date:
            days = (end_date - start_date).days
            return round(max(0, days / 365.25), 1)
    except Exception:
        pass
    return 0.0

def parse_date_string(date_str: str) -> date | None:
    if not date_str:
        return None
    try:
        parsed_datetime = parser.parse(date_str, default=date.today())
        return parsed_datetime.date()
    except Exception:
        return None
