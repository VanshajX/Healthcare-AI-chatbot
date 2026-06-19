import streamlit as st
import uuid
from utils.database import save_report, log_search
from utils.ai_model import is_using_fallback, summarise_report, get_model_name
from utils.report_parser import extract_text
from utils.styles import inject_base_css, callout

st.set_page_config(page_title="Report Summarizer", page_icon="📄", layout="wide")
inject_base_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "report_history" not in st.session_state:
    st.session_state.report_history = []

st.title("📄 Medical Report Summarizer")
st.caption("Upload a medical report (PDF, image, or text) and get a plain-English summary.")

st.markdown(
    "<div class='result-box result-box-purple'>🔒 <strong>Privacy:</strong> Your report is processed locally "
    "and never stored permanently. The summary is saved in your local SQLite database only.</div>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "txt", "png", "jpg", "jpeg"],
    help="Supported: PDF, plain text (.txt), or scanned image (PNG/JPG)",
)

if uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
    with col2:
        summarize_btn = st.button("🔍 Summarize Report", use_container_width=True, type="primary")

    if summarize_btn:
        with st.spinner("Extracting text from report…"):
            raw_text, file_type = extract_text(uploaded_file)

        if raw_text.startswith("["):
            st.error(raw_text)
        else:
            with st.expander("📝 Extracted raw text (click to expand)"):
                shown = raw_text[:3000] + ("…" if len(raw_text) > 3000 else "")
                st.markdown(f"<div class='extracted-text'>{shown}</div>", unsafe_allow_html=True)

            with st.spinner("AI is reading your report…"):
                summary = summarise_report(raw_text)

            st.session_state.report_history.insert(0, {
                "filename": uploaded_file.name, "file_type": file_type,
                "summary": summary, "raw": raw_text,
            })
            save_report(st.session_state.session_id, uploaded_file.name, summary)
            log_search(st.session_state.session_id, "report", uploaded_file.name)

st.divider()

if st.session_state.report_history:
    latest = st.session_state.report_history[0]
    st.markdown(f"## 📋 Summary: {latest['filename']}")
    st.markdown(f"<span class='badge badge-purple'>📁 {latest['file_type']}</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-box result-box-purple'>{latest['summary']}</div>", unsafe_allow_html=True)
    callout(
        "<strong>Disclaimer:</strong> This AI summary is for informational purposes only. "
        "Always review with your doctor.",
        kind="warn",
    )
    st.download_button(
        "📥 Download Summary",
        data=f"Report: {latest['filename']}\n\n{latest['summary']}",
        file_name=f"{latest['filename']}_summary.txt",
        mime="text/plain",
    )

    if len(st.session_state.report_history) > 1:
        st.divider()
        st.markdown("### 🕑 Previous reports this session")
        for entry in st.session_state.report_history[1:4]:
            with st.expander(f"📄 {entry['filename']}"):
                st.markdown(entry["summary"])
else:
    st.info("📄 Upload a medical report above to get started.")

with st.sidebar:
    st.markdown(f"**Model:** `{get_model_name()}`")
    if is_using_fallback():
        callout(
            "The primary AI model failed to load, so answers are currently coming from a "
            "lower-quality fallback model. Check the app logs for the load error.",
            kind="danger",
        )
    st.divider()
    st.markdown("### 📁 Analyzed this session")
    if st.session_state.report_history:
        for e in st.session_state.report_history[:5]:
            st.markdown(f"- {e['filename']}")
    else:
        st.caption("None yet.")
    st.divider()
    st.markdown("""
    **Supported formats:**
    - 📄 PDF reports
    - 🖼️ Scanned images (PNG/JPG)
    - 📝 Plain text files (.txt)

    **What gets highlighted:**
    - Key findings & values
    - Abnormal results
    - Follow-up recommendations
    """)
    callout("Always verify with your doctor.", kind="warn")
