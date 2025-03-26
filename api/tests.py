import io
import csv
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from userManagement.models import User


class ImportUsersTestCase(APITestCase):
    
    def setUp(self):
        self.import_url = reverse("users_import") 

    def create_csv_file(self, data):
        """Helper function to create a CSV file."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "email", "age"])  # CSV header
        writer.writerows(data)
        output.seek(0)
        return SimpleUploadedFile("test.csv", output.getvalue().encode("utf-8"), content_type="text/csv")

    def test_successful_import(self):
        """Test that valid users are imported successfully."""
        csv_file = self.create_csv_file([
            ["John Doe", "john@example.com", "25"],
            ["Jane Doe", "jane@example.com", "30"]
        ])

        response = self.client.post(self.import_url, {"file": csv_file}, format="multipart")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data["success"], 2)

    def test_invalid_file_type(self):
        """Test that non-CSV files are rejected."""
        file = SimpleUploadedFile("test.txt", b"Invalid file content", content_type="text/plain")
        response = self.client.post(self.import_url, {"file": file}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "Only .csv file is accepted")

    def test_empty_file(self):
        """Test handling of an empty CSV file."""
        empty_csv = self.create_csv_file([])
        response = self.client.post(self.import_url, {"file": empty_csv}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data["success"], 0)

    def test_invalid_email(self):
        """Test handling of invalid email addresses."""
        csv_file = self.create_csv_file([
            ["John Doe", "invalid-email", "25"]
        ])
        response = self.client.post(self.import_url, {"file": csv_file}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["message"], "Invalid email address")

    def test_missing_fields(self):
        """Test handling of missing fields."""
        csv_file = self.create_csv_file([
            ["John Doe", "", "25"],  # Missing email
            ["", "jane@example.com", "30"],  # Missing name
            ["Alice", "alice@example.com", ""]  # Missing age
        ])
        response = self.client.post(self.import_url, {"file": csv_file}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(response.data["errors"]), 3)

    def test_duplicate_users(self):
        """Test that duplicate users are not imported."""
        User.objects.create(name="John Doe", email="john@example.com", age=25)

        csv_file = self.create_csv_file([
            ["John Doe", "john@example.com", "25"]  # Duplicate entry
        ])

        response = self.client.post(self.import_url, {"file": csv_file}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)  # Should remain 1
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["message"], "User already exists")

    def test_invalid_age(self):
        """Test handling of invalid age values."""
        csv_file = self.create_csv_file([
            ["John Doe", "john@example.com", "-5"],  # Negative age
            ["Jane Doe", "jane@example.com", "150"],  # Unrealistic age
            ["Alice", "alice@example.com", "not_a_number"]  # Non-numeric age
        ])

        response = self.client.post(self.import_url, {"file": csv_file}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(response.data["errors"]), 3)

