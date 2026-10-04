from types import SimpleNamespace

from backend.routers.analyze import requirement_check
from backend.routers.reports import _serialize


def test_requirement_checks_met():
    coverage = {
        "years_candidate": 4, "years_required": 3, "years_met": True,
        "degree_found": 2, "degree_required": 2, "degree_met": True,
    }
    assert requirement_check(coverage) == {"experience": "Met", "education": "Met"}


def test_requirement_checks_below():
    coverage = {
        "years_candidate": 2, "years_required": 3, "years_met": False,
        "degree_found": 1, "degree_required": 2, "degree_met": False,
    }
    assert requirement_check(coverage) == {"experience": "Below", "education": "Below"}


def test_requirement_checks_missing():
    assert requirement_check({
        "years_candidate": None, "years_required": 3,
        "degree_found": None, "degree_required": 2,
    }) == {"experience": "Not enough information", "education": "Not enough information"}


def test_old_report_without_requirement_coverage_loads():
    report = SimpleNamespace(
        id="report", created_at=None, resume_filename="resume.pdf",
        target_role=None, job_description="jd", match_level="Weak match",
        skill_coverage=None, matched_skills="[]", missing_skills="[]",
        summary="summary", requirement_coverage=None,
    )
    assert _serialize(report)["requirement_coverage"] is None
