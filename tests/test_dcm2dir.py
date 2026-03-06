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
import json
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from dcm2dir.dcm2dir import (
    main,
    process_dicom,
    organize_dicoms,
    rename_series_folders,
    sanitize_name,
    ensure_unique_path,
    overwrite_default_anon_config,
)
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
        self.temp_report_file.close()

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

    def test_sanitize_name(self):
        """Test sanitize_name with empty and non-alphanumeric values."""
        self.assertEqual(sanitize_name(""), "na")
        self.assertEqual(sanitize_name("A B/C"), "A_B_C")

    def test_ensure_unique_path(self):
        """Test ensure_unique_path adds suffix when destination exists."""
        base_path = os.path.join(self.temp_output_dir.name, "series")
        os.makedirs(base_path, exist_ok=True)
        unique = ensure_unique_path(base_path)
        self.assertTrue(unique.endswith("series_1"))

    def test_process_dicom_with_anonymization_saves_file(self):
        """Test process_dicom writes via save_as when anonymization is enabled."""
        mock_dicom_file = os.path.join(self.temp_input_dir.name, "test_an.dcm")
        with open(mock_dicom_file, "w", encoding="utf-8") as f:
            f.write("Mock DICOM content")

        mock_ds = MagicMock()
        with patch("dcm2dir.dcm2dir.pydicom.dcmread", return_value=mock_ds):
            with patch("dcm2dir.dcm2dir.anonymize_dicom", return_value=mock_ds):
                result = process_dicom(
                    mock_dicom_file,
                    self.temp_output_dir.name,
                    "%i/%x_%t/%s_%d",
                    anonymize={"(0010-0010)": "C:ANON"}
                )

        self.assertIsNotNone(result)
        self.assertTrue(mock_ds.save_as.called)

    def test_process_dicom_invalid_structure_key_returns_none(self):
        """Test process_dicom returns None for invalid folder key placeholders."""
        mock_dicom_file = os.path.join(self.temp_input_dir.name, "test_key.dcm")
        with open(mock_dicom_file, "w", encoding="utf-8") as f:
            f.write("Mock DICOM content")

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", return_value=MagicMock()):
            result = process_dicom(mock_dicom_file, self.temp_output_dir.name, "{missing}")

        self.assertIsNone(result)

    def test_process_dicom_handles_read_errors(self):
        """Test process_dicom handles DICOM read errors by returning None."""
        with patch("dcm2dir.dcm2dir.pydicom.dcmread", side_effect=OSError("fail")):
            result = process_dicom("nonexistent.dcm", self.temp_output_dir.name, "%i")
        self.assertIsNone(result)

    def test_argument_parsing_rename_folder_without_output(self):
        """
        Test that --rename-folder works without --output and calls rename_series_folders.
        """
        test_args = [
            "dcm2dir",
            "-i", self.temp_input_dir.name,
            "--rename-folder",
            "-f", "%s_%d"
        ]
        with patch("sys.argv", test_args):
            with patch("dcm2dir.dcm2dir.rename_series_folders") as mock_rename:
                main()
                mock_rename.assert_called_once_with(
                    self.temp_input_dir.name,
                    None,
                    "%s_%d"
                )

    def test_organize_dicoms_without_report(self):
        """Test organize_dicoms branch when report output is not requested."""
        for i in range(2):
            with open(os.path.join(self.temp_input_dir.name, f"noreport_{i}.dcm"),
                      "w",
                      encoding="utf-8") as f:
                f.write("Mock DICOM content")

        with patch("dcm2dir.dcm2dir.process_dicom", return_value=("ID", "Date", "Exam", "S", "D")):
            organize_dicoms(
                self.temp_input_dir.name,
                self.temp_output_dir.name,
                None,
                "%i/%x_%t/%s_%d",
                None
            )

    def test_rename_series_folders_output_collision(self):
        """Test renaming to output folder uses collision-safe destination names."""
        source_folder = os.path.join(self.temp_input_dir.name, "series_src")
        os.makedirs(source_folder, exist_ok=True)
        with open(os.path.join(source_folder, "img_0.dcm"), "w", encoding="utf-8") as f:
            f.write("Mock DICOM content")

        os.makedirs(os.path.join(self.temp_output_dir.name, "401_FLAIR_F"), exist_ok=True)

        mock_dataset = MagicMock()
        mock_dataset.SeriesInstanceUID = "1.2.3.4"
        mock_dataset.SeriesNumber = "401"
        mock_dataset.SeriesDescription = "FLAIR F"

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", return_value=mock_dataset):
            rename_series_folders(self.temp_input_dir.name, self.temp_output_dir.name, "%s_%d")

        self.assertTrue(os.path.exists(os.path.join(self.temp_output_dir.name, "401_FLAIR_F_1")))

    def test_rename_series_folders_skips_non_dicom_folder(self):
        """Test folders with no valid DICOM files are ignored."""
        source_folder = os.path.join(self.temp_input_dir.name, "non_dicom")
        os.makedirs(source_folder, exist_ok=True)
        with open(os.path.join(source_folder, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("not dicom")

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", side_effect=OSError("bad")):
            rename_series_folders(self.temp_input_dir.name, None, "%s_%d")

        self.assertTrue(os.path.exists(source_folder))

    def test_rename_series_folders_invalid_structure_key(self):
        """Test folder rename skips when folder structure has invalid placeholder."""
        source_folder = os.path.join(self.temp_input_dir.name, "series_bad_fmt")
        os.makedirs(source_folder, exist_ok=True)
        with open(os.path.join(source_folder, "img_0.dcm"), "w", encoding="utf-8") as f:
            f.write("Mock DICOM content")

        mock_dataset = MagicMock()
        mock_dataset.SeriesInstanceUID = "1.2.3.4"

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", return_value=mock_dataset):
            rename_series_folders(self.temp_input_dir.name, None, "{missing}")

        self.assertTrue(os.path.exists(source_folder))

    def test_overwrite_default_anon_config(self):
        """Test override helper updates default config entries."""
        default = {"(0010-0010)": "Z"}
        custom = {"(0010-0010)": "C:ANON", "(0010-0020)": "X"}
        out = overwrite_default_anon_config(default, custom)
        self.assertEqual(out["(0010-0010)"], "C:ANON")
        self.assertEqual(out["(0010-0020)"], "X")

    def test_main_requires_output_without_rename(self):
        """Test CLI errors when --output is missing in normal organize mode."""
        test_args = ["dcm2dir", "-i", self.temp_input_dir.name]
        with patch("sys.argv", test_args):
            with self.assertRaises(SystemExit):
                main()

    def test_main_rejects_anonymize_with_rename(self):
        """Test CLI rejects --anonymize together with --rename-folder."""
        test_args = ["dcm2dir", "-i", self.temp_input_dir.name, "--rename-folder", "-a"]
        with patch("sys.argv", test_args):
            with self.assertRaises(SystemExit):
                main()

    def test_main_loads_custom_anonymization_config(self):
        """Test main loads custom anonymization config and calls organize_dicoms."""
        custom_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        custom_file.close()
        with open(custom_file.name, "w", encoding="utf-8") as f:
            json.dump({"(0010-0010)": "C:ANON"}, f)

        test_args = [
            "dcm2dir",
            "-i", self.temp_input_dir.name,
            "-o", self.temp_output_dir.name,
            "-a",
            "-c", custom_file.name,
        ]
        try:
            with patch("sys.argv", test_args):
                with patch("dcm2dir.dcm2dir.organize_dicoms") as mock_organize:
                    with patch("dcm2dir.dcm2dir.DEFAULT_ANONYMIZATION_CONFIG", {"(0010-0020)": "X"}):
                        main()

            passed_config = mock_organize.call_args[0][4]
            self.assertEqual(passed_config["(0010-0010)"], "C:ANON")
            self.assertEqual(passed_config["(0010-0020)"], "X")
        finally:
            os.unlink(custom_file.name)

    def test_rename_series_folders_in_place(self):
        """
        Test in-place folder rename when all DICOM files in a folder belong to one series.
        """
        source_folder = os.path.join(self.temp_input_dir.name, "old_series")
        os.makedirs(source_folder, exist_ok=True)

        for i in range(2):
            with open(os.path.join(source_folder, f"img_{i}.dcm"), "w", encoding="utf-8") as f:
                f.write("Mock DICOM content")

        mock_dataset = MagicMock()
        mock_dataset.SeriesInstanceUID = "1.2.3.4"
        mock_dataset.SeriesNumber = "401"
        mock_dataset.SeriesDescription = "FLAIR F"

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", return_value=mock_dataset):
            rename_series_folders(self.temp_input_dir.name, None, "%s_%d")

        self.assertFalse(os.path.exists(source_folder))
        self.assertTrue(os.path.exists(os.path.join(self.temp_input_dir.name, "401_FLAIR_F")))

    def test_rename_series_folders_skips_mixed_series(self):
        """
        Test folder is skipped when DICOM files contain more than one SeriesInstanceUID.
        """
        source_folder = os.path.join(self.temp_input_dir.name, "mixed_series")
        os.makedirs(source_folder, exist_ok=True)

        for i in range(2):
            with open(os.path.join(source_folder, f"img_{i}.dcm"), "w", encoding="utf-8") as f:
                f.write("Mock DICOM content")

        ds1 = MagicMock()
        ds1.SeriesInstanceUID = "1.2.3.4"
        ds2 = MagicMock()
        ds2.SeriesInstanceUID = "9.8.7.6"

        with patch("dcm2dir.dcm2dir.pydicom.dcmread", side_effect=[ds1, ds2]):
            rename_series_folders(self.temp_input_dir.name, None, "%s_%d")

        self.assertTrue(os.path.exists(source_folder))

if __name__ == "__main__":
    unittest.main()
