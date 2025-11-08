import pathlib

import pytest

from app.job_finder import JobFinder, format_job
from app.resume_modifier import match_skills, tailor_resume, tailor_summary


@pytest.fixture(scope="module")
def sample_jobs_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent / "data" / "jobs.json"


@pytest.fixture(scope="module")
def job_finder(sample_jobs_path: pathlib.Path) -> JobFinder:
    return JobFinder(sample_jobs_path)


def test_search_matches_keyword(job_finder: JobFinder):
    results = job_finder.search(["machine", "learning"], None)
    assert results, "Expected to find at least one machine learning job"
    assert results[0].id == "DS-101"


def test_search_filters_location(job_finder: JobFinder):
    results = job_finder.search([], "New York")
    assert len(results) == 1
    assert results[0].id == "PM-301"


def test_format_job_contains_score(job_finder: JobFinder):
    job = job_finder.search(["python"], None)[0]
    formatted = format_job(job)
    assert "Match score" in formatted


def test_match_skills_detects_overlap(job_finder: JobFinder):
    job = job_finder.get_job("DS-101")
    resume_skills = ["Python", "Machine Learning", "Public Speaking"]
    overlap = match_skills(resume_skills, job.skills)
    assert overlap == ["Python", "Machine Learning"]


def test_tailor_resume_injects_sections(job_finder: JobFinder):
    job = job_finder.get_job("DS-101")
    resume = """NAME\nAda Lovelace\n\nSUMMARY\nExperienced data professional.\n\nSKILLS\n- Python\n- SQL\n- Public Speaking\n"""
    tailored = tailor_resume(resume, job)
    assert "TAILORED SUMMARY" in tailored
    assert "ROLE HIGHLIGHTS" in tailored


def test_tailor_summary_handles_no_skills(job_finder: JobFinder):
    job = job_finder.get_job("PM-301")
    summary = tailor_summary("Seasoned PM", job, [])
    assert "Eager to ramp up" in summary
