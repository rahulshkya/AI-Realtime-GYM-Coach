# Real-time Gym Trainer

Live demo: [ai-realtime-gym-coach-o2.streamlit.app](https://ai-realtime-gym-coach-o2.streamlit.app/)

An interactive Streamlit app that acts as a real-time AI gym coach. It uses webcam pose tracking to monitor exercise form, count reps and sets, store workout history, and provide voice coaching during a session.

## Features

- Live webcam workout tracking with `streamlit-webrtc`
- Exercise support for squats, push-ups, lunges, biceps curls, and shoulder press
- Real-time form metrics and workout progress counters
- Username-based login wall and per-user workout history
- Optional AI voice coaching powered by Groq and text-to-speech
- Local styling and custom fonts for the in-app experience

## Tech Stack

- Python 3.11
- Streamlit
- MediaPipe
- OpenCV
- NumPy
- Pandas
- Groq
- gTTS

## Project Structure

- `main.py` - Streamlit app entrypoint
- `core/` - base exercise logic
- `detectors/` - exercise-specific pose detectors
- `services/` - auth, coaching, tracking, persistence, config, UI, and vision helpers
- `static/` - app styling and assets
- `ml_models/` - pose landmarker model files
- `LandingPage/` - landing page assets

## Local Setup

1. Clone the repository.
2. Create and activate a Python environment using Python 3.11.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.streamlit/secrets.toml` file and add your Groq API key:

```toml
GROQ_API_KEY="your_groq_api_key_here"
```

5. Run the app:

```bash
streamlit run main.py
```

## How It Works

- Enter a username to start a session.
- Choose an exercise, sets, and reps from the sidebar.
- Start the workout to open the webcam tracker.
- Follow the live pose guidance and review your workout history after the session.

## Deployment Notes

- The app expects `GROQ_API_KEY` to be available through environment variables or Streamlit secrets.
- The project is configured for Python 3.11 via `runtime.txt`.
- `.streamlit/secrets.toml` is ignored from version control, so keep secrets local.

## License

No license file is included in this repository yet.