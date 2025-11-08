# Job Search and Resume Tailoring App

This repository now includes a lightweight command-line tool that helps you:

1. Search curated job postings using keywords and location filters.
2. Tailor your resume text to align with a specific job before applying.

The application ships with a small sample dataset (`data/jobs.json`) but you can
point it to your own JSON file containing job postings with the same schema.

## Getting started

The project uses the Python standard library only. To run the app, ensure you
have Python 3.11+ installed.

Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

## Usage

Run the command-line interface via the `python -m` entry point:

```bash
python -m app.cli <command> [options]
```

### Search for jobs

Search by keywords and/or location. Keywords are matched against job titles,
summaries, descriptions, and listed skills. Location is treated as a regular
expression so you can match multiple cities or remote roles.

```bash
python -m app.cli search --keywords "data,python" --location "Remote"
```

### Tailor a resume

Provide the target job id and a path to a plain-text resume. The command will
inject a tailored summary and a highlighted skills section. The output is saved
next to the original resume unless you specify a custom path.

```bash
python -m app.cli tailor DS-101 resume.txt --output resume_ds101.txt
```

### Using a custom dataset

All commands accept an optional `--data` argument pointing to a JSON file with
job postings. Each posting should contain the following keys:

- `id`
- `title`
- `company`
- `location`
- `type`
- `summary`
- `skills` (list of strings)
- `tools` (list of strings)
- `experience_level`
- `description`
- `responsibilities` (list of strings)

## Running tests

The repository includes unit tests covering the job search and resume tailoring
logic. Execute the test suite with:

```bash
python -m pytest
```

## Sample resume format

The tailoring logic detects sections by uppercase headings. A minimal example:

```
NAME
Ada Lovelace

CONTACT
ada@example.com | linkedin.com/in/ada

SUMMARY
Data scientist with experience delivering predictive analytics products.

SKILLS
- Python
- Machine Learning
- SQL
- Statistics
- Data Visualization
```

Feel free to adjust the headings to match your resume; the tool preserves
existing sections and adds job-specific highlights.
