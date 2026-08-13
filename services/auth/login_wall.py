import streamlit as st

from services.persistence.exercise import get_or_create_user


def login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.title("💪 A Real-Time GYM Trainer")
    st.markdown("### Welcome! Please enter your username to start.")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Name (unique)",
            placeholder="Enter your name"
        )

        submit_button = st.form_submit_button(
            "Start Session",
            use_container_width=True
        )
   
    if submit_button:
        if not username:
            st.warning("Please enter a username.")
            return False

        user = get_or_create_user(username)

        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.success(f"Welcome, {user['username']}! You are now logged in.")

        st.rerun()

    return False