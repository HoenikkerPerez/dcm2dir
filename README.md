[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![example workflow](https://github.com/HoenikkerPerez/dcm2dir/actions/workflows/pylint_pytest.yml/badge.svg)

# dcm2dir
Dcm2dir recursively scans a given root folder for DICOM files, extracts relevant metadata, and organizes the files into a structured output folder.


## Description
This Python script recursively scans a given root folder for DICOM files, extracts relevant metadata, and organizes the files into a structured output folder. The folder structure is customizable using placeholders for different DICOM tags. Additionally, a CSV report is generated with details of all processed DICOM series. The tool also supports anonymizing DICOM files with a default anonymization configuration and allows providing custom anonymization actions.


## Features
- Recursively scans and organizes DICOM files.
- Supports customizable folder structures.
- Utilizes multi-threading for faster processing.
- Generates a CSV report listing all series metadata.
- Handles missing DICOM tags gracefully.
- **Anonymizes DICOM files** based on a default anonymization configuration.

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
dcm2dir -i <input_folder> -o <output_folder> [-r <csv_report>] [-f <folder_structure>] [-a]
```

### Arguments:
- `-i, --input` (required): Path to the root folder containing DICOM files.
- `-o, --output` (required): Path to the destination folder where organized files will be stored.
- `-r, --report` (optional): Path to save the generated CSV report.
- `-f, --folder-structure` (optional): Custom folder structure using placeholders. See "Folder Structure" section.
- `-a, --anonymize` (optional): Enable anonymization of DICOMs.
- `-c, --custom_anon_config ` (optional): Path to the JSON file specifying anonymization rules.

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

## Anonymization
The `-a` or `--anonymize` flag enables anonymization of DICOM files. When this flag is provided, the tool uses a default anonymization configuration to process the DICOM files. The configuration specifies how to handle sensitive DICOM tags, such as removing or replacing their values.

### Default Anonymization Configuration
The default anonymization configuration is embedded in the tool and includes rules for handling sensitive DICOM tags. For example:
- Replace patient names and IDs with anonymized values.
- Remove sensitive metadata such as institution names and addresses.
- Retain essential metadata such as study and series UIDs.

For a detailed list of anonymization actions for specific DICOM tags, see the [Anonymization Actions Table](#anonymization-actions-table).

### Custom Anonymization Configuration
Providing a custom anonymization configuration ("-c <custom_anon_file.json>") allows you to specify how to handle sensitive DICOM tags. The configuration is a JSON file that maps DICOM tags to anonymization actions. 
For example:
```json
{
    "(0010,0010)": "C:ANONYMOUS^ANONYMOUS",
    "(0010,0020)": "C:ANONYMOUS_ID",
    "(0008,0020)": "K",
    "(0008,0021)": "K",
    "(0008,0022)": "K",
    "(0008,0023)": "Z",
    "(0008,0024)": "X",
    "(0008,0025)": "X"
}
```
**Legend for Actions**:
- **U**: Keep the tag but ensure it is unique.
- **X**: Remove the tag entirely.
- **Z**: Replace the tag value with anonymized data.
- **D**: Clean the tag value (e.g., remove sensitive information but keep the tag).
- **C:VALUE**: Replace the tag value with a custom value.

### Example Usage with DEFAULT anonymization:
```sh
dcm2dir -i ./dicoms -o ./organized -r report.csv -f "%i/%x_%t/%s_%d" -a
```
### Example Usage with CUSTOM anonymization:
```sh
dcm2dir -i ./dicoms -o ./organized -r report.csv -f "%i/%x_%t/%s_%d" -a -c custom_anonymization_file.json
```

This command will anonymize the DICOM files and organize them into the specified folder structure.

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
- The script uses multi-threading for better performance.
- Anonymization ensures sensitive patient data is removed or replaced.

## License
This project is open-source and available under the MIT License.

## Anonymization Actions Table 

The following table lists the anonymization actions for specific DICOM tags:

| **Tag**         | **Description**                     | **Action**       |
|------------------|-------------------------------------|------------------|
|	`(0002-0003)`	|	MediaStorageSOPInstanceUID	|	U	|
|	`(0008-0014)`	|	InstanceCreatorUID	|	X	|
|	`(0008-0015)`	|	InstanceCoercionDateTime	|	X	|
|	`(0008-0018)`	|	SOPInstanceUID	|	U	|
|	`(0008-0020)`	|	StudyDate	|	K	|
|	`(0008-0021)`	|	SeriesDate	|	K	|
|	`(0008-0022)`	|	AcquisitionDate	|	K	|
|	`(0008-0023)`	|	ContentDate	|	Z	|
|	`(0008-0024)`	|	OverlayDate	|	X	|
|	`(0008-0025)`	|	CurveDate	|	X	|
|	`(0008-0050)`	|	AccessionNumber	|	Z	|
|	`(0008-0054)`	|	RetrieveAETitle	|	X	|
|	`(0008-0058)`	|	FailedSOPInstanceUIDList	|	U	|
|	`(0008-0080)`	|	InstitutionName	|	Z	|
|	`(0008-0081)`	|	InstitutionAddress	|	X	|
|	`(0008-0090)`	|	ReferringPhysicianName	|	Z	|
|	`(0008-0092)`	|	ReferringPhysicianAddress	|	X	|
|	`(0008-0094)`	|	ReferringPhysicianTelephoneNumbers	|	X	|
|	`(0008-0096)`	|	ReferringPhysicianIdentificationSequence	|	X	|
|	`(0008-0201)`	|	TimezoneOffsetFromUTC	|	X	|
|	`(0008-1032)`	|	ProcedureCodeSequence	|	X	|
|	`(0008-1040)`	|	InstitutionalDepartmentName	|	X	|
|	`(0008-1048)`	|	PhysiciansOfRecord	|	X	|
|	`(0008-1049)`	|	PhysiciansOfRecordIdentificationSequence	|	X	|
|	`(0008-1050)`	|	PerformingPhysicianName	|	X	|
|	`(0008-1052)`	|	PerformingPhysicianIdentificationSequence	|	X	|
|	`(0008-1060)`	|	NameOfPhysiciansReadingStudy	|	X	|
|	`(0008-1062)`	|	PhysiciansReadingStudyIdentificationSequence	|	X	|
|	`(0008-1070)`	|	OperatorsName	|	D	|
|	`(0008-1072)`	|	OperatorIdentificationSequence	|	D	|
|	`(0008-1080)`	|	AdmittingDiagnosesDescription	|	X	|
|	`(0008-1084)`	|	AdmittingDiagnosesCodeSequence	|	X	|
|	`(0008-1090)`	|	ManufacturerModelName	|	X	|
|	`(0008-1110)`	|	ReferencedStudySequence	|	X	|
|	`(0008-1120)`	|	ReferencedPatientSequence	|	X	|
|	`(0008-1140)`	|	ReferencedImageSequence	|	X	|
|	`(0008-1155)`	|	ReferencedSOPInstanceUID	|	U	|
|	`(0008-1195)`	|	TransactionUID	|	U	|
|	`(0008-2111)`	|	DerivationDescription	|	X	|
|	`(0008-3010)`	|	IrradiationEventUID	|	U	|
|	`(0008-4000)`	|	IdentifyingComments	|	X	|
|	`(0010-0010)`	|	PatientName	|	C:ANONYMOUS^ANONYMOUS	|
|	`(0010-0020)`	|	PatientID	|	C:ANONYMOUS_ID	|
|	`(0010-0021)`	|	IssuerOfPatientID	|	X	|
|	`(0010-0030)`	|	PatientBirthDate	|	Z	|
|	`(0010-0032)`	|	PatientBirthTime	|	X	|
|	`(0010-0050)`	|	PatientInsurancePlanCodeSequence	|	X	|
|	`(0010-0101)`	|	PatientPrimaryLanguageCodeSequence	|	X	|
|	`(0010-0102)`	|	PatientPrimaryLanguageModifierCodeSequence	|	X	|
|	`(0010-1000)`	|	OtherPatientIDs	|	X	|
|	`(0010-1001)`	|	OtherPatientNames	|	X	|
|	`(0010-1002)`	|	OtherPatientIDsSequence	|	X	|
|	`(0010-1005)`	|	PatientBirthName	|	X	|
|	`(0010-1020)`	|	PatientSize	|	X	|
|	`(0010-1030)`	|	PatientWeight	|	X	|
|	`(0010-1040)`	|	PatientAddress	|	X	|
|	`(0010-1050)`	|	InsurancePlanIdentification	|	X	|
|	`(0010-1060)`	|	PatientMotherBirthName	|	X	|
|	`(0010-1080)`	|	MilitaryRank	|	X	|
|	`(0010-1081)`	|	BranchOfService	|	X	|
|	`(0010-1090)`	|	MedicalRecordLocator	|	X	|
|	`(0010-2000)`	|	MedicalAlerts	|	X	|
|	`(0010-2110)`	|	Allergies	|	X	|
|	`(0010-2150)`	|	CountryOfResidence	|	X	|
|	`(0010-2152)`	|	RegionOfResidence	|	X	|
|	`(0010-2154)`	|	PatientTelephoneNumbers	|	X	|
|	`(0010-2160)`	|	EthnicGroup	|	X	|
|	`(0010-2180)`	|	Occupation	|	X	|
|	`(0010-21A0)`	|	SmokingStatus	|	X	|
|	`(0010-21B0)`	|	AdditionalPatientHistory	|	X	|
|	`(0010-21C0)`	|	PregnancyStatus	|	X	|
|	`(0010-21D0)`	|	LastMenstrualDate	|	X	|
|	`(0010-21F0)`	|	PatientReligiousPreference	|	X	|
|	`(0010-2203)`	|	PatientSexNeutered	|	X	|
|	`(0010-2297)`	|	ResponsiblePerson	|	X	|
|	`(0010-2299)`	|	ResponsibleOrganization	|	X	|
|	`(0010-4000)`	|	PatientComments	|	X	|
|	`(0012-0010)`	|	ClinicalTrialSponsorName	|	D	|
|	`(0012-0020)`	|	ClinicalTrialProtocolID	|	D	|
|	`(0012-0021)`	|	ClinicalTrialProtocolName	|	Z	|
|	`(0012-0030)`	|	ClinicalTrialSiteID	|	Z	|
|	`(0012-0031)`	|	ClinicalTrialSiteName	|	Z	|
|	`(0012-0040)`	|	ClinicalTrialSubjectID	|	D	|
|	`(0012-0042)`	|	ClinicalTrialSubjectReadingID	|	D	|
|	`(0012-0050)`	|	ClinicalTrialTimePointID	|	Z	|
|	`(0012-0051)`	|	ClinicalTrialTimePointDescription	|	X	|
|	`(0012-0060)`	|	ClinicalTrialCoordinatingCenterName	|	Z	|
|	`(0018-1002)`	|	DeviceUID	|	U	|
|	`(0018-1004)`	|	PlateID	|	X	|
|	`(0018-1005)`	|	GeneratorID	|	X	|
|	`(0018-1007)`	|	CassetteID	|	X	|
|	`(0018-1008)`	|	GantryID	|	X	|
|	`(0018-1012)`	|	DateOfSecondaryCapture	|	X	|
|	`(0018-1014)`	|	TimeOfSecondaryCapture	|	X	|
|	`(0018-1020)`	|	SoftwareVersions	|	X	|
|	`(0018-1042)`	|	ContrastBolusStartTime	|	X	|
|	`(0018-1043)`	|	ContrastBolusStopTime	|	X	|
|	`(0018-1072)`	|	RadiopharmaceuticalStartTime	|	X	|
|	`(0018-1073)`	|	RadiopharmaceuticalStopTime	|	X	|
|	`(0018-1200)`	|	DateOfLastCalibration	|	X	|
|	`(0018-1201)`	|	TimeOfLastCalibration	|	X	|
|	`(0018-1400)`	|	AcquisitionDeviceProcessingDescription	|	D	|
|	`(0018-4000)`	|	AcquisitionComments	|	X	|
|	`(0018-700A)`	|	DetectorID	|	X	|
|	`(0018-700C)`	|	DateOfLastDetectorCalibration	|	X	|
|	`(0018-700E)`	|	TimeOfLastDetectorCalibration	|	X	|
|	`(0018-9424)`	|	AcquisitionProtocolDescription	|	X	|
|	`(0018-A003)`	|	ContributionDescription	|	X	|
|	`(0020-000D)`	|	StudyInstanceUID	|	U	|
|	`(0020-000E)`	|	SeriesInstanceUID	|	U	|
|	`(0020-0010)`	|	StudyID	|	C:CUSTOM_EXAM_ID	|
|	`(0020-0052)`	|	FrameOfReferenceUID	|	U	|
|	`(0020-3401)`	|	ModifyingDeviceID	|	X	|
|	`(0020-3404)`	|	ModifyingDeviceManufacturer	|	X	|
|	`(0020-3406)`	|	ModifiedImageDescription	|	X	|
|	`(0020-4000)`	|	ImageComments	|	X	|
|	`(0020-9158)`	|	FrameComments	|	X	|
|	`(0020-9161)`	|	ConcatenationUID	|	U	|
|	`(0020-9164)`	|	DimensionOrganizationUID	|	U	|
|	`(0028-1199)`	|	PaletteColorLookupTableUID	|	U	|
|	`(0028-1214)`	|	LargePaletteColorLookupTableUID	|	U	|
|	`(0032-0012)`	|	StudyIDIssuer	|	X	|
|	`(0032-0032)`	|	StudyVerifiedDate	|	X	|
|	`(0032-0033)`	|	StudyVerifiedTime	|	X	|
|	`(0032-0034)`	|	StudyReadDate	|	X	|
|	`(0032-0035)`	|	StudyReadTime	|	X	|
|	`(0032-1000)`	|	ScheduledStudyStartDate	|	X	|
|	`(0032-1001)`	|	ScheduledStudyStartTime	|	X	|
|	`(0032-1010)`	|	ScheduledStudyStopDate	|	X	|
|	`(0032-1011)`	|	ScheduledStudyStopTime	|	X	|
|	`(0032-1020)`	|	ScheduledStudyLocation	|	X	|
|	`(0032-1021)`	|	ScheduledStudyLocationAETitle	|	X	|
|	`(0032-1030)`	|	ReasonForStudy	|	X	|
|	`(0032-1032)`	|	RequestingPhysician	|	X	|
|	`(0032-1033)`	|	RequestingService	|	X	|
|	`(0032-1040)`	|	StudyArrivalDate	|	X	|
|	`(0032-1041)`	|	StudyArrivalTime	|	X	|
|	`(0032-1050)`	|	StudyCompletionDate	|	X	|
|	`(0032-1051)`	|	StudyCompletionTime	|	X	|
|	`(0032-1060)`	|	RequestedProcedureDescription	|	X	|
|	`(0032-1070)`	|	RequestedContrastAgent	|	X	|
|	`(0032-4000)`	|	StudyComments	|	X	|
|	`(0038-0004)`	|	ReferencedPatientAliasSequence	|	X	|
|	`(0038-0010)`	|	AdmissionID	|	X	|
|	`(0038-0011)`	|	IssuerOfAdmissionID	|	X	|
|	`(0038-001A)`	|	ScheduledAdmissionDate	|	X	|
|	`(0038-001B)`	|	ScheduledAdmissionTime	|	X	|
|	`(0038-001C)`	|	ScheduledDischargeDate	|	X	|
|	`(0038-001D)`	|	ScheduledDischargeTime	|	X	|
|	`(0038-001E)`	|	ScheduledPatientInstitutionResidence	|	X	|
|	`(0038-0020)`	|	AdmittingDate	|	X	|
|	`(0038-0021)`	|	AdmittingTime	|	X	|
|	`(0038-0030)`	|	DischargeDate	|	X	|
|	`(0038-0032)`	|	DischargeTime	|	X	|
|	`(0038-0040)`	|	DischargeDiagnosisDescription	|	X	|
|	`(0038-0050)`	|	SpecialNeeds	|	X	|
|	`(0038-0060)`	|	ServiceEpisodeID	|	X	|
|	`(0038-0061)`	|	IssuerOfServiceEpisodeID	|	X	|
|	`(0038-0062)`	|	ServiceEpisodeDescription	|	X	|
|	`(0038-0300)`	|	CurrentPatientLocation	|	X	|
|	`(0038-0400)`	|	PatientInstitutionResidence	|	X	|
|	`(0038-0500)`	|	PatientState	|	X	|
|	`(0038-4000)`	|	VisitComments	|	X	|
|	`(0040-0001)`	|	ScheduledStationAETitle	|	X	|
|	`(0040-0002)`	|	ScheduledProcedureStepStartDate	|	X	|
|	`(0040-0003)`	|	ScheduledProcedureStepStartTime	|	X	|
|	`(0040-0004)`	|	ScheduledProcedureStepEndDate	|	X	|
|	`(0040-0005)`	|	ScheduledProcedureStepEndTime	|	X	|
|	`(0040-0006)`	|	ScheduledPerformingPhysicianName	|	X	|
|	`(0040-0007)`	|	ScheduledProcedureStepDescription	|	X	|
|	`(0040-0009)`	|	ScheduledProcedureStepID	|	X	|
|	`(0040-000B)`	|	ScheduledPerformingPhysicianIdentificationSequence	|	X	|
|	`(0040-0010)`	|	ScheduledStationName	|	X	|
|	`(0040-0011)`	|	ScheduledProcedureStepLocation	|	X	|
|	`(0040-0012)`	|	PreMedication	|	X	|
|	`(0040-0241)`	|	PerformedStationAETitle	|	X	|
|	`(0040-0242)`	|	PerformedStationName	|	X	|
|	`(0040-0243)`	|	PerformedLocation	|	X	|
|	`(0040-0244)`	|	PerformedProcedureStepStartDate	|	X	|
|	`(0040-0245)`	|	PerformedProcedureStepStartTime	|	X	|
|	`(0040-0250)`	|	PerformedProcedureStepEndDate	|	X	|
|	`(0040-0251)`	|	PerformedProcedureStepEndTime	|	X	|
|	`(0040-0253)`	|	PerformedProcedureStepID	|	X	|
|	`(0040-0254)`	|	PerformedProcedureStepDescription	|	X	|
|	`(0040-0275)`	|	RequestAttributesSequence	|	X	|
|	`(0040-0280)`	|	CommentsOnThePerformedProcedureStep	|	X	|
|	`(0040-0281)`	|	PerformedProcedureStepDiscontinuationReasonCodeSequence	|	X	|
|	`(0040-0310)`	|	CommentsOnRadiationDose	|	X	|
|	`(0040-050A)`	|	SpecimenAccessionNumber	|	X	|
|	`(0040-0555)`	|	AcquisitionContextSequence	|	X	|
|	`(0040-06FA)`	|	SlideIdentifier	|	X	|
|	`(0040-1001)`	|	RequestedProcedureID	|	X	|
|	`(0040-1002)`	|	ReasonForTheRequestedProcedure	|	X	|
|	`(0040-1004)`	|	PatientTransportArrangements	|	X	|
|	`(0040-1005)`	|	RequestedProcedureLocation	|	X	|
|	`(0040-1010)`	|	NamesOfIntendedRecipientsOfResults	|	X	|
|	`(0040-1011)`	|	IntendedRecipientsOfResultsIdentificationSequence	|	X	|
|	`(0040-1102)`	|	PersonAddress	|	X	|
|	`(0040-1103)`	|	PersonTelephoneNumbers	|	X	|
|	`(0040-1400)`	|	RequestedProcedureComments	|	X	|
|	`(0040-2001)`	|	ReasonForTheImagingServiceRequest	|	X	|
|	`(0040-2004)`	|	IssueDateOfImagingServiceRequest	|	X	|
|	`(0040-2005)`	|	IssueTimeOfImagingServiceRequest	|	X	|
|	`(0040-2008)`	|	OrderEnteredBy	|	X	|
|	`(0040-2009)`	|	OrderEntererLocation	|	X	|
|	`(0040-2010)`	|	OrderCallbackPhoneNumber	|	X	|
|	`(0040-2016)`	|	PlacerOrderNumberImagingServiceRequest	|	Z	|
|	`(0040-2017)`	|	FillerOrderNumberImagingServiceRequest	|	Z	|
|	`(0040-2400)`	|	ImagingServiceRequestComments	|	X	|
|	`(0040-3001)`	|	ConfidentialityConstraintOnPatientDataDescription	|	X	|
|	`(0040-4023)`	|	ReferencedGeneralPurposeScheduledProcedureStepTransactionUID	|	U	|
|	`(0040-4025)`	|	ScheduledStationNameCodeSequence	|	X	|
|	`(0040-4027)`	|	ScheduledStationGeographicLocationCodeSequence	|	X	|
|	`(0040-4030)`	|	PerformedStationGeographicLocationCodeSequence	|	X	|
|	`(0040-4034)`	|	ScheduledHumanPerformersSequence	|	X	|
|	`(0040-4035)`	|	ActualHumanPerformersSequence	|	X	|
|	`(0040-4036)`	|	HumanPerformerOrganization	|	X	|
|	`(0040-4037)`	|	HumanPerformerName	|	X	|
|	`(0040-A073)`	|	VerifyingObserverSequence	|	X	|
|	`(0040-A075)`	|	VerifyingObserverName	|	D	|
|	`(0040-A078)`	|	AuthorObserverSequence	|	X	|
|	`(0040-A07A)`	|	ParticipantSequence	|	X	|
|	`(0040-A07C)`	|	CustodialOrganizationSequence	|	X	|
|	`(0040-A088)`	|	VerifyingObserverIdentificationCodeSequence	|	Z	|
|	`(0040-A122)`	|	Time	|	X	|
|	`(0040-A123)`	|	PersonName	|	D	|
|	`(0040-A124)`	|	UID	|	U	|
|	`(0040-A730)`	|	ContentSequence	|	X	|
|	`(0040-DB06)`	|	TemplateVersion	|	X	|
|	`(0040-DB07)`	|	TemplateLocalVersion	|	X	|
|	`(0040-DB0C)`	|	TemplateExtensionOrganizationUID	|	U	|
|	`(0040-DB0D)`	|	TemplateExtensionCreatorUID	|	U	|
|	`(0060-3000)`	|	HistogramSequence	|	X	|
|	`(0070-031A)`	|	FiducialUID	|	U	|
|	`(0088-0140)`	|	StorageMediaFileSetUID	|	U	|
|	`(0088-0200)`	|	IconImageSequence	|	X	|
|	`(0088-0906)`	|	TopicSubject	|	X	|
|	`(0088-0910)`	|	TopicAuthor	|	X	|
|	`(0088-0912)`	|	TopicKeywords	|	X	|
|	`(0400-0100)`	|	DigitalSignatureUID	|	U	|
|	`(2030-0010)`	|	AnnotationPosition	|	Z	|
|	`(2030-0020)`	|	TextString	|	X	|
|	`(2040-0010)`	|	ReferencedOverlayPlaneSequence	|	Z	|
|	`(2040-0011)`	|	ReferencedOverlayPlaneGroups	|	Z	|
|	`(2040-0020)`	|	OverlayPixelDataSequence	|	Z	|
|	`(2040-0060)`	|	OverlayMagnificationType	|	Z	|
|	`(2040-0070)`	|	OverlaySmoothingType	|	Z	|
|	`(2040-0072)`	|	OverlayOrImageMagnification	|	Z	|
|	`(2040-0074)`	|	MagnifyToNumberOfColumns	|	Z	|
|	`(2040-0080)`	|	OverlayForegroundDensity	|	Z	|
|	`(2040-0082)`	|	OverlayBackgroundDensity	|	Z	|
|	`(2040-0090)`	|	OverlayMode	|	Z	|
|	`(2040-0100)`	|	ThresholdDensity	|	Z	|
|	`(2040-0500)`	|	ReferencedImageBoxSequenceRetired	|	Z	|
|	`(2100-0020)`	|	ExecutionStatus	|	Z	|
|	`(2100-0030)`	|	ExecutionStatusInfo	|	Z	|
|	`(2100-0040)`	|	CreationDate	|	X	|
|	`(2100-0050)`	|	CreationTime	|	X	|
|	`(2100-0070)`	|	Originator	|	X	|
|	`(2110-0010)`	|	PrinterStatus	|	Z	|
|	`(2110-0020)`	|	PrinterStatusInfo	|	Z	|
|	`(2110-0030)`	|	PrinterName	|	Z	|
|	`(2110-0099)`	|	PrintQueueID	|	Z	|
|	`(3006-0024)`	|	ReferencedFrameOfReferenceUID	|	U	|
|	`(3006-00C2)`	|	RelatedFrameOfReferenceUID	|	U	|
|	`(300A-0013)`	|	DoseReferenceUID	|	U	|
|	`(4000-0010)`	|	Arbitrary	|	X	|
|	`(4000-4000)`	|	TextComments	|	X	|
|	`(4008-0042)`	|	ResultsIDIssuer	|	X	|
|	`(4008-0102)`	|	InterpretationRecorder	|	X	|
|	`(4008-010A)`	|	InterpretationTranscriber	|	X	|
|	`(4008-010B)`	|	InterpretationText	|	X	|
|	`(4008-010C)`	|	InterpretationAuthor	|	X	|
|	`(4008-0111)`	|	InterpretationApproverSequence	|	X	|
|	`(4008-0114)`	|	PhysicianApprovingInterpretation	|	X	|
|	`(4008-0115)`	|	InterpretationDiagnosisDescription	|	X	|
|	`(4008-0118)`	|	ResultsDistributionListSequence	|	X	|
|	`(4008-0119)`	|	DistributionName	|	X	|
|	`(4008-011A)`	|	DistributionAddress	|	X	|
|	`(4008-0202)`	|	InterpretationIDIssuer	|	X	|
|	`(4008-0300)`	|	Impressions	|	X	|
|	`(4008-4000)`	|	ResultsComments	|	X	|


**Legend for Actions**:
- **U**: Keep the tag but ensure it is unique.
- **X**: Remove the tag entirely.
- **Z**: Replace the tag value with anonymized data.
- **D**: Clean the tag value (e.g., remove sensitive information but keep the tag).
- **C:VALUE**: Replace the tag value with a custom value.
