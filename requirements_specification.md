# Requirements Specification

## Project title
Multimodal Attendance & Engagement Agent

## Problem statement
Manual attendance consumes class time, and instructors may not have an easy way to review session-level participation patterns. This prototype explores video and audio signals to create attendance-support logs and simple session summaries.

## Objectives
- Sample a video and detect visible faces across time.
- Estimate sustained visible presence rather than relying on a single frame.
- Extract basic audio activity features.
- Combine available signals into a transparent activity indicator.
- Offer non-binding, context-aware teaching suggestions.
- Export analysis results as CSV files.

## Functional requirements
- FR1: Accept a supported classroom video file.
- FR2: Sample frames and detect faces.
- FR3: Generate timestamped visibility logs.
- FR4: Accept an audio file and extract RMS energy and zero-crossing rate.
- FR5: Calculate an illustrative session activity indicator when signals are available.
- FR6: Show teaching suggestions based on thresholds.
- FR7: Allow CSV download of generated results.

## Non-functional requirements
- NFR1: Provide a simple browser-based interface.
- NFR2: Display clear errors for unsupported or unreadable files.
- NFR3: Keep the heuristic transparent and explain its limitations.
- NFR4: Avoid identifying students by name in this prototype.
- NFR5: Require human review before using results for official attendance or decisions.

## Tools
Python, Streamlit, OpenCV, NumPy, Pandas, Librosa, SoundFile.

## Acceptance criteria
- The application launches with `streamlit run app.py`.
- A supported video produces a timestamped CSV.
- A supported audio file produces signal features.
- Session analytics displays a summary and suggestions.
- CSV downloads are available for generated outputs.
