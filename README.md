# Multimodal Attendance & Engagement Agent

A student prototype for the SmartBridge project. It demonstrates:
1. Video frame sampling and face detection for visible-presence estimation.
2. Audio feature extraction using RMS energy and zero-crossing rate.
3. A transparent, illustrative activity indicator and instructor suggestions.
4. CSV exports for video logs, audio features, and session summaries.

## Setup (Windows / macOS / Linux)

Use Python 3.10 or 3.11.

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and launch:
```bash
pip install -r requirements.txt
streamlit run app.py
```

The terminal will show a local address, usually `http://localhost:8501`. Open it in a browser.

## How to demo
1. Open the Video attendance tab and upload a short classroom video recorded with consent.
2. Click **Analyze video** and download the CSV.
3. Open Audio signals and upload a WAV/MP3 recording if available.
4. Click **Analyze audio**.
5. Open Session analytics and download the session summary.

## Project structure

```text
multimodal_attendance_engagement/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── sample_session.csv
```

## Important limitations
- This is a prototype, not a production attendance system.
- It detects faces but does not identify students or verify identity.
- Camera angle, lighting, occlusion, and group seating can affect face detection.
- Audio energy is not equivalent to speech recognition or attention.
- The activity indicator is an illustrative heuristic, not a validated psychological metric.
- Human review, consent, and institutional privacy requirements are essential.
