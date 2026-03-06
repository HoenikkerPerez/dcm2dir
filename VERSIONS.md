
### Version v1.2.0.20260306 - 06-March-2026
- Added `--rename-folder` mode to validate and rename series folders based on DICOM metadata.
- Added support for in-place folder renaming when `--rename-folder` is used without `-o/--output`.
- Added folder-level validation to skip directories containing multiple `SeriesInstanceUID` values.
- Added collision-safe destination naming during folder rename operations.

### Version v1.1.0.20250402 - 02-April-2025
- Migrate packaging from setup.py/cfg to pyproject.toml  (Thanks to [jakob1379](https://github.com/jakob1379) in [PR #2](https://github.com/HoenikkerPerez/dcm2dir/pull/2))

### Version v1.0.0.20250328 - 28-March-2025
- Stable release of the `dcm2dir` tool.
- Added anonymization feature with the `-a` or `--anonymize` flag.
- Uses a default anonymization configuration to handle sensitive DICOM tags.
- Supports custom anonymization configurations via a JSON file.
- Improved error handling and logging for anonymization process.

### Version v0.1.0.20250325 - 25-March-2025
- Initial release of the `dcm2dir` tool.