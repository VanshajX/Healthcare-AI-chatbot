import streamlit as st

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_base_css, callout, footer
from utils.database import init_db, get_stats

init_db()
inject_base_css()

st.markdown("""
<div class="main-header">
    <h1>🏥 Healthcare AI Assistant</h1>
    <p style="margin:0; font-size:1.1rem;">
        Your intelligent health companion — powered by AI, built for learning
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### What can I help you with?")
    st.markdown("""
    <div class="card">💬 <strong>Health FAQ Chatbot</strong> — Ask any general health question in natural language</div>
    <div class="card">🔬 <strong>Disease Explainer</strong> — Get clear, simple explanations of any disease or condition</div>
    <div class="card">💊 <strong>Medicine Lookup</strong> — Search for drug information, side effects & interactions</div>
    <div class="card">📄 <strong>Report Summarizer</strong> — Upload a medical report (PDF/image) and get a plain-English summary</div>
    """, unsafe_allow_html=True)

    callout(
        "<strong>Important Disclaimer:</strong> This tool is for educational and informational purposes only. "
        "It is <strong>not</strong> a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider for medical concerns.",
        kind="warn",
    )

    st.markdown("### 🧭 Use the sidebar to navigate")
    st.caption("Open **💬 FAQ Chatbot**, **🔬 Disease Explainer**, **💊 Medicine Lookup**, **📄 Report Summarizer**, or **📊 History** from the left sidebar.")

with col2:
    st.markdown("### 📊 Quick Stats")
    stats = get_stats()
    st.metric("Total Conversations", stats["total_chats"])
    st.metric("Questions Asked", stats["total_messages"])
    st.metric("Reports Analyzed", stats["total_reports"])

    with st.expander("🛠️ Tech Stack", expanded=False):
        st.markdown("""
        - **Frontend:** Streamlit
        - **AI Model:** Hugging Face Transformers (FLAN-T5, fallback GPT-2)
        - **OCR:** Tesseract + Pillow
        - **PDF Parsing:** PyMuPDF
        - **Database:** SQLite
        """)

footer()
