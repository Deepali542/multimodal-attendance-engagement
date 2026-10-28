import streamlit as st
import pandas as pd
import numpy as np
import cv2
import tempfile
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Multimodal Attendance & Engagement Agent", page_icon="🎓", layout="wide")
st.title("🎓 Multimodal Attendance & Engagement Agent")
st.caption("Prototype for classroom attendance, session engagement analysis, and AI-assisted teaching suggestions.")

with st.sidebar:
    st.header("Session details")
    session_name = st.text_input("Session / class name", "Demo Classroom Session")
    minimum_presence = st.slider("Minimum presence threshold (%)", 10, 90, 60, 5)
    st.info("Privacy note: use consented classroom recordings only. This prototype estimates visible presence; it does not identify students by name.")

tab1, tab2, tab3 = st.tabs(["📹 Video attendance", "🔊 Audio signals", "📊 Session analytics"])

if "video_results" not in st.session_state:
    st.session_state.video_results = None
if "audio_results" not in st.session_state:
    st.session_state.audio_results = None

def analyze_video(uploaded, sample_every=15, max_frames=600):
    suffix = Path(uploaded.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        video_path = tmp.name
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        try: os.remove(video_path)
        except Exception: pass
        raise ValueError("Could not open this video. Try MP4 or MOV.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 25
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if frame_count else 0
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    rows = []
    idx = 0
    processed = 0
    previous_gray = None
    while processed < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % sample_every == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            movement = 0.0
            if previous_gray is not None:
                resized = cv2.resize(gray, (160, 90))
                movement = float(cv2.absdiff(resized, previous_gray).mean() / 255.0)
                previous_gray = resized
            else:
                previous_gray = cv2.resize(gray, (160, 90))
            rows.append({
                "timestamp_seconds": round(idx / fps, 2),
                "faces_detected": int(len(faces)),
                "visible_presence": int(len(faces) > 0),
                "movement_proxy": round(movement, 4)
            })
            processed += 1
        idx += 1
    cap.release()
    try: os.remove(video_path)
    except Exception: pass
    if not rows:
        raise ValueError("No readable frames found in the uploaded video.")
    df = pd.DataFrame(rows)
    return df, duration, fps

def analyze_audio(uploaded):
    try:
        import librosa
    except Exception as e:
        raise RuntimeError("Audio analysis library is not installed. Run: pip install -r requirements.txt") from e
    suffix = Path(uploaded.name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        audio_path = tmp.name
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = len(y) / sr if sr else 0
        hop = 512
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=2048, hop_length=hop)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
        threshold = max(float(np.percentile(rms, 35)), 0.008)
        rows = []
        for t, r, z in zip(times, rms, zcr):
            rows.append({
                "timestamp_seconds": round(float(t), 2),
                "rms_energy": round(float(r), 5),
                "zero_crossing_rate": round(float(z), 5),
                "audio_active": int(r > threshold)
            })
        return pd.DataFrame(rows), duration, sr
    finally:
        try: os.remove(audio_path)
        except Exception: pass

with tab1:
    st.subheader("Automated attendance from a video")
    st.write("Upload a consented classroom video. The prototype samples frames, detects visible faces, and estimates sustained presence.")
    video = st.file_uploader("Upload video (MP4/MOV/AVI)", type=["mp4", "mov", "avi", "m4v"], key="video")
    col_a, col_b = st.columns(2)
    with col_a:
        sample_every = st.selectbox("Analyze every Nth frame", [5, 10, 15, 30], index=2)
    with col_b:
        max_frames = st.selectbox("Maximum sampled frames", [120, 300, 600, 1000], index=2)
    if st.button("Analyze video", type="primary", disabled=video is None):
        with st.spinner("Analyzing sampled frames..."):
            try:
                vdf, duration, fps = analyze_video(video, sample_every, max_frames)
                st.session_state.video_results = vdf
                st.success(f"Analysis complete. Sampled {len(vdf)} frames. Approx. video duration: {duration:.1f} seconds.")
            except Exception as e:
                st.error(str(e))
    vdf = st.session_state.video_results
    if vdf is not None:
        total = len(vdf)
        presence_pct = 100 * vdf["visible_presence"].mean() if total else 0
        present = "Present (visible in sampled frames)" if presence_pct >= minimum_presence else "Needs review"
        c1, c2, c3 = st.columns(3)
        c1.metric("Sampled frames", total)
        c2.metric("Visible presence", f"{presence_pct:.1f}%")
        c3.metric("Attendance estimate", present)
        st.line_chart(vdf.set_index("timestamp_seconds")[["faces_detected"]])
        st.dataframe(vdf, use_container_width=True)
        st.download_button("Download video analysis CSV", vdf.to_csv(index=False).encode("utf-8"), "video_attendance_log.csv", "text/csv")

with tab2:
    st.subheader("Audio signal extraction")
    st.write("Upload an audio file to calculate signal energy and zero-crossing rate. These are signal activity indicators, not proof of attention or speech content.")
    audio = st.file_uploader("Upload audio (WAV/MP3/FLAC/OGG)", type=["wav", "mp3", "flac", "ogg"], key="audio")
    if st.button("Analyze audio", type="primary", disabled=audio is None):
        with st.spinner("Extracting audio features..."):
            try:
                adf, duration, sr = analyze_audio(audio)
                st.session_state.audio_results = adf
                st.success(f"Audio analysis complete. Duration: {duration:.1f}s; sample rate: {sr} Hz.")
            except Exception as e:
                st.error(str(e))
    adf = st.session_state.audio_results
    if adf is not None:
        active_pct = 100 * adf["audio_active"].mean() if len(adf) else 0
        c1, c2 = st.columns(2)
        c1.metric("Audio-active intervals", f"{active_pct:.1f}%")
        c2.metric("Intervals analyzed", len(adf))
        st.line_chart(adf.set_index("timestamp_seconds")[["rms_energy", "zero_crossing_rate"]])
        st.dataframe(adf.head(100), use_container_width=True)
        st.download_button("Download audio features CSV", adf.to_csv(index=False).encode("utf-8"), "audio_signal_features.csv", "text/csv")

with tab3:
    st.subheader("Session analytics and teaching suggestions")
    vdf = st.session_state.video_results
    adf = st.session_state.audio_results
    if vdf is None and adf is None:
        st.info("Analyze a video and/or audio file in the other tabs to generate session analytics.")
    else:
        visibility = float(vdf["visible_presence"].mean()) if vdf is not None and len(vdf) else None
        movement = float(vdf["movement_proxy"].mean()) if vdf is not None and len(vdf) else None
        audio_active = float(adf["audio_active"].mean()) if adf is not None and len(adf) else None
        # Transparent heuristic, not a validated psychological measure.
        components = []
        if visibility is not None: components.append(visibility * 100 * 0.5)
        if movement is not None: components.append(min(movement * 400, 100) * 0.25)
        if audio_active is not None: components.append(audio_active * 100 * 0.25)
        score = float(np.mean(components)) if components else 0
        st.metric("Prototype activity indicator", f"{score:.1f}/100")
        st.caption("This is an illustrative heuristic, not a validated measure of attention, learning, or student performance.")
        suggestions = []
        if visibility is not None and visibility < 0.6:
            suggestions.append("Review camera framing and attendance manually; few faces were detected in sampled frames.")
        if movement is not None and movement < 0.03:
            suggestions.append("Consider a short poll, question, or stretch break if this aligns with instructor observations.")
        if audio_active is not None and audio_active < 0.15:
            suggestions.append("If appropriate for the lesson, invite questions or use a brief discussion activity.")
        if not suggestions:
            suggestions.append("Maintain the current pace, and validate these signals against instructor observations and student feedback.")
        st.markdown("#### Suggested instructor actions")
        for item in suggestions:
            st.write("• " + item)
        st.markdown("#### Session summary")
        summary = pd.DataFrame([{
            "session_name": session_name,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "visible_presence_fraction": round(visibility, 3) if visibility is not None else None,
            "average_movement_proxy": round(movement, 4) if movement is not None else None,
            "audio_active_fraction": round(audio_active, 3) if audio_active is not None else None,
            "prototype_activity_indicator": round(score, 1),
            "suggestions": " | ".join(suggestions)
        }])
        st.dataframe(summary, use_container_width=True)
        st.download_button("Download session summary CSV", summary.to_csv(index=False).encode("utf-8"), "session_summary.csv", "text/csv")

st.divider()
st.caption("Prototype limitations: Haar-cascade face detection can miss faces and does not identify individuals. Presence estimates require manual verification. Audio energy does not distinguish speech from noise. Obtain consent and follow institutional privacy rules.")
