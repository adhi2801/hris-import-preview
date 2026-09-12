import io
from django.test import TestCase
from .hris_parser import parse_hris_csv


def make_file(csv_text):
    return io.BytesIO(csv_text.encode("utf-8"))


class HrisParserTests(TestCase):

    def test_duplicate_employee_id_is_rejected(self):
        csv_text = (
            "employee_id,employee_name,email,manager_id,manager_email,department\n"
            "E1,Alice,alice@x.com,,,Eng\n"
            "E1,Alice Two,alice2@x.com,,,Eng\n"
        )
        result = parse_hris_csv(make_file(csv_text))
        self.assertEqual(result.total_rows, 2)
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.errors), 2)

    def test_root_employee_with_no_manager(self):
        csv_text = (
            "employee_id,employee_name,email,manager_id,manager_email,department\n"
            "E1,Alice,alice@x.com,,,Eng\n"
        )
        result = parse_hris_csv(make_file(csv_text))
        self.assertEqual(result.roots, ["E1"])
        self.assertEqual(len(result.errors), 0)

    def test_simple_reporting_cycle_is_detected(self):
        csv_text = (
            "employee_id,employee_name,email,manager_id,manager_email,department\n"
            "E1,Alice,alice@x.com,E2,,Eng\n"
            "E2,Bob,bob@x.com,E1,,Eng\n"
        )
        result = parse_hris_csv(make_file(csv_text))
        self.assertEqual(result.cyclic_ids, {"E1", "E2"})

    def test_manager_id_and_email_conflict_is_an_error(self):
        csv_text = (
            "employee_id,employee_name,email,manager_id,manager_email,department\n"
            "E1,Alice,alice@x.com,,,Eng\n"
            "E2,Bob,bob@x.com,,,Eng\n"
            "E3,Carl,carl@x.com,E1,bob@x.com,Eng\n"
        )
        result = parse_hris_csv(make_file(csv_text))
        self.assertTrue(any("do not match" in e["message"] for e in result.errors))