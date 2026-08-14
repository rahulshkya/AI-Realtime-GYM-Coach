import os
import time
import pandas as pd
from services.persistence.exercise import get_users_exercises
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

            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")

            end_session_button = st.button("End Workout", key="end_session_button", width="stretch")

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
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("target_sets")

            st.subheader("Progress")

            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability", st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)


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

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()
        inject_webrtc_styles()

    st.divider()
    st.markdown("#### workout History")

    user_id =st.session_state.get("user_id",0)

    if isinstance(user_id,int):
        history_rows=get_users_exercises(user_id)

        arr=[
            {
                "Exercise":row['exercise_name'],
                "Reps":row['reps'],
                "Sets":row['sets'],
                "Time (s)":row['time'],
                "Date":row['created_at']
            }
            for row in history_rows
        ]

        df =pd.DataFrame(arr)

        if not df.empty:
           
            df["Date"]=pd.to_datetime(df["Date"]).dt.date
            agg_df=df.groupby(["Exercise","Date"]).agg({
                "Reps":"sum",
                "Sets":"sum",
                "Time (s)":"sum"
            }).reset_index()
            agg_df.index += 1
            st.table(agg_df,border="horizontal")

        else:
            st.info("No workout history found. Start your first session to see your progress here!")



    
if __name__ == "__main__":
    main()
