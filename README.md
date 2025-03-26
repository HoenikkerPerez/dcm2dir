# dcm2dir
dcm2dir recursively scans a given root folder for DICOM files, extracts relevant metadata, and organizes the files into a structured output folder.

## Description
dcm2dir tool recursively scans a given root folder for DICOM files, extracts relevant metadata, and organizes the files into a structured output folder. The folder structure is customizable using placeholders for different DICOM tags. Additionally, a CSV report is generated with details of all processed DICOM series.

## Features
- Recursively scans and organizes DICOM files.
- Supports customizable folder structures.
- Utilizes multi-threading for faster processing.
- Generates a CSV report listing all series metadata.
- Handles missing DICOM tags gracefully.

## Installation

### From PyPI
Install the package directly from PyPI using `pip`:
```sh
pip install dcm2dir
```

### From Source Code
Clone the repository and install the dependencies manually:
```sh
git clone https://github.com/HoenikkerPerez/dcm2dir.git
cd dcm2dir
pip install -e .
```

## Usage
Run dcm2dir with the following command-line arguments:

```sh
dcm2dir -i <input_folder> -o <output_folder> [-r <csv_report>] [-f <folder_structure>]
```

### Arguments:
- `-i, --input` (required): Path to the root folder containing DICOM files.
- `-o, --output` (required): Path to the destination folder where organized files will be stored.
- `-r, --report` (optional): Path to save the generated CSV report.
- `-f, --folder-structure` (optional): Custom folder structure using placeholders. See "Folder Structure" section.

### Example Usage:
```sh
dcm2dir -i ./dicoms -o ./organized -r report.csv -f "%i/%x_%t/%s_%d"
```

### Folder Structure:
The folder structure can be customized using placeholders for different DICOM tags. The following placeholders are available:
- `%a`: Antenna (coil) name
- `%b`: Basename
- `%c`: Comments
- `%d`: Description
- `%e`: Echo number
- `%f`: Folder name
- `%g`: Accession number
- `%i`: ID of patient
- `%j`: SeriesInstanceUID
- `%k`: StudyInstanceUID
- `%m`: Manufacturer
- `%n`: Name of patient
- `%o`: MediaObjectInstanceUID
- `%p`: Protocol
- `%r`: Instance number
- `%s`: Series number
- `%t`: Exam date
- `%u`: Acquisition number
- `%v`: Vendor
- `%x`: Study ID
- `%z`: Sequence name

If `-f` is not provided, the default structure is used:
```
"-f %i/%x_%t/%s_%d"
```
which corresponds to:
```
/path/to/output/
├── PatientID1/
│   ├── StudyID1_20250101/
│   │   ├── SeriesNumber1_SeriesDescription/
│   │   │   └── file1.dcm
│   │   │   └── file2.dcm
├── PatientID2/
│   ├── StudyID2_20250102/
│   │   ├── SeriesNumber2_SeriesDescription/
│   │   │   └── file3.dcm
```

## Output

The tool organizes DICOM files into the specified output folder following the given structure. A CSV report is saved, containing the following columns:
- SubjectID
- ExamDate
- ExamID
- SeriesID
- SeriesDescription

## Notes
- Non-alphanumeric characters in metadata are replaced with underscores.
- If a DICOM tag is missing, a default placeholder `na` is used.
- The tool uses multi-threading for better performance.

## License
This project is open-source and available under the MIT License.
