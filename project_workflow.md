# Project Workflow

1. **Requirement analysis:** identify input media, output logs, privacy constraints, and success criteria.
2. **Environment setup:** install Python and required packages.
3. **Video module:** sample frames, convert to grayscale, detect faces, and record timestamps and visible presence.
4. **Audio module:** load audio and compute RMS energy and zero-crossing rate.
5. **Multimodal integration:** combine only the available signal indicators using a documented heuristic.
6. **Recommendation module:** generate suggestions from low-presence, low-movement, or low-audio-activity indicators.
7. **Reporting:** display tables/charts and export CSV files.
8. **Testing:** test valid files, invalid files, missing signals, and empty inputs.
9. **Documentation:** explain the design, dependencies, limitations, and privacy safeguards.
10. **Demonstration:** show the workflow and verify downloaded CSVs.

## Data flow
Video/audio input → preprocessing → feature extraction → signal summary → heuristic fusion → teaching suggestions → CSV export.

## Ethical safeguards
Obtain consent for recordings, minimize retention of media, avoid identity claims, and require instructor review. Engagement indicators must not be treated as definitive judgments about an individual student.
