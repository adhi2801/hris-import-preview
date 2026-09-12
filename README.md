\# HRIS Import Preview



A small Django application that lets a user upload an HRIS CSV export and

preview the data before anything is written to the Diversio platform: row

counts, validation errors, root employees, manager/direct-report counts,

and employees caught in a reporting cycle.



\## Setup and run instructions



1\. Create and activate a virtual environment (optional but recommended):

python -m venv venv

venv\\Scripts\\activate

2. Install dependencies:

pip install Django

3. Run the development server:

python manage.py runserver

4. Open http://127.0.0.1:8000/ in a browser and upload a CSV file

&#x20;  (`sample\_hris.csv` is included in the project root).



\## Test instructions



Run the automated test suite with:

python manage.py test preview

This runs 4 focused tests against the parsing/hierarchy logic in

`preview/hris\_parser.py`, independent of the browser:

\- duplicate employee\_id rejection

\- root employee detection (no manager)

\- reporting cycle detection

\- manager\_id / manager\_email conflict detection



\## Assumptions and known limitations



\- Analysis happens entirely in memory on upload; nothing is persisted to a

&#x20; database, per the exercise instructions.

\- If `manager\_id` and `manager\_email` are both supplied and disagree, the

&#x20; row is flagged as an error rather than guessing which one is correct.

\- An employee with a manager error is still counted as "accepted" but does

&#x20; not appear as a root and does not produce a reporting relationship, per

&#x20; the exercise's manager rules.

\- Cycle detection only flags employees who are actually part of the cycle

&#x20; itself, not employees who merely report into one.

\- The CSV must contain all six required headers (employee\_id,

&#x20; employee\_name, email, manager\_id, manager\_email, department) in any

&#x20; order; a file missing any of them is rejected with a clear error instead

&#x20; of silently producing an empty result.

\- The interface is plain, unstyled HTML — functionality and clarity were

&#x20; prioritized over visual polish, per the exercise's guidance.

\- Given more time, I would add: a way to download the error list as CSV,

&#x20; pagination for very large files in the browser view, and a visual

&#x20; org-tree rendering rather than a flat list of managers and counts.



\## Time spent



\[FILL IN: your approximate build time, excluding the video recording]



\## AI tools used



\[FILL IN: e.g. "I used Claude to help scaffold the Django project structure,

debug environment/settings issues, and review my parsing logic. I wrote and

reasoned through the core CSV parsing, validation, and cycle-detection logic

myself, and can explain every function in the walkthrough video."]



