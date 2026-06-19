import streamlit as st
import uuid
from utils.database import create_conversation, save_message, log_search
from utils.ai_model import is_using_fallback, answer_faq, get_model_name
from utils.styles import inject_base_css, callout

st.set_page_config(page_title="Health FAQ Chatbot", page_icon="💬", layout="wide")
inject_base_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "faq_conv_id" not in st.session_state:
    st.session_state.faq_conv_id = create_conversation(st.session_state.session_id, "faq")
if "faq_messages" not in st.session_state:
    st.session_state.faq_messages = []

col1, col2 = st.columns([3, 1])
with col1:
    st.title("💬 Health FAQ Chatbot")
    st.caption("Ask any general health question. Powered by Hugging Face.")
with col2:
    st.markdown(f"<br><span class='badge badge-primary'>🤖 {get_model_name()}</span>", unsafe_allow_html=True)
    if is_using_fallback():
        st.caption("⛔ Primary model failed to load — using lower-quality fallback.")
    if st.button("🗑️ Clear Chat"):
        st.session_state.faq_messages = []
        st.session_state.faq_conv_id = create_conversation(st.session_state.session_id, "faq")
        st.rerun()

st.divider()

st.markdown("**Quick questions:**")
quick_cols = st.columns(3)
quick_qs = [
    "What are symptoms of the flu?",
    "How much water should I drink daily?",
    "What causes high blood pressure?",
    "How can I improve my sleep quality?",
    "What vitamins should I take daily?",
    "When should I see a doctor for a fever?",
]
for i, q in enumerate(quick_qs):
    if quick_cols[i % 3].button(q, key=f"quick_{i}"):
        st.session_state["faq_prefill"] = q

st.divider()

chat_container = st.container()
with chat_container:
    if not st.session_state.faq_messages:
        st.info("👋 Hello! Ask me any health-related question and I'll do my best to help.")
    for msg in st.session_state.faq_messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'><strong>🧑 You</strong><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'><strong>🏥 Healthcare AI</strong><br>{msg['content']}</div>", unsafe_allow_html=True)

prefill = st.session_state.pop("faq_prefill", "")
with st.form("faq_form", clear_on_submit=True):
    user_input = st.text_input(
        "Your question:",
        value=prefill,
        placeholder="e.g. What are the symptoms of anemia?",
    )
    submitted = st.form_submit_button("Send →", use_container_width=True)

if submitted and user_input.strip():
    question = user_input.strip()
    st.session_state.faq_messages.append({"role": "user", "content": question})
    save_message(st.session_state.faq_conv_id, "user", question)
    log_search(st.session_state.session_id, "faq", question)

    with st.spinner("Thinking…"):
        answer = answer_faq(question, st.session_state.faq_messages[:-1])

    st.session_state.faq_messages.append({"role": "assistant", "content": answer})
    save_message(st.session_state.faq_conv_id, "assistant", answer)
    st.rerun()

with st.sidebar:
    st.markdown("### 📜 This Session")
    user_msgs = [m for m in st.session_state.faq_messages if m["role"] == "user"]
    if user_msgs:
        for m in user_msgs[-5:]:
            st.markdown(f"- {m['content'][:60]}{'…' if len(m['content'])>60 else ''}")
    else:
        st.caption("No questions yet.")

    st.divider()
    st.markdown("""
    **Tips:**
    - Be specific for better answers
    - Mention age/context if relevant
    - For emergencies, call your local emergency number
    """)
    callout("Not a substitute for professional medical advice.", kind="warn")
