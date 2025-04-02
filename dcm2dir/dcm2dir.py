"""
dcm2dir: A tool to organize DICOM files into a structured folder hierarchy.

This script recursively scans a given root folder for DICOM files, extracts relevant metadata,
and organizes the files into a structured output folder. The folder structure is customizable
using placeholders for different DICOM tags. Additionally, a CSV report can be generated with
details of all processed DICOM series.

Features:
- Recursively scans and organizes DICOM files.
- Supports customizable folder structures using placeholders.
- Utilizes multi-threading for faster processing.
- Generates a CSV report listing all series metadata.
- Handles missing DICOM tags gracefully.

Usage:
    python dcm2dir.py -i <input_folder> -o <output_folder> [-r <csv_report>] [-f <folder_structure>]

Arguments:
    -i, --input (required): Path to the root folder containing DICOM files.
    -o, --output (required): Path to the destination folder where organized files will be stored.
    -r, --report (optional): Path to save the generated CSV report.
    -f, --folder-structure (optional): Custom folder structure using placeholders.
"""

import os
import shutil
import csv
import re
import argparse
import concurrent.futures
import json

from .anonymize import anonymize_dicom, DEFAULT_ANONYMIZATION_CONFIG
import pydicom
from tqdm import tqdm


def sanitize_name(name, placeholder="na"):
    """
    Sanitize names by replacing non-alphanumeric characters with underscores.

    Args:
        name (str): The name to sanitize.
        placeholder (str): The default value to use if the name is None or empty.

    Returns:
        str: The sanitized name.
    """
    if not name:
        return placeholder
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


def convert_folder_structure(string):
    """
    Converts the placeholder syntax to Python's format string.

    Args:
        string (str): The folder structure string with placeholders (e.g., "%i/%x_%t/%s_%d").

    Returns:
        str: The folder structure string converted to Python's format string syntax.
    """
    return re.sub(r"(%[a-zA-Z])", r"{\1}", string)


