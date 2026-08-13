import os
from time import time

import streamlit as st
from services.auth.login_wall import login_wall
from services.state.session_default import initial_session_default
from services.config.workout_config import EXERCISE_OPTIONS
from services.tracking.metrics import sync_metrics_update
from services.ui.style_loader import load_css, inject_local_font,inject_webrtc_styles
from services.persistence.exercise import init_db
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
from services.config.metrics_config import EXERCISE_METRICS
from services.vision.exercise_video_processor import VideoProcessorClass

def main():
    init_db()
    initial_session_default()
    st.set_page_config(page_title="💪 A Real-Time GYM Trainer", page_icon="💪", layout="centered", initial_sidebar_state="expanded")
    if not login_wall():
        return


    load_css(os.path.join(os.getcwd(),"static","style.css"))
    inject_local_font(os.path.join(os.getcwd(),"static","AdobeClean-Regular.otf"),"Adobe Clean")
    st.write("Welcome to the Real-Time GYM Trainer application!")

    workout_started = st.session_state.get("workout_started", False)
    with st.sidebar:
        st.title(" RS AI Coach")

        if st.session_state.username:
            st.caption(f"Logged in as: {st.session_state.username}")
    
        st.divider()

        st.subheader("Workout Plan")

        if not workout_started:
            st.selectbox("Exercise", EXERCISE_OPTIONS, key="plan_exercise")

            st.number_input("Sets", min_value=1, max_value=10, value=3, step=1, key="plan_sets")

            st.number_input("Reps per Set", min_value=1, max_value=50, value=10, step=1, key="plan_reps")


            st.markdown("")

            start_session_button = st.button("Start Session", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state["workout_started"] = True

                st.session_state.exercise_type = st.session_state.plan_exercise
                st.session_state.target_sets = int(st.session_state.plan_sets)
                st.session_state.reps_per_set = int(st.session_state.plan_reps)

                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False


                st.rerun()

                
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")
            print(exercise, sets, reps)
            st.info(f"Workout in progress: {exercise} - {sets} sets of {reps} reps")
            end_session_button =st.button("End Session", width="stretch", key="end_session_button")

            if end_session_button:
                st.session_state["workout_started"]=False
                st.session_state["sets_completed"]=0
                st.session_state["reps_per_set"]=0
                st.session_state["current_set_reps"]=0
                st.session_state["workout_complete"]=False
                st.session_state["last_notified_sets_completed"]=0
                st.session_state["last_notified_workout_complete"]=False
                st.session_state["last_saved_sets_completed"]=0
                st.session_state["set_cycle_started_at"]=0.0
                st.session_state["last_exercise_type"]="Squats"
                st.rerun()

        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type")
            total_reps=st.session_state.get("reps")
            reps_per_sets=st.session_state.get("reps_per_set")
            current_set_reps=st.session_state.get("current_set_reps")
            sets_completed=st.session_state.get("sets_completed")
            target_sets=st.session_state.get("target_sets")
            st.subheader("Workout Progress")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Reps", total_reps)

            with col2:
                st.metric("Current Set", current_set_reps)

            with col3:
                st.metric("Sets", f"{sets_completed}/{target_sets}")


            st.divider()

            exercise_info = EXERCISE_METRICS.get(exercise)

            if exercise_info:
                st.subheader(exercise_info["title"])

                for label, key, value_type in exercise_info["metrics"]:

                    value = st.session_state.get(key)

                    if value is None:
                        if value_type == "angle":
                            value = 0.0
                        else:
                            value = "N/A"

                    if value_type == "angle":
                        st.metric(label, f"{float(value):.1f}°")
                    else:
                        st.metric(label, value)

    st.title("AI Real-time GYM coach")
    st.markdown("#### real time pose detection with proactiv AI voice coaching ")

    if not workout_started:
        st.markdown("""
        <div style="
        border:10px dashed #444;
        border-radius:0px;
        padding:48px 32px;
        text-align:center;
        color:#888;
        margin-top:32px;
        ">
        <h2 style="color:#ccc; margin-bottom:8px;">set your workout plan </h2>
        <p style="color:#aaa; font-size:16px;">select your exercise, sets and reps to start your workout session then <strong>click "Start Workout"</strong></p>
        </div>
        """,unsafe_allow_html=True)

    else:
        context=webrtc_streamer(
            key="exercise_streamer",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers":[
                {
                    "urls":["stun:stun.l.google.com:19302"]
                }
            ]
        },
        media_stream_constraints={"video":True,"audio":False},
        async_processing=True
            
        )

    sync_metrics_update(context)
    inject_webrtc_styles()
    st.markdown("#### workout History")

    
if __name__ == "__main__":
    main()
