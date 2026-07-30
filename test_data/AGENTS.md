# Test Data Generation - Approach & Context

## Goal

Automate the creation of After Effects project files (.aep) that serve as test data
for the Deadline Cloud for After Effects submitter. These projects cover the test matrix
from the SMF Test Coverage Quip doc and should be runnable across AE 2024/2025/2026 on
Mac and Windows.

## Current State

- 10 generator scripts exist covering the automatable test cases from the Quip matrix
- A shared `config.jsx` provides reusable helpers (createComp, addText, addSolid, etc.)
- Runner scripts (`run_all.jsx`, `run_single.jsx`, `run_cross_version.bat`) handle execution
- Generated .aep files go into `output/` (git-ignored)

## What's Automated vs Manual

**Fully automated (script generates ready-to-submit .aep):**
- 01: Video rendering (H.264 output)
- 03: Image chunking (300 frames, JPEG sequence)
- 04: Special characters (8 comps with various symbols)
- 05: Multi-frame rendering (3 MFR configs)
- 06: Timeout (long + short comp)
- 07: Multicomp (5 comps in render queue)
- 10: Custom fonts (system fonts auto-detected per OS)

**Partially automated (script creates structure, manual steps needed):**
- 02: Audio rendering - ExtendScript cannot generate audio; tester must import a .wav/.mp3
- 08: Image sequence import - two-step: render source sequence, then import into consumer comp
- 09: Missing dependencies - tester must add real images, then delete one to test the toggle

## Not Covered by Scripts (require env/install changes)

These test cases from the Quip doc are not automatable via ExtendScript:
- JSX bundler check (build tooling, not AE project)
- Unit tests (Python/hatch, not AE project)
- Submit Button + Dockable (UI interaction)
- Deadline CLI error handling (requires removing deadline from PATH)
- AE env variable (host config, not project data)
- Installer testing (installer binary, not AE project)
- Conda testing (farm/fleet setup)
- Incompatible version warning (requires specific AE version install)
- Comp-level sticky settings (UI interaction between comp selections)

## Next Steps

1. **Audio rendering**: explore auto-importing a .wav from a known `assets/` path if one exists
2. **Render automation**: build a companion script that submits each .aep via `deadline bundle gui-submit` headlessly (post-generation step)
3. **Validation scripts**: after renders complete, verify output files exist with expected frame counts
4. **CI integration**: wire into a pipeline that runs generation + submission + validation per AE version
5. **Cross-platform parity**: test the macOS runner (`run_all.sh`) and fix any path issues

## Architecture

```
test_data/
├── config.jsx           # Shared utilities, constants, helper functions
├── run_all.jsx          # Sequential runner (logs results to generation_log.txt)
├── run_single.jsx       # Run one generator by TEST_INDEX variable
├── run_all.bat/.sh      # OS-specific launchers (auto-detect AE install path)
├── run_cross_version.bat # Loop through AE 2024/2025/2026 installations
├── generators/          # One .jsx per test case, numbered for ordering
│   └── NN_name.jsx     # Each: closes project, creates fresh, builds comp, saves
└── output/              # Git-ignored; generated .aep + instruction files land here
```

Each generator follows a consistent pattern:
1. `#include "../config.jsx"` for shared utilities
2. Close any open project, create new
3. Build composition(s) with appropriate content
4. Add to render queue with correct output settings
5. Save project to `output/<test_name>/<test_name>.aep`
6. Write instruction files for any manual steps
