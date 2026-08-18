import os
import tomllib
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomllib.load(f)
        api_key = secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

models = client.models.list()
for m in models.data:
    print(m.id)