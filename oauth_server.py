import requests
from flask import Flask, request, jsonify, redirect
import re  # For extracting emojis

app = Flask(__name__)

# =======================
# Configuration Section
# =======================
# Replace these with your new Zoom OAuth credentials
CLIENT_ID = "XeBUEdCKRB2TuUYMCn8mwQ"
CLIENT_SECRET = "HUT8ma2fY2kk6CAzF6AmHp9UhoapWAnB"

# Tokens
SECRET_TOKEN = "DVb8pCcSTteCwKPP2oxikA"
VERIFICATION_TOKEN = "a3VcjPvKRzOohwhg6CFlzQ"

# Redirect URI
REDIRECT_URI = "https://obs-overlays.vercel.app/oauth/callback"

# Zoom API Endpoints
TOKEN_URL = "https://zoom.us/oauth/token"
CHAT_MESSAGES_URL = "https://api.zoom.us/v2/chat/users/me/messages"
AUTH_URL = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

# =======================
# Utility Functions
# =======================

# Function to extract emojis from a text message
def extract_emojis(text):
    emoji_pattern = re.compile(
        "["  # Add Unicode ranges for emojis
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001FA00-\U0001FAFF"  # Supplemental symbols
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

# =======================
# Flask Routes
# =======================

@app.route("/")
def home():
    return f'<a href="{AUTH_URL}">Connect Your Zoom Account</a>'

@app.route("/oauth/callback")
def oauth_callback():
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "Authorization code not provided"}), 400

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(
        TOKEN_URL,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve access token"}), response.status_code

    response_data = response.json()
    return jsonify({"access_token": response_data.get("access_token")})

@app.route("/zoom-data")
def get_zoom_data():
    # Fixed token for testing
    token = "eyJzdiI6IjAwMDAwMiIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6ImMxZjUzYzkxLTUyYzQtNDQ5Yy05MmRiLTFlYzkzOTI2NDYzYSJ9.eyJ2ZXIiOjEwLCJhdWlkIjoiNzg5YzQ2NzAyNzU2NDUzYTgyNzQ2Yzk4N2YxZjY0ZjU5NzQwMTgxYTFiNGE2NmRjYjc0Mjk4N2QwYWQ3NzQxYiIsImNvZGUiOiI0U2hxUFAxU2NOUVlIVVB1WjhkUkMtaDBFRGx2dXBmVVEiLCJpc3MiOiJ6bTpjaWQ6WGVCVUVkQ0tSQjJUdVVZTUNuOG13USIsImdubyI6MCwidHlwZSI6MCwidGlkIjowLCJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiI0UHlpcXZ5dFFLeWZZcllrTUo0MFNBIiwibmJmIjoxNzM0OTM2Mjk5LCJleHAiOjE3MzQ5Mzk4OTksImlhdCI6MTczNDkzNjI5OSwiYWlkIjoib0hjRnQtaXdUTTZzbXdvLTdIUEhYZyJ9.T2Zx9_jc1JW1AHHpG6bxTSZC2sgcNs3WR9NiOXah7NYkMQcduyFsNq6MbrvYtnFXHYe3nNCNtHhsa78VE4hFUQ"

    response = requests.get(
        CHAT_MESSAGES_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Debugging: Print response details
    print("Chat Messages Debug:")
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve chat messages"}), response.status_code

    chat_messages = response.json().get("messages", [])
    emojis = []
    for msg in chat_messages:
        emojis.extend(extract_emojis(msg.get("message", "")))

    return jsonify({
        "chat": [msg.get("message", "") for msg in chat_messages],
        "reactions": emojis
    })

# =======================
# Main Entry Point
# =======================

if __name__ == "__main__":
    app.run(port=5000)
