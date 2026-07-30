# After Effects Test Data Generation Scripts

Automated ExtendScript (.jsx) scripts that generate `.aep` project files for testing
the Deadline Cloud for After Effects submitter across AE 2024/2025/2026 on Mac and Windows.

## Usage

### Run all test data generators at once:

```bash
# Windows
AfterFX.exe -s "$.evalFile('C:/Users/jaikish/Projects/deadline-cloud-for-after-effects/test_data/run_all.jsx')"

# macOS
/Applications/Adobe\ After\ Effects\ 2025/aerender -s "$.evalFile('/path/to/test_data/run_all.jsx')"
```

### Run individual test scripts:

```bash
AfterFX.exe -s "$.evalFile('C:/path/to/test_data/generators/01_video_rendering.jsx')"
```

## Output

All generated `.aep` files are saved to `test_data/output/<test_name>/`.

## Test Matrix Coverage

| # | Script | Quip Test Case |
|---|--------|----------------|
| 01 | video_rendering.jsx | Video Rendering + Custom Font Solution |
| 02 | audio_rendering.jsx | Audio Rendering |
| 03 | image_chunking.jsx | Image Chunking (300 frames, JPEG seq) |
| 04 | special_characters.jsx | Naming / special characters |
| 05 | multi_frame_rendering.jsx | Multi-frame rendering settings |
| 06 | timeout_test.jsx | Timeout (very short comp) |
| 07 | multicomp.jsx | After Effects Multicomp |
| 08 | image_sequence_import.jsx | Image Sequence Import |
| 09 | missing_dependencies.jsx | Missing Dependencies Test |
| 10 | custom_fonts.jsx | Custom Font coverage (multiple font types) |

## Cross-version Testing

These scripts use only stable ExtendScript APIs and should run identically on:
- After Effects 2024 (v24.x)
- After Effects 2025 (v25.x)
- After Effects 2026 (v26.x)

on both macOS and Windows.
