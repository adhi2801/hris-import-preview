import csv
import io


class ParseResult:
    def __init__(self):
        self.total_rows = 0
        self.errors = []          # list of {"row": int, "message": str}
        self.accepted = {}        # employee_id -> employee dict
        self.roots = []           # employee_ids with no manager
        self.manager_counts = {}  # manager_id -> count of direct reports
        self.cyclic_ids = set()


def parse_hris_csv(file_obj):
    result = ParseResult()

    raw_bytes = file_obj.read()
    text = raw_bytes.decode("utf-8-sig")  # handles BOM automatically
    reader = csv.DictReader(io.StringIO(text))

    required_headers = {"employee_id", "employee_name", "email", "manager_id", "manager_email", "department"}
    actual_headers = set(reader.fieldnames or [])
    if not required_headers.issubset(actual_headers):
        missing = required_headers - actual_headers
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    seen_ids = {}
    seen_emails = {}
    rows = []

    for row_num, row in enumerate(reader, start=2):  # row 1 is the header
        result.total_rows += 1
        cleaned = {k: (v.strip() if v else "") for k, v in row.items()}
        cleaned["email"] = cleaned.get("email", "").lower()
        cleaned["manager_email"] = cleaned.get("manager_email", "").lower()
        rows.append((row_num, cleaned))

        emp_id = cleaned.get("employee_id", "")
        email = cleaned.get("email", "")

        if not emp_id or not email:
            result.errors.append({"row": row_num, "message": "Missing employee_id or email"})
            continue

        seen_ids.setdefault(emp_id, []).append(row_num)
        seen_emails.setdefault(email, []).append(row_num)

    # find duplicates
    duplicate_ids = {k for k, v in seen_ids.items() if len(v) > 1}
    duplicate_emails = {k for k, v in seen_emails.items() if len(v) > 1}

    for row_num, cleaned in rows:
        emp_id = cleaned.get("employee_id", "")
        email = cleaned.get("email", "")

        if not emp_id or not email:
            continue  # already logged above
        if emp_id in duplicate_ids:
            result.errors.append({"row": row_num, "message": f"Duplicate employee_id: {emp_id}"})
            continue
        if email in duplicate_emails:
            result.errors.append({"row": row_num, "message": f"Duplicate email: {email}"})
            continue

        result.accepted[emp_id] = cleaned

    # build id -> employee and email -> employee lookups for manager resolution
    by_id = result.accepted
    by_email = {v["email"]: v for v in result.accepted.values()}

    relationships = {}  # employee_id -> manager_id

    for emp_id, emp in result.accepted.items():
        manager_id = emp.get("manager_id", "")
        manager_email = emp.get("manager_email", "")

        if not manager_id and not manager_email:
            result.roots.append(emp_id)
            continue

        manager_by_id = by_id.get(manager_id) if manager_id else None
        manager_by_email = by_email.get(manager_email) if manager_email else None

        if manager_id and manager_email:
            if not manager_by_id or not manager_by_email or manager_by_id["employee_id"] != manager_by_email["employee_id"]:
                result.errors.append({"row": None, "message": f"{emp_id}: manager_id and manager_email do not match the same person"})
                continue
            manager = manager_by_id
        elif manager_id:
            manager = manager_by_id
        else:
            manager = manager_by_email

        if not manager:
            result.errors.append({"row": None, "message": f"{emp_id}: manager not found"})
            continue

        if manager["employee_id"] == emp_id:
            result.errors.append({"row": None, "message": f"{emp_id}: cannot be their own manager"})
            continue

        relationships[emp_id] = manager["employee_id"]
        result.manager_counts[manager["employee_id"]] = result.manager_counts.get(manager["employee_id"], 0) + 1

    # detect cycles: walk up the manager chain from each employee
    def find_cycle_members(start_id):
        visited = []
        current = start_id
        seen = set()
        while current in relationships:
            if current in seen:
                # found the cycle: everything from the first repeat onward
                cycle_start_index = visited.index(current)
                return set(visited[cycle_start_index:])
            seen.add(current)
            visited.append(current)
            current = relationships[current]
        return set()

    for emp_id in relationships:
        cycle = find_cycle_members(emp_id)
        result.cyclic_ids.update(cycle)

    return result