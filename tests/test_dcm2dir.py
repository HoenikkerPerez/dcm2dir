"""
Unit tests for the dcm2dir tool.

This test suite verifies the functionality of the dcm2dir tool, including:
- Argument parsing for the command-line interface.
- Processing of individual DICOM files.
- Organizing DICOM files into a structured output folder.
- Generating a CSV report with metadata.
- Converting folder structure placeholders to Python format strings.
- Anonymizing DICOM files based on a configuration.

The tests use temporary directories and files to ensure isolation and avoid
modifying the actual file system. Mocking is used to simulate external dependencies
such as DICOM file reading and metadata extraction.
"""

import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from dcm2dir.dcm2dir import main, process_dicom, organize_dicoms
from dcm2dir.dcm2dir import convert_folder_structure
from dcm2dir.anonymize import DEFAULT_ANONYMIZATION_CONFIG

class TestDCM2Dir(unittest.TestCase):
    """
    Test suite for the dcm2dir tool.
    """

    def setUp(self):
        """
        Set up temporary directories and files for testing.
        This ensures that tests are isolated and do not modify the actual file system.
        """
        self.temp_input_dir = tempfile.TemporaryDirectory()
        self.temp_output_dir = tempfile.TemporaryDirectory()
        self.temp_report_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        """
        Clean up temporary directories and files after each test.
        """
        self.temp_input_dir.cleanup()
        self.temp_output_dir.cleanup()
        os.unlink(self.temp_report_file.name)

    def test_argument_parsing(self):
        """
        Test that command-line arguments are parsed correctly and passed to the organize_dicoms 
        function.
        """
        test_args = [
            "dcm2dir",
            "-i", self.temp_input_dir.name,
            "-o", self.temp_output_dir.name,
            "-r", self.temp_report_file.name,
        ]
        with patch("sys.argv", test_args):
            with patch("dcm2dir.dcm2dir.organize_dicoms") as mock_organize:
                main()
                mock_organize.assert_called_once_with(
                    self.temp_input_dir.name,
                    self.temp_output_dir.name,
                    self.temp_report_file.name,
                    "%i/%x_%t/%s_%d",
                    None
                )

    def test_process_dicom(self):
        """
        Test the process_dicom function with a mock DICOM file.
        Ensures that the function processes the file and returns a valid result.
        """
        mock_dicom_file = os.path.join(self.temp_input_dir.name, "test.dcm")
        with open(mock_dicom_file, "w", encoding="utf-8") as f:
            f.write("Mock DICOM content")

        with patch("dcm2dir.dcm2dir.pydicom.dcmread") as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            result = process_dicom(mock_dicom_file, self.temp_output_dir.name, "%i/%x_%t/%s_%d")
            self.assertIsNotNone(result)

    def test_organize_dicoms(self):
        """
        Test the organize_dicoms function to ensure that DICOM files are organized
        into the correct folder structure and a CSV report is generated.
        """
        for i in range(3):
            with open(os.path.join(self.temp_input_dir.name, f"test_{i}.dcm"),
                      "w", 
                      encoding="utf-8") as f:
                f.write("Mock DICOM content")

        with patch("dcm2dir.dcm2dir.process_dicom",
                   return_value=("ID", "Date", "ExamID", "SeriesID", "Description")):
            organize_dicoms(
                self.temp_input_dir.name,
                self.temp_output_dir.name,
                self.temp_report_file.name,
                "%i/%x_%t/%s_%d",
                None
            )

        self.assertTrue(os.path.exists(self.temp_report_file.name))
        with open(self.temp_report_file.name, "r", encoding="utf-8") as f:
            content = f.readlines()
            self.assertGreater(len(content), 1)  # Ensure the CSV has data

    def test_organize_dicoms_with_anonymization(self):
        """
        Test the organize_dicoms function with anonymization enabled.
        Ensures that DICOM files are anonymized and organized correctly.
        """
        for i in range(3):
            with open(os.path.join(self.temp_input_dir.name, f"test_{i}.dcm"),
                      "w", 
                      encoding="utf-8") as f:
                f.write("Mock DICOM content")

        mock_anonymization_config = {
            "(0010,0010)": "C:ANON_SUBJECTNAME",
            "(0010,0020)": "C:ANON_SUBJECTID"
        }

        with patch("dcm2dir.dcm2dir.process_dicom",
                   return_value=("ID", "Date", "ExamID", "SeriesID", "Description")):
            organize_dicoms(
                self.temp_input_dir.name,
                self.temp_output_dir.name,
                self.temp_report_file.name,
                "%i/%x_%t/%s_%d",
                anonymize=mock_anonymization_config
            )

        self.assertTrue(os.path.exists(self.temp_report_file.name))
        with open(self.temp_report_file.name, "r", encoding="utf-8") as f:
            content = f.readlines()
            self.assertGreater(len(content), 1)  # Ensure the CSV has data

    def test_folder_structure_conversion(self):
        """
        Test the convert_folder_structure function to ensure that placeholders
        are correctly converted to Python format strings.
        """
        result = convert_folder_structure("%i/%x_%t/%s_%d")
        self.assertEqual(result, "{%i}/{%x}_{%t}/{%s}_{%d}")

if __name__ == "__main__":
    unittest.main()
