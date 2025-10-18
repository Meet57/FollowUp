import streamlit as st
from db import get_all_documents
from bson import ObjectId

st.set_page_config(page_title="Ticket Dashboard", page_icon="📋")

st.title("📋 Ticket Dashboard")
st.markdown("Here are all the tickets created by the assistant.")

tickets = get_all_documents()

if tickets:
    for t in tickets:
        with st.expander(f"🎫 {t.get('title', 'Untitled Ticket')} ({t.get('type', '')})"):
            st.markdown(f"**ID:** {str(t['_id'])}")
            st.markdown(f"**Description:** {t.get('description', '')}")
            st.markdown(f"**Action:** {t.get('action', '')}")
            st.markdown("### 🧾 Messages:")
            for msg in t.get("messages", []):
                st.markdown(f"- {msg}")
else:
    st.info("No tickets found yet. Try chatting with the assistant first.")