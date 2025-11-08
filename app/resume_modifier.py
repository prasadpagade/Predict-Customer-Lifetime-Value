"""Utilities to tailor a resume for a specific job posting."""
from __future__ import annotations

import pathlib
from typing import Iterable, Sequence

from .job_finder import JobPosting


def normalize_token(token: str) -> str:
    return token.strip().lower()


def _tokenize(items: Iterable[str]) -> set[str]:
    tokens: set[str] = set()
    for item in items:
        tokens.update(normalize_token(part) for part in item.split(","))
    return {token for token in tokens if token}


def match_skills(resume_skills: Sequence[str], job_skills: Sequence[str]) -> list[str]:
    """Return overlapping skills between a resume and a job posting."""

    resume_tokens = _tokenize(resume_skills)
    intersection = [skill for skill in job_skills if normalize_token(skill) in resume_tokens]
    return intersection


def tailor_summary(base_summary: str, job: JobPosting, matched_skills: Sequence[str]) -> str:
    """Return a tailored summary highlighting the job title and matched skills."""

    if matched_skills:
        skills_phrase = ", ".join(matched_skills[:5])
        skills_text = f"Key strengths aligned with this role include {skills_phrase}."
    else:
        skills_text = "Eager to ramp up on the team\'s preferred tools and practices."
    return (
        f"Target Role: {job.title} at {job.company}.\n"
        f"{base_summary.strip()}\n"
        f"Focus for this application: {skills_text}"
    )


def tailor_resume(resume_text: str, job: JobPosting) -> str:
    """Inject a tailored summary and highlighted skills into a resume."""

    sections = _split_sections(resume_text)
    skills_section = sections.get("skills", "")
    resume_skills = [line.strip("- ") for line in skills_section.splitlines() if line.strip()]
    matched_skills = match_skills(resume_skills, job.skills)

    summary_text = sections.get("summary") or sections.get("professional summary") or ""
    tailored_summary = tailor_summary(summary_text or "Experienced professional ready to contribute.", job, matched_skills)

    highlighted_lines = [
        "Highlighted Skills for this role:",
    ]
    if matched_skills:
        highlighted_lines.extend(f"- {skill}" for skill in matched_skills)
    else:
        highlighted_lines.append("- Rapid learner with a track record of mastering new domains")

    sections["tailored summary"] = tailored_summary
    sections["role highlights"] = "\n".join(highlighted_lines)

    ordered_sections = [
        "name",
        "contact",
        "tailored summary",
        "summary",
        "professional summary",
        "experience",
        "projects",
        "education",
        "skills",
        "role highlights",
    ]

    assembled: list[str] = []
    seen = set()
    for key in ordered_sections:
        if key in sections and key not in seen and sections[key].strip():
            assembled.append(_format_section(key, sections[key]))
            seen.add(key)

    # Add any remaining sections that were not in the default order.
    for key, value in sections.items():
        if key not in seen and value.strip():
            assembled.append(_format_section(key, value))
            seen.add(key)

    return "\n\n".join(assembled).strip() + "\n"


def _split_sections(resume_text: str) -> dict[str, str]:
    """Split a resume into sections using headings as delimiters."""

    sections: dict[str, str] = {}
    current_header = ""
    buffer: list[str] = []
    for line in resume_text.splitlines():
        stripped = line.strip()
        if stripped.isupper() and len(stripped.split()) <= 4:
            if current_header:
                sections[current_header] = "\n".join(buffer).strip()
                buffer = []
            current_header = stripped.lower()
        else:
            buffer.append(line)
    if current_header:
        sections[current_header] = "\n".join(buffer).strip()
    elif buffer:
        sections["summary"] = "\n".join(buffer).strip()
    return sections


def _format_section(header: str, body: str) -> str:
    title = header.upper()
    return f"{title}\n{body.strip()}"


def load_resume(path: pathlib.Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def save_resume(text: str, path: pathlib.Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
