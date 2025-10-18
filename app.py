import streamlit as st
from agent import process_message
from db import get_all_documents

st.set_page_config(
    page_title="Smart Follow-Up Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Smart Follow-Up Assistant")

tab1, tab2 = st.tabs(["💬 Assistant Chat", "📋 Ticket Dashboard"])

with tab1:
    st.subheader("Chat with your Smart Follow-Up Agent")
    user_input = st.text_area(
        "Your message:",
        placeholder="e.g. Remind me to follow up with CTO tomorrow",
        height=100
    )

    if st.button("Process Message", use_container_width=True):
        if user_input.strip():
            with st.spinner("Analyzing message..."):
                result = process_message(user_input)
            st.success("✅ Message processed")
            st.json(result)
        else:
            st.warning("Please type something first.")

with tab2:
    st.subheader("Your Tickets")

    tickets = get_all_documents()

    if tickets:
        for t in tickets:
            with st.expander(f"{t.get('title', 'Untitled Ticket')} ({t.get('type', '')})"):
                st.markdown(f"**ID:** {t['_id']}")
                st.markdown(f"**Description:** {t.get('description', '')}")
                st.markdown(f"**Action:** {t.get('action', '')}")
                st.markdown("### 🧾 Messages:")
                for msg in t.get("messages", []):
                    st.markdown(f"- {msg}")
    else:
        st.info("No tickets found yet. Try chatting with the assistant first.")