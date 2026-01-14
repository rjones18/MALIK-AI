import os
import uuid
import json
import datetime

import boto3
from flask import Flask, render_template, request, jsonify, url_for
from openai import OpenAI


# ============================================
# AWS Secrets Manager — Load API Key
# ============================================

def get_openai_key_from_secrets(secret_name: str) -> str:
    client = boto3.client("secretsmanager")

    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret_data = json.loads(response["SecretString"])
        return secret_data.get("API_KEY")

    raise Exception("Failed to read API_KEY from Secrets Manager")


OPENAI_SECRET_NAME = "MALIK_SECRETS"  # <--- your AWS secret name
OPENAI_API_KEY = get_openai_key_from_secrets(OPENAI_SECRET_NAME)

client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================
# Flask, Polly, etc.
# ============================================

app = Flask(__name__)

AUDIO_DIR = os.path.join(app.static_folder or "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

polly = boto3.client("polly")


# ============================================
#  OpenAI brain
# ============================================

def ask_openai(prompt: str) -> str:
    """
    Send the user's text to OpenAI and return Malik's reply.
    Uses the new OpenAI client API.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        return "My OpenAI brain isn't configured yet. Please add a valid API key."

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # choose any model you like
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Malik, a friendly, confident AI assistant. "
                        "Answer clearly and concisely. Break down technical topics "
                        "in simple terms when needed."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"[OpenAI] Error: {e}")
        return "My OpenAI brain had trouble thinking. Try again in a moment."


# ============================================
#  Malik's command routing
# ============================================

def respond_to_command(command: str) -> str:
    """
    Handle some commands locally (name, time, joke, exit),
    and delegate all other questions to OpenAI.
    """
    text = (command or "").strip()
    lc = text.lower()

    if "your name" in lc or "who are you" in lc:
        return "I am Malik, your intelligent assistant."
    elif "time" in lc:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
    elif "joke" in lc:
        return "Why did the AI go broke? Because it had too many neural debts!"
    elif any(word in lc for word in ["exit", "quit", "shut down", "shutdown"]):
        return "Shutting down. Goodbye."
    elif not text:
        return "Say something so I can help you."

    # Everything else → OpenAI
    return ask_openai(text)


# ============================================
#  Amazon Polly Text-to-Speech
# ============================================

def synthesize_speech_to_file(text: str) -> str:
    """
    Use Amazon Polly to synthesize Malik's reply to an MP3 file.
    Returns the filename (not the full path).
    """
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Matthew",  # change to another Polly voice if you want
    )

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(response["AudioStream"].read())

    return filename


# ============================================
#  Routes
# ============================================

@app.route("/")
def index():
    """
    Renders the Bootstrap + JS UI.
    Make sure you have templates/index.html present.
    """
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Frontend sends JSON: { "message": "..." }
    We:
      - Run respond_to_command (local logic + OpenAI)
      - Generate an MP3 via Polly
      - Return JSON with text reply + audio URL
    """
    data = request.get_json(force=True)
    user_message = data.get("message", "")

    # Malik thinks
    reply = respond_to_command(user_message)

    # Malik speaks
    audio_url = None
    try:
        audio_filename = synthesize_speech_to_file(reply)
        audio_url = url_for("static", filename=f"audio/{audio_filename}")
    except Exception as e:
        print(f"[Polly] Error: {e}")
        # audio_url stays None; frontend will still have text

    return jsonify(
        {
            "reply": reply,
            "audio_url": audio_url,
        }
    )


# ============================================
#  Main entrypoint
# ============================================

if __name__ == "__main__":
    # Run in dev mode – open http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=8080, debug=True)


