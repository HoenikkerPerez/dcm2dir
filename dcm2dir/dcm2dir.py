import os
import shutil
import pydicom
import csv
import re
import argparse
import concurrent.futures
from tqdm import tqdm


def sanitize_name(name, placeholder="na"):
    """Sanitize names by replacing non-alphanumeric characters with underscores."""
    if not name:
        return placeholder
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


def convert_folder_structure(string):
    """Converts the placeholder syntax to Python's format string."""
    return re.sub(r"(%[a-zA-Z])", r"{\1}", string)


def process_dicom(file_path, output_folder, folder_structure):
    """Reads a DICOM file, extracts relevant metadata, and copies it to the structured output folder."""
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)

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
        shutil.copy2(file_path, dest_folder)

        return [metadata["%i"], metadata["%t"], metadata["%x"], metadata["%s"], metadata["%d"]]
    except Exception as e:
        print(f"Skipping {file_path}: {e}")
        return None


def organize_dicoms(root_folder, output_folder, report_path, folder_structure):
    """Recursively scans DICOM files, processes them in parallel, and generates a CSV report."""
    
    # Convert placeholder syntax to Python's format string
    folder_structure = convert_folder_structure(folder_structure)

    dicom_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            dicom_files.append(os.path.join(dirpath, file))

    dicom_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            tqdm(executor.map(lambda f: process_dicom(f, output_folder, folder_structure), dicom_files),
                 total=len(dicom_files),
                 desc="Processing DICOMs"))

    dicom_data = [r for r in results if r]

    # Write CSV report if provided
    if report_path:
        with open(report_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["SubjectID", "ExamDate", "ExamID", "SeriesID", "SeriesDescription"])
            for row in sorted(dicom_data, key=lambda x: (x[0], x[1])):
                writer.writerow(row)
        print(f"Processing completed. CSV report saved at {report_path}")
    else:
        print("Processing completed. No CSV report generated.")


def main():
    parser = argparse.ArgumentParser(description="Organize DICOM files recursively and generate a CSV report.")
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
    args = parser.parse_args()

    organize_dicoms(args.input, args.output, args.report, args.folder_structure)


if __name__ == "__main__":
    main()