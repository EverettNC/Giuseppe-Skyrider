import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"Voice ID loaded: {'Yes' if voice_id else 'No'}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}")
