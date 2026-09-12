# HRIS Import Preview

A small Django application built for Diversio's Engineer I technical exercise. It lets a user upload a client's HRIS CSV export and preview the data — row counts, validation errors, organizational hierarchy, and reporting-cycle detection — before anything is written to the Diversio platform.

## Overview

A client sends an HRIS export listing employees and their reporting relationships. Before that data touches the platform, Client Success needs a fast, reliable way to inspect it: how many rows came in, which rows are invalid and why, who the root employees are (no manager), how many direct reports each manager has, and whether any employees are stuck in a circular reporting relationship.

This app takes a CSV upload from the browser, analyzes it entirely in memory, and displays the results — no database writes.

## How it works

1. The uploaded file is decoded and checked for the six required columns.
2. Every row is parsed, whitespace-trimmed, and emails are lowercased.
3. Duplicate `employee_id` or `email` values are detected across the whole file and those rows are excluded from further analysis.
4. For each remaining employee, their manager is resolved by `manager_id`, `manager_email`, or both (which must agree) — conflicts, missing managers, and self-management are all reported as errors.
5. Reporting cycles are detected by walking each employee's manager chain and identifying repeated nodes.

## Project structure

hris-import-preview/
- manage.py
- README.md
- sample_hris.csv
- hris_preview/  (Django project config: settings.py, urls.py, wsgi.py, asgi.py)
- preview/  (Django app)
  - hris_parser.py — core parsing/validation/hierarchy logic (no Django dependency)
  - views.py — handles upload and renders results
  - tests.py — automated tests for hris_parser.py
  - templates/preview/upload.html

## Setup and run instructions

1. Create and activate a virtual environment (optional but recommended):
python -m venv venv
venv\Scripts\activate
2. Install dependencies:
pip install Django
3. Run the development server:
python manage.py runserver
4. Open http://127.0.0.1:8000/ in a browser and upload a CSV file. A sample file, `sample_hris.csv`, is included in the project root.

## Test instructions

Run the automated test suite with:
python manage.py test preview

This runs 4 focused tests against `preview/hris_parser.py`, independent of the browser:
- Duplicate `employee_id` rejection
- Root employee detection (no manager)
- Reporting cycle detection
- `manager_id` / `manager_email` conflict detection

## Complexity

Employee and manager lookups use dictionaries keyed by `employee_id` and `email`, so resolving a manager reference is O(1) rather than a linear scan. Overall, parsing and hierarchy resolution run in O(n) time and O(n) space relative to the number of employees. Cycle detection walks each employee's manager chain once; since every employee has at most one manager, each walk is bounded by the length of that chain, keeping the overall approach linear even at scale (e.g., ~100,000 employees).

## Assumptions and known limitations

- Analysis happens entirely in memory on upload; nothing is persisted to a database, per the exercise instructions.
- If `manager_id` and `manager_email` are both supplied and disagree, the row is flagged as an error rather than guessing which one is correct.
- An employee with a manager error is still counted as "accepted" but does not appear as a root and does not produce a reporting relationship.
- Cycle detection only flags employees who are actually part of the cycle itself, not employees who merely report into one.
- The CSV must contain all six required headers (`employee_id`, `employee_name`, `email`, `manager_id`, `manager_email`, `department`) in any order; a file missing any of them is rejected with a clear error instead of silently producing an empty result.
- The interface is plain, unstyled HTML — functionality and clarity were prioritized over visual polish, per the exercise's guidance.
- Given more time, I would add: a way to download the error list as CSV, pagination for large files in the browser view, and a visual org-tree rendering instead of a flat list of managers and counts.

## Time spent

Approximately 2 hours, excluding the video recording.

## AI tools used

I used Claude to help scaffold the Django project structure, work through Windows/PowerShell environment setup issues, and review my parsing and cycle-detection logic. When my code silently returned an empty result for an invalid file instead of an error, Claude suggested adding an explicit header-validation check — I agreed that was necessary and added it. I wrote and understand the core CSV parsing, manager-resolution, and cycle-detection logic myself, and can explain and modify any part of it.
