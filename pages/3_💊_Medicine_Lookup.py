import streamlit as st
import uuid
from utils.database import create_conversation, save_message, log_search
from utils.ai_model import is_using_fallback, lookup_medicine, get_model_name
from utils.styles import inject_base_css, callout

st.set_page_config(page_title="Medicine Lookup", page_icon="💊", layout="wide")
inject_base_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "medicine_history" not in st.session_state:
    st.session_state.medicine_history = []

st.title("💊 Medicine Information Lookup")
st.caption("Search for drug details, side effects, and interactions.")

callout(
    "<strong>Important:</strong> Medicine information provided here is for <strong>educational purposes only</strong>. "
    "Dosages and interactions vary by individual. <strong>Always consult your doctor or pharmacist</strong> "
    "before taking any medication.",
    kind="warn",
)

st.markdown("### Common medicines")
common_meds = [
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Metformin",
    "Atorvastatin", "Omeprazole", "Aspirin", "Amlodipine",
    "Cetirizine", "Azithromycin", "Pantoprazole", "Vitamin D",
]
cols = st.columns(4)
for i, med in enumerate(common_meds):
    if cols[i % 4].button(med, key=f"med_{i}"):
        st.session_state["med_prefill"] = med

st.divider()

prefill = st.session_state.pop("med_prefill", "")
with st.form("medicine_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        med_input = st.text_input(
            "Medicine name (generic or brand):",
            value=prefill,
            placeholder="e.g. Metformin, Paracetamol, Lisinopril, Vitamin D3…",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.form_submit_button("Look up →", use_container_width=True)

if search_btn and med_input.strip():
    medicine = med_input.strip()
    log_search(st.session_state.session_id, "medicine", medicine)

    with st.spinner(f"Looking up '{medicine}'…"):
        info = lookup_medicine(medicine)

    st.session_state.medicine_history.insert(0, {"medicine": medicine, "info": info})

    conv_id = create_conversation(st.session_state.session_id, "medicine")
    save_message(conv_id, "user", f"Medicine info: {medicine}")
    save_message(conv_id, "assistant", info)

if st.session_state.medicine_history:
    latest = st.session_state.medicine_history[0]

    st.markdown(f"## 💊 {latest['medicine']}")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<div class='result-box result-box-warn'>{latest['info']}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### ⚡ Quick Info")
        st.markdown("""
        <span class='badge badge-warn'>⚠️ Consult doctor</span>
        <span class='badge badge-warn'>🚫 No self-medication</span>
        <span class='badge badge-info'>ℹ️ Educational only</span>
        <span class='badge badge-info'>💊 Check interactions</span>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "📥 Save info",
            data=f"Medicine: {latest['medicine']}\n\n{latest['info']}",
            file_name=f"{latest['medicine'].replace(' ', '_')}_info.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if len(st.session_state.medicine_history) > 1:
        st.divider()
        st.markdown("### 🕑 Recent lookups")
        for entry in st.session_state.medicine_history[1:5]:
            with st.expander(f"💊 {entry['medicine']}"):
                st.markdown(entry["info"])

else:
    st.info("💊 Search for a medicine above to get detailed information.")

with st.sidebar:
    st.markdown(f"**Model:** `{get_model_name()}`")
    if is_using_fallback():
        callout(
            "The primary AI model failed to load, so answers are currently coming from a "
            "lower-quality fallback model. Check the app logs for the load error.",
            kind="danger",
        )
    st.divider()
    st.markdown("### 🕑 Lookup history")
    if st.session_state.medicine_history:
        for e in st.session_state.medicine_history[:8]:
            st.markdown(f"- {e['medicine']}")
    else:
        st.caption("None yet.")

    st.divider()
    st.markdown("""
    **What you'll find:**
    - Indications / uses
    - Dosage guidance
    - Common side effects
    - Major interactions
    - Important warnings
    """)
    callout("Never change dosage without consulting your doctor.", kind="danger")
