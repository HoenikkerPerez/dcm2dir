import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from dcm2dir.dcm2dir import main, process_dicom, organize_dicoms

class TestDCM2Dir(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_input_dir = tempfile.TemporaryDirectory()
        self.temp_output_dir = tempfile.TemporaryDirectory()
        self.temp_report_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        # Clean up temporary directories and files
        self.temp_input_dir.cleanup()
        self.temp_output_dir.cleanup()
        os.unlink(self.temp_report_file.name)

    def test_argument_parsing(self):
        # Mock command-line arguments
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
                )

    def test_process_dicom(self):
        # Mock a DICOM file and test processing
        mock_dicom_file = os.path.join(self.temp_input_dir.name, "test.dcm")
        with open(mock_dicom_file, "w") as f:
            f.write("Mock DICOM content")

        # Mock the output of process_dicom
        with patch("dcm2dir.dcm2dir.pydicom.dcmread") as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            result = process_dicom(mock_dicom_file, self.temp_output_dir.name, "%i/%x_%t/%s_%d")
            self.assertIsNotNone(result)

    def test_organize_dicoms(self):
        # Create mock DICOM files
        for i in range(3):
            with open(os.path.join(self.temp_input_dir.name, f"test_{i}.dcm"), "w") as f:
                f.write("Mock DICOM content")

        # Mock process_dicom to return dummy data
        with patch("dcm2dir.dcm2dir.process_dicom", return_value=("ID", "Date", "ExamID", "SeriesID", "Description")):
            organize_dicoms(
                self.temp_input_dir.name,
                self.temp_output_dir.name,
                self.temp_report_file.name,
                "%i/%x_%t/%s_%d",
            )

        # Check if the report file is generated
        self.assertTrue(os.path.exists(self.temp_report_file.name))
        with open(self.temp_report_file.name, "r") as f:
            content = f.readlines()
            self.assertGreater(len(content), 1)  # Ensure the CSV has data

    def test_folder_structure_conversion(self):
        # Test folder structure conversion (if applicable)
        from dcm2dir.dcm2dir import convert_folder_structure
        result = convert_folder_structure("%i/%x_%t/%s_%d")
        self.assertEqual(result, "{%i}/{%x}_{%t}/{%s}_{%d}")

if __name__ == "__main__":
    unittest.main()