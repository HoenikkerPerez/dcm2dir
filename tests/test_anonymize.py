"""Unit tests for anonymization helpers and DICOM anonymization behavior."""

import unittest
from unittest.mock import MagicMock, patch

from pydicom.dataset import Dataset
from pydicom.tag import Tag

from dcm2dir.anonymize.anonymize import (
    anonymize_dicom,
    change_value,
    empty_value,
    generate_unique_uid,
    hash_value,
    string_to_tag,
)


class TestAnonymizeHelpers(unittest.TestCase):
    """Tests for helper functions in anonymize module."""

    def test_generate_unique_uid_without_entropy(self):
        uid = generate_unique_uid()
        self.assertIsInstance(uid, str)
        self.assertIn(".", uid)

    def test_generate_unique_uid_with_entropy_prefix(self):
        uid = generate_unique_uid("abc")
        self.assertTrue(uid.startswith("1.2.826.0.1."))

    def test_empty_value_returns_attribute(self):
        tag = MagicMock()
        tag.empty_value = ""
        self.assertEqual(empty_value(tag), "")

    def test_change_value_returns_new_value(self):
        tag = MagicMock()
        self.assertEqual(change_value(tag, "NEW"), "NEW")

    def test_string_to_tag_parses_hex(self):
        self.assertEqual(string_to_tag("(0010-0010)"), Tag(0x0010, 0x0010))

    def test_hash_value_vr_branches(self):
        tag_sh = MagicMock(value="abc", VR="SH")
        tag_da = MagicMock(value="20200101", VR="DA")
        tag_as = MagicMock(value="034Y", VR="AS")
        tag_pn = MagicMock(value="John^Doe", VR="PN")
        tag_lo = MagicMock(value="long text", VR="LO")

        self.assertEqual(len(hash_value(tag_sh)), 16)
        self.assertEqual(hash_value(tag_da), "19000101")
        self.assertEqual(len(hash_value(tag_as)), 4)
        self.assertTrue(hash_value(tag_pn).startswith("ANON_"))
        self.assertEqual(len(hash_value(tag_lo)), 64)

    def test_hash_value_handles_empty_and_unsupported_vr(self):
        tag_empty = MagicMock(value="", VR="LO")
        self.assertEqual(hash_value(tag_empty), "")

        tag_bad = MagicMock(value="abc", VR="UN")
        with self.assertRaises(ValueError):
            hash_value(tag_bad)


class TestAnonymizeDicom(unittest.TestCase):
    """Tests for anonymize_dicom action handling."""

    def _build_dataset(self):
        ds = Dataset()
        ds.add_new(Tag(0x0008, 0x0080), "LO", "Institution")
        ds.add_new(Tag(0x0008, 0x0020), "DA", "20240201")
        ds.add_new(Tag(0x0008, 0x0090), "PN", "Ref^Phys")
        ds.add_new(Tag(0x0010, 0x0010), "PN", "Patient^Name")
        ds.add_new(Tag(0x0008, 0x0018), "UI", "1.2.3.4")
        return ds

    def test_anonymize_dicom_applies_x_z_d_c_u(self):
        ds = self._build_dataset()
        config = {
            "(0008-0080)": "X",
            "(0008-0020)": "Z",
            "(0008-0090)": "D",
            "(0010-0010)": "C:ANON^NAME",
            "(0008-0018)": "U",
        }

        out = anonymize_dicom(ds, config)
        self.assertNotIn(Tag(0x0008, 0x0080), out)
        self.assertEqual(out[Tag(0x0008, 0x0020)].value, "")
        self.assertEqual(out[Tag(0x0010, 0x0010)].value, "ANON^NAME")
        self.assertNotEqual(out[Tag(0x0008, 0x0018)].value, "1.2.3.4")

    def test_anonymize_dicom_d_and_u_exception_paths(self):
        ds = self._build_dataset()
        config = {
            "(0008-0090)": "D",
            "(0008-0018)": "U",
        }

        with patch("dcm2dir.anonymize.anonymize.hash_value", side_effect=Exception("x")):
            with patch("dcm2dir.anonymize.anonymize.generate_unique_uid", side_effect=TypeError):
                with patch("builtins.print") as mock_print:
                    anonymize_dicom(ds, config)

        printed = "\n".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Could not hash tag", printed)
        self.assertIn("Could not generate a unique UID", printed)


if __name__ == "__main__":
    unittest.main()
