import streamlit as st
from agent import process_message

st.set_page_config(page_title="Assistant Chat", page_icon="💬")

st.title("💬 Assistant Chat")

# Chat input area
user_input = st.text_area("Your message", placeholder="Type something like 'Remind me to follow up with CTO tomorrow'...")

if st.button("Process Message", use_container_width=True):
    if user_input.strip():
        with st.spinner("Thinking..."):
            result = process_message(user_input)
        st.success("✅ Done!")
        st.json(result)
    else:
        st.warning("Please type a message first.")