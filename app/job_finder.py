"""Utilities to load and search job postings."""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence


@dataclass
class JobPosting:
    """Simple representation of a job posting."""

    id: str
    title: str
    company: str
    location: str
    type: str
    summary: str
    skills: Sequence[str]
    tools: Sequence[str]
    experience_level: str
    description: str
    responsibilities: Sequence[str]
    score: float = field(default=0.0)

    def to_display_dict(self) -> dict:
        """Return the posting as a dictionary suitable for printing."""
        payload = self.__dict__.copy()
        payload["skills"] = list(self.skills)
        payload["tools"] = list(self.tools)
        payload["responsibilities"] = list(self.responsibilities)
        return payload


class JobFinder:
    """Load and search job postings from a JSON file."""

    def __init__(self, jobs_path: pathlib.Path) -> None:
        self.jobs_path = jobs_path
        self._jobs = self._load_jobs()

    def _load_jobs(self) -> List[JobPosting]:
        if not self.jobs_path.exists():
            raise FileNotFoundError(f"Job file not found: {self.jobs_path}")
        with self.jobs_path.open("r", encoding="utf-8") as f:
            raw_jobs = json.load(f)
        jobs = []
        for entry in raw_jobs:
            jobs.append(JobPosting(**entry))
        return jobs

    @property
    def jobs(self) -> Sequence[JobPosting]:
        return tuple(self._jobs)

    def search(self, keywords: Iterable[str], location: str | None = None) -> List[JobPosting]:
        """Return job postings that match the provided keywords and optional location.

        Jobs are ranked by the number of keyword matches found in the title,
        summary, description, or skills list.
        """

        keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        if not keywords and not location:
            return list(self.jobs)

        matched: List[JobPosting] = []
        location_regex = re.compile(location, re.IGNORECASE) if location else None
        for job in self.jobs:
            if location_regex and not location_regex.search(job.location):
                continue

            score = 0
            haystacks = [job.title, job.summary, job.description, " ".join(job.skills)]
            text = " ".join(haystacks).lower()
            for kw in keywords:
                if kw in text:
                    score += 1
            if score or (not keywords and location_regex):
                job_copy = JobPosting(**job.to_display_dict())
                job_copy.score = float(score)
                matched.append(job_copy)

        matched.sort(key=lambda j: j.score, reverse=True)
        return matched

    def get_job(self, job_id: str) -> JobPosting:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise ValueError(f"Job with id '{job_id}' not found")


def format_job(job: JobPosting) -> str:
    """Pretty print a job posting for CLI output."""

    lines = [
        f"[{job.id}] {job.title} - {job.company}",
        f"Location: {job.location} | Type: {job.type} | Experience: {job.experience_level}",
        f"Summary: {job.summary}",
        "Skills: " + ", ".join(job.skills),
        "Tools: " + ", ".join(job.tools),
        "Responsibilities:",
    ]
    lines.extend(f"  - {resp}" for resp in job.responsibilities)
    if job.score:
        lines.append(f"Match score: {job.score:.0f}")
    return "\n".join(lines)


def load_default_jobs() -> JobFinder:
    """Helper to load jobs from the default data file."""

    data_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "jobs.json"
    return JobFinder(data_path)
