import streamlit as st
import uuid
from utils.database import get_stats, get_recent_history
from utils.styles import inject_base_css

st.set_page_config(page_title="History & Analytics", page_icon="📊", layout="wide")
inject_base_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("📊 History & Analytics")
st.caption("Overview of all queries and usage across this app.")

stats = get_stats()
c1, c2, c3 = st.columns(3)
c1.metric("💬 Total Conversations", stats["total_chats"])
c2.metric("❓ Questions Asked", stats["total_messages"])
c3.metric("📄 Reports Analyzed", stats["total_reports"])

st.divider()

st.markdown("### 🕑 Recent activity (this session)")
history = get_recent_history(st.session_state.session_id, limit=20)
if history:
    feature_icons = {"faq": "💬", "disease": "🔬", "medicine": "💊", "report": "📄"}
    for item in history:
        icon = feature_icons.get(item["feature"], "🔍")
        st.markdown(
            f"<div class='card'>{icon} <strong>{item['feature'].upper()}</strong> — {item['query']} "
            f"<span style='color:#9DA7B3;font-size:0.8rem;'>({item['searched_at']})</span></div>",
            unsafe_allow_html=True,
        )
else:
    st.info("No activity yet. Start by asking a question or uploading a report!")

st.divider()
st.markdown("""
### 🗄️ Database Info
- **Location:** `data/healthcare.db` (SQLite, local)
- **Tables:** `conversations`, `messages`, `report_uploads`, `search_history`
- **Data stays local** — nothing is sent to external servers (except the HuggingFace model download on first run)
""")