def process_dicom(file_path, output_folder, folder_structure, anonymize=None):
    """
    Reads a DICOM file, extracts relevant metadata, anonymizes it (if required),
    and copies it to the structured output folder.

    Args:
        file_path (str): Path to the DICOM file.
        output_folder (str): Path to the destination folder.
        folder_structure (str): Custom folder structure using placeholders.
        anonymize (dict): Dictionary of anonymization actions, or None.
    Returns:
        list: A list of metadata values for the CSV report, or None if the file 
        could not be processed.
    """
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        
        # Extract and sanitize ORIGINAL DICOM tags
        original_metadata = {
            "%a": sanitize_name(str(getattr(ds, "Coil", "na"))),
            "%b": sanitize_name(os.path.basename(file_path)),
            "%c": sanitize_name(str(getattr(ds, "ImageComments", "na"))),
            "%d": sanitize_name(str(getattr(ds, "SeriesDescription", "na"))),
            "%e": sanitize_name(str(getattr(ds, "EchoNumbers", "na"))),
            "%f": sanitize_name(os.path.dirname(file_path)),
            "%g": sanitize_name(str(getattr(ds, "AccessionNumber", "na"))),
            "%i": sanitize_name(str(getattr(ds, "PatientID", "na"))),
            "%j": sanitize_name(str(getattr(ds, "SeriesInstanceUID", "na"))),
            "%k": sanitize_name(str(getattr(ds, "StudyInstanceUID", "na"))),
            "%m": sanitize_name(str(getattr(ds, "Manufacturer", "na"))),
            "%n": sanitize_name(str(getattr(ds, "PatientName", "na"))),
            "%o": sanitize_name(str(getattr(ds, "MediaStorageSOPInstanceUID", "na"))),
            "%p": sanitize_name(str(getattr(ds, "ProtocolName", "na"))),
            "%r": sanitize_name(str(getattr(ds, "InstanceNumber", "na"))),
            "%s": sanitize_name(str(getattr(ds, "SeriesNumber", "na"))),
            "%t": sanitize_name(str(getattr(ds, "StudyDate", "na"))),
            "%u": sanitize_name(str(getattr(ds, "AcquisitionNumber", "na"))),
            "%v": sanitize_name(str(getattr(ds, "ManufacturerModelName", "na"))),
            "%x": sanitize_name(str(getattr(ds, "StudyID", "na"))),
            "%z": sanitize_name(str(getattr(ds, "SequenceName", "na")))
        }
        # Anonymize the DICOM file if the flag is set
        if anonymize is not None:
            ds = anonymize_dicom(ds, anonymize)

        # Extract and sanitize DICOM tags
        metadata = {
            "%a": sanitize_name(str(getattr(ds, "Coil", "na"))),
            "%b": sanitize_name(os.path.basename(file_path)),
            "%c": sanitize_name(str(getattr(ds, "ImageComments", "na"))),
            "%d": sanitize_name(str(getattr(ds, "SeriesDescription", "na"))),
            "%e": sanitize_name(str(getattr(ds, "EchoNumbers", "na"))),
            "%f": sanitize_name(os.path.dirname(file_path)),
            "%g": sanitize_name(str(getattr(ds, "AccessionNumber", "na"))),
            "%i": sanitize_name(str(getattr(ds, "PatientID", "na"))),
            "%j": sanitize_name(str(getattr(ds, "SeriesInstanceUID", "na"))),
            "%k": sanitize_name(str(getattr(ds, "StudyInstanceUID", "na"))),
            "%m": sanitize_name(str(getattr(ds, "Manufacturer", "na"))),
            "%n": sanitize_name(str(getattr(ds, "PatientName", "na"))),
            "%o": sanitize_name(str(getattr(ds, "MediaStorageSOPInstanceUID", "na"))),
            "%p": sanitize_name(str(getattr(ds, "ProtocolName", "na"))),
            "%r": sanitize_name(str(getattr(ds, "InstanceNumber", "na"))),
            "%s": sanitize_name(str(getattr(ds, "SeriesNumber", "na"))),
            "%t": sanitize_name(str(getattr(ds, "StudyDate", "na"))),
            "%u": sanitize_name(str(getattr(ds, "AcquisitionNumber", "na"))),
            "%v": sanitize_name(str(getattr(ds, "ManufacturerModelName", "na"))),
            "%x": sanitize_name(str(getattr(ds, "StudyID", "na"))),
            "%z": sanitize_name(str(getattr(ds, "SequenceName", "na")))
        }

        # Apply default folder structure if none is provided
        if not folder_structure:
            folder_structure = "%i/%x_%t/%s_%d"

        # Validate and generate folder structure based on user-defined syntax
        try:
            dest_folder = os.path.join(output_folder, folder_structure.format(**metadata))
            dest_folder = os.path.normpath(dest_folder)
        except KeyError as e:
            print(f"Invalid folder structure key: {e}")
            return None

        os.makedirs(dest_folder, exist_ok=True)

        # Save the anonymized DICOM file if anonymization is enabled
        if anonymize is not None:
            anonymized_file_path = os.path.join(dest_folder, os.path.basename(file_path))
            ds.save_as(anonymized_file_path)
        else:
            shutil.copy2(file_path, dest_folder)

        return [original_metadata["%i"], original_metadata["%t"], 
                original_metadata["%x"], original_metadata["%s"], original_metadata["%d"]]
    except (pydicom.errors.InvalidDicomError, KeyError, OSError) as e:
        print(f"Skipping {file_path}: {e}")
        return None


