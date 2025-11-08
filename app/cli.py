"""Command line interface for the job search and resume tailoring app."""
from __future__ import annotations

import argparse
import pathlib
from typing import Iterable

from .job_finder import JobFinder, format_job, load_default_jobs
from .resume_modifier import load_resume, save_resume, tailor_resume


def _parse_keywords(raw_keywords: str | None) -> list[str]:
    if not raw_keywords:
        return []
    return [kw.strip() for kw in raw_keywords.split(",") if kw.strip()]


def command_search(args: argparse.Namespace) -> None:
    finder = load_default_jobs() if args.data is None else JobFinder(pathlib.Path(args.data))
    keywords = _parse_keywords(args.keywords)
    matches = finder.search(keywords, args.location)
    if not matches:
        print("No jobs found for the provided criteria.")
        return
    for job in matches:
        print(format_job(job))
        print("-" * 60)


def command_tailor(args: argparse.Namespace) -> None:
    finder = load_default_jobs() if args.data is None else JobFinder(pathlib.Path(args.data))
    job = finder.get_job(args.job_id)

    resume_path = pathlib.Path(args.resume)
    resume_text = load_resume(resume_path)
    tailored = tailor_resume(resume_text, job)

    output_path = pathlib.Path(args.output) if args.output else resume_path.with_name(resume_path.stem + f"_{job.id}.txt")
    save_resume(tailored, output_path)
    print(f"Tailored resume saved to {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find jobs and tailor your resume for applications.")
    parser.add_argument("--data", help="Optional path to a JSON file containing job postings.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search for job postings.")
    search_parser.add_argument("--keywords", help="Comma-separated list of keywords to match.")
    search_parser.add_argument("--location", help="Regex to filter by location", default=None)
    search_parser.set_defaults(func=command_search)

    tailor_parser = subparsers.add_parser("tailor", help="Tailor a resume for a specific job.")
    tailor_parser.add_argument("job_id", help="The job id to tailor the resume for.")
    tailor_parser.add_argument("resume", help="Path to the resume text file.")
    tailor_parser.add_argument("--output", help="Optional output path for the tailored resume.")
    tailor_parser.set_defaults(func=command_tailor)

    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
