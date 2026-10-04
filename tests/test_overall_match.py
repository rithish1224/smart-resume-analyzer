from types import SimpleNamespace

from backend.routers.analyze import compute_overall_match, _overall_level
from backend.routers.reports import _serialize


def coverage(**updates):
    value = {
        "skill_coverage": 100,
        "years_candidate": 4,
        "years_required": 3,
        "years_met": True,
        "degree_found": 2,
        "degree_required": 2,
        "degree_met": True,
    }
    value.update(updates)
    return value


def test_full_experience_score():
    assert compute_overall_match(coverage()) == 100


def test_one_year_of_five_lowers_match_level():
    value = compute_overall_match(coverage(
        skill_coverage=67, years_candidate=1, years_required=5,
        years_met=False, degree_found=None, degree_met=None,
    ))
    assert value == 57
    assert _overall_level(value) == "Partial match"


def test_missing_experience_rescales_weights():
    value = compute_overall_match(coverage(years_candidate=None, years_met=None))
    assert value == 100


def test_preferred_experience_is_excluded():
    value = compute_overall_match(
        coverage(years_candidate=1, years_required=5, years_met=False),
        "Python required. Five years of experience preferred.",
    )
    assert value == 100


def test_old_report_without_overall_match_still_loads():
    report = SimpleNamespace(
        id="report", created_at=None, resume_filename="resume.pdf",
        target_role=None, job_description="jd", match_level="Partial match",
        skill_coverage=62, overall_match_percent=None,
        matched_skills="[]", missing_skills="[]", summary="summary",
        requirement_coverage=None,
    )
    assert _serialize(report)["overall_match_percent"] == 62