def organize_dicoms(root_folder, output_folder, report_path, folder_structure, anonymize=None):
    """
    Recursively scans DICOM files, processes them based on the provided parameters,
    and organizes them into a structured output folder. Optionally, generates a CSV report
    with details of all processed DICOM series. Anonymization can be enabled.

    Args:
        root_folder (str): Path to the root folder containing DICOM files.
        output_folder (str): Path to the destination folder.
        report_path (str): Path to save the CSV report (optional).
        folder_structure (str): Custom folder structure using placeholders.
        anonymize (dict): Dictionary of anonymization actions, or None 
    """
    folder_structure = convert_folder_structure(folder_structure)

    dicom_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            dicom_files.append(os.path.join(dirpath, file))

    dicom_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            tqdm(executor.map(
                lambda f: process_dicom(f, output_folder, folder_structure, anonymize),
                dicom_files),
                 total=len(dicom_files),
                 desc="Processing DICOMs"))

    dicom_data = [r for r in results if r]

    # Write CSV report if provided
    if report_path:
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["SubjectID", "ExamDate", "ExamID", "SeriesID", "SeriesDescription"])
            for row in sorted(dicom_data, key=lambda x: (x[0], x[1])):
                writer.writerow(row)
        print(f"Processing completed. CSV report saved at {report_path}")
    else:
        print("Processing completed. No CSV report generated.")


def overwrite_default_anon_config(default_config_dict, custom_conf_dict):
    """
    Overwrites the default anonymization configuration with custom values.

    Args:
        default_config_dict (dict): The default anonymization configuration dictionary.
        custom_conf_dict (dict): The custom anonymization configuration dictionary.

    Returns:
        dict: The updated anonymization configuration dictionary.
    """
    for tag_id, metadata in custom_conf_dict.items():
        default_config_dict[tag_id] = metadata
    return default_config_dict


def main():
    """
    Entry point for the script. Parses command-line arguments and organizes DICOM files.
    """
    print("Luca Peretti's dcm2dir version v1.1.0.20250402")

    parser = argparse.ArgumentParser(
        description="Organize DICOM files recursively and generate a CSV report."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the root DICOM folder")
    parser.add_argument("-o", "--output", required=True, help="Path to the destination folder")
    parser.add_argument("-r", "--report", help="Path to save the CSV report (optional)")
    parser.add_argument("-f", "--folder-structure", default="%i/%x_%t/%s_%d",
                        help="Folder structure using placeholders: "
                             "%%a=antenna (coil) name,  "
                             "%%b=basename,  "
                             "%%c=comments,  "
                             "%%d=description,  "
                             "%%e=echo number,  "
                             "%%f=folder name,  "
                             "%%g=accession number,  "
                             "%%i=ID of patient,  "
                             "%%j=seriesInstanceUID,  "
                             "%%k=studyInstanceUID,  "
                             "%%m=manufacturer,  "
                             "%%n=name of patient,  "
                             "%%o=mediaObjectInstanceUID,  "
                             "%%p=protocol,  "
                             "%%r=instance number,  "
                             "%%s=series number,  "
                             "%%t=examDate,  "
                             "%%u=acquisition number,  "
                             "%%v=vendor,  "
                             "%%x=study ID,  "
                             "%%z=sequence name.  "
                             "default '%%i/%%x_%%t/%%s_%%d'")
    parser.add_argument("-a", "--anonymize", action="store_true",
                        help="Enable anonymization of DICOM files.")
    # provide anonimization custom values in a json file

    parser.add_argument("-c", "--custom_anon_config", default=None,
                         help="Path to the JSON file specifying anonymization rules.")
    args = parser.parse_args()

    # Load anonymization configuration if anonymization is enabled


    if args.anonymize:
        print("Anonymization enabled. Loading default anonymization configuration...")
        if args.custom_anon_config:
            print(f"Loading custom anonymization configuration from {args.custom_anon_config}...")
            with open(args.custom_anon_config, encoding="utf-8") as f:
                custom_anonymization_config = json.load(f)
            args.anonymize = overwrite_default_anon_config(DEFAULT_ANONYMIZATION_CONFIG, 
                                                           custom_anonymization_config)
        else:
            args.anonymize = DEFAULT_ANONYMIZATION_CONFIG
    else:
        args.anonymize = None
        
    organize_dicoms(args.input, args.output, args.report, args.folder_structure, args.anonymize)


if __name__ == "__main__":
    main()
