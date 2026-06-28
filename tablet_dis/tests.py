from django.test import SimpleTestCase, TestCase, Client

from tablet_dis.tablet_checker import (
    validate_input_format,
    normalize_input,
    INVALID_INPUT,
)


class TabletCheckerFormatTests(SimpleTestCase):
    def test_valid_medicine_names(self):
        valid = [
            "Paracetamol",
            "Dolo 650",
            "Crocin Advance",
            "Vitamin C",
            "Amoxicillin 500",
            "crocin",
        ]
        for name in valid:
            with self.subTest(name=name):
                result = validate_input_format(name)
                self.assertTrue(result.ok, msg=f"{name} should be valid")

    def test_reject_empty(self):
        result = validate_input_format("   ")
        self.assertFalse(result.ok)
        self.assertEqual(result.message, INVALID_INPUT)

    def test_reject_numbers_only(self):
        for name in ["12345", "9876", "000"]:
            with self.subTest(name=name):
                result = validate_input_format(name)
                self.assertFalse(result.ok)

    def test_reject_keyboard_mash(self):
        for name in ["asdfgh", "qwerty", "xyzabc"]:
            with self.subTest(name=name):
                result = validate_input_format(name)
                self.assertFalse(result.ok)

    def test_reject_unrelated_words(self):
        for name in ["Apple", "Bangalore", "India", "Dog", "Suresh", "John"]:
            with self.subTest(name=name):
                result = validate_input_format(name)
                self.assertFalse(result.ok)

    def test_reject_symbols_only(self):
        result = validate_input_format("@#$%^")
        self.assertFalse(result.ok)

    def test_normalize_input(self):
        self.assertEqual(normalize_input("  Dolo   650  "), "dolo 650")
        self.assertEqual(normalize_input("Paracetamol"), "paracetamol")


class TabletCheckerViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_invalid_input_page(self):
        response = self.client.get("/en/tablet/asdfgh/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, INVALID_INPUT)

    def test_invalid_numbers_page(self):
        response = self.client.get("/en/tablet/123456/")
        self.assertContains(response, INVALID_INPUT)

    def test_valid_medicine_page(self):
        response = self.client.get("/en/tablet/Paracetamol/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, INVALID_INPUT)

    def test_validate_search_api(self):
        response = self.client.get("/en/validate-search/?q=qwerty")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertEqual(data["message"], INVALID_INPUT)

        response = self.client.get("/en/validate-search/?q=Paracetamol")
        data = response.json()
        self.assertTrue(data["ok"])
