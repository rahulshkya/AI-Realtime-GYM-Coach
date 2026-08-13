
import streamlit as st
from services

def sync_metrics_update(context):
    if not context or not hasattr(context,"state") or not context.state.playing:
        return


    processor =getattr(context.state,"video_processor",None)


    if not processor:
        return

    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return

    processor.set_exercise(exercise)

    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return

    reps = latest_metrics.get("reps")

    if not reps:
        return

    st.session_state.reps = reps
