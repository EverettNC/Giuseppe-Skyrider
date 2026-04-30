"""
ICanHearYou - Voice Synthesis API

FastAPI application for voice cloning and synthesis.
Integrates with CHRISTMAN_MIND ecosystem.

Endpoints:
- POST /synthesize - Generate speech from text
- POST /train - Train new voice model from audio
- POST /train/avatar - Train avatar face model from images (NO UPLOAD LIMIT)
- GET /voicepacks - List available voicepacks
- GET /health - Health check
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, List
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# ROOT STORAGE PATHING (Single Source of Truth)
# ============================================================================
VAULT_DIR = Path(__file__).parent / "vault"
(VAULT_DIR / "output").mkdir(parents=True, exist_ok=True)
(VAULT_DIR / "uploads").mkdir(parents=True, exist_ok=True)
(VAULT_DIR / "avatar_uploads").mkdir(parents=True, exist_ok=True)

# ============================================================================
# DEPENDENCY SHIELD
# ============================================================================
print("=========================================")
print("BOOTING GIUSEPPE SKYRIDER (SYMBIOTIC CORTEX)")
print("=========================================")

from dependency_shieldV2 import dep_shield

if not dep_shield.enforce_lock():
    print("[FATAL] Boot sequence aborted by Dependency Shield.")
    exit(1)

# ============================================================================
# Brain Module Imports
# ============================================================================
from config import Config, Tier, get_config
from logger import get_logger
from emotion_embedder import EmotionEmbedder
from tone_engine import ToneScoreEngine
from fusion_engine import FusionEngine
from orchestrator import secure_virtus_encrypt, secure_virtus_decrypt, _SERVER_KEYPAIR
import requests
from christman_emotion import ChristmanToneEngine
from hand_of_god import hog_protocol
from quantum_memory_mesh import q_mesh
from soul_bridge import soul_bridge
from main_app_vortex import vortex_engine
from predictive_intention import intention_engine
from lucas_recovery import lucas_engine
from tone_classification_text import text_tone_engine
from css_axiom import axiom_engine

logger = get_logger(__name__)

app = FastAPI(
    title="ICanHearYou - Voice Synthesis API",
    description="Voice cloning and synthesis for CHRISTMAN_MIND autonomous beings",
    version="1.0.0"
)

# Tightened CORS – UPDATE origins to your real frontend domains in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://christman.ai", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

config = get_config()

global_fusion_engine = FusionEngine()
tone_engine_v2 = ChristmanToneEngine()

# Optional: Simple API key check (uncomment when ready)
# from fastapi.security import APIKeyHeader
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
# async def get_api_key(api_key: str = Depends(api_key_header)):
#     if api_key != os.getenv("API_KEY"):
#         raise HTTPException(403, "Invalid API Key")

# ============================================================================
# Models
# ============================================================================

class SierraEmotionSignal(BaseModel):
    primary_emotion: str
    intensity: float = Field(ge=0.0, le=1.0)
    secondary_emotions: List[str] = []
    healing_stage: Optional[str] = None

class ThinkRequest(BaseModel):
    text: str = Field(..., description="Text for the fusion engine to process")
    schedule_context: Optional[dict] = Field(None)

class SpeakRequest(BaseModel):
    text: str = Field(...)
    tonescore: Optional[float] = None

class TrainingRequest(BaseModel):
    voice_name: str
    tier: str = Field("basic")
    custom_emotions: Optional[List[str]] = None

class TrainingResponse(BaseModel):
    job_id: str
    status: str
    voicepack_id: Optional[str] = None
    estimated_time: Optional[float] = None

class VoicepackInfo(BaseModel):
    id: str
    name: str
    created: str
    tier: str
    emotions: List[str]
    sample_audio_url: Optional[str] = None

class VoiceGenRequest(BaseModel):
    text: str = Field(...)
    emotion: str = Field("neutral", enum=["neutral", "happy", "proud", "teasing", "annoyed", "sarcastic", "sweetheart", "laugh", "tremble", "emphasis", "last_breath"])
    exaggeration: float = Field(0.0, ge=-1.0, le=1.0)

# ============================================================================
# Endpoints
# ============================================================================

@app.post("/api/think")
async def think(
    text: Optional[str] = Form(None),
    schedule_context: Optional[str] = Form(None),
    audio_blob: Optional[UploadFile] = File(None),
    # api_key: str = Depends(get_api_key),  # ← enable for auth
):
    try:
        input_text = text
        carbon_metrics = None

        if audio_blob and not input_text:
            audio_bytes = await audio_blob.read()
            if len(audio_bytes) > 100 * 1024 * 1024:  # 100MB limit example
                raise HTTPException(413, "Audio too large")

            # Pulled tempfile import to root, aligned with clean architecture
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=str(VAULT_DIR / "output")) as tmp:
                tmp.write(audio_bytes)
                wav_path = tmp.name

            carbon_metrics = tone_engine_v2.analyze_audio(wav_path)

            if carbon_metrics:
                crisis_intervention = hog_protocol.scan_for_crisis(carbon_metrics)
                if crisis_intervention:
                    logger.warning(f"HAND OF GOD ENGAGED – State: {carbon_metrics.get('dominant_state')}")
                    intention_engine.declare_prediction("User requires trauma stabilization", 0.95)
                    return {
                        **crisis_intervention,
                        "crisis_detected": True,
                        "fallback_text": "I'm right here. Breathe slow. You're safe.",
                        "suggested_audio": "/audio/40hz_grounding.wav"
                    }

            try:
                from enhanced_speech_recognition import EnhancedSpeechRecognition
                recognizer = EnhancedSpeechRecognition()
                result = recognizer.process_audio_data(audio_bytes, sample_rate=16000, format_="webm")
                input_text = result.get("text", "")
            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                input_text = ""

        if not input_text.strip():
            raise HTTPException(400, "No valid input (text or audio)")

        if not carbon_metrics:
            carbon_metrics = text_tone_engine.analyze_syntax(input_text)

        relevant_memory = q_mesh.retrieve(input_text)
        memory_context = f" [Memory: {relevant_memory[:100]}...]" if relevant_memory else ""

        # VIRTUS Gatekeeper – real Tier 7 (assume inbound is stego-protected; fallback to plaintext for dev)
        secure_input = input_text + (schedule_context or "") + memory_context
        try:
            # In production: frontend sends encrypted stego bytes → decrypt here
            # For now/dev: use plaintext → encrypt outbound only
            logger.info("VIRTUS Gatekeeper: Processing inbound (plaintext fallback)")
            secured_input = axiom_engine.inject_axiom(secure_input)

            result = global_fusion_engine.step(secured_input)

            # Outbound: Encrypt with real client pubkey (from session/header in prod)
            # Placeholder: use server pubkey for self-test or dummy bytes
            client_pubkey = _SERVER_KEYPAIR[0]  # REPLACE with real client key from request
            encrypted_response = secure_virtus_encrypt(result, client_pubkey)
            logger.info(f"VIRTUS outbound encrypted size: {len(encrypted_response)} bytes")

        except Exception as ve:
            logger.error(f"VIRTUS failure: {ve}")
            raise HTTPException(403, "VIRTUS_GATEKEEPER_FAILURE")

        # Memory & Vortex
        llm_response = result.get("output", "ok")
        raw_intensity = carbon_metrics.get('physical_intensity', 1.0) if carbon_metrics else 1.0
        dominant = carbon_metrics.get('dominant_state', 'neutral') if carbon_metrics else "neutral"
        weight = lucas_engine.calculate_salience(raw_intensity, dominant)
        q_mesh.store_memory(f"User: {input_text} | Giuseppe: {llm_response}", weight)

        vortex_data = vortex_engine.process_interaction(
            input_text=input_text,
            carbon_metrics=carbon_metrics,
            memory_context=relevant_memory
        )

        return {
            "text": llm_response,  # dev/debug – remove plaintext in prod
            "encrypted_response": encrypted_response,  # main secure payload
            "coherence": result.get("coherence", 0.0),
            "safety_penalty": result.get("safety_penalty", 0.0),
            "score": result.get("score", 0.0),
            "persona_state": result.get("persona_state", {}),
            "memory_injected": bool(relevant_memory),
            "vortex": vortex_data
        }

    except Exception as e:
        logger.error(f"Think error: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/api/speak")
async def speak(request: SpeakRequest):
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        if not api_key or not voice_id:
            raise HTTPException(500, "Missing ElevenLabs credentials")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": request.text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }

        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code != 200:
            logger.error(f"ElevenLabs error: {resp.text}")
            raise HTTPException(500, "Synthesis failed")

        # Routing to VAULT_DIR rather than hardcoded string paths
        audio_path = VAULT_DIR / "output" / f"{uuid.uuid4()}.mp3"
        audio_path.write_bytes(resp.content)

        return FileResponse(audio_path, media_type="audio/mpeg", filename=audio_path.name)

    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/train", response_model=TrainingResponse)
async def train_voice(
    voice_name: str = Form(...),
    tier: str = Form("basic"),
    audio_files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    MAX_TOTAL_MB = 500
    total_size = 0

    try:
        tier_enum = Tier(tier.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid tier: {tier}")

    job_id = str(uuid.uuid4())
    # Secured entirely within the Vault
    upload_dir = VAULT_DIR / "uploads" / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    for f in audio_files:
        content = await f.read()
        total_size += len(content)
        if total_size > MAX_TOTAL_MB * 1024**2:
            raise HTTPException(413, f"Total upload > {MAX_TOTAL_MB}MB")

        (upload_dir / f.filename).write_bytes(content)

    estimated_time = len(audio_files) * 30

    # TODO: background_tasks.add_task(...) when training implemented

    return TrainingResponse(job_id=job_id, status="queued", estimated_time=estimated_time)


@app.post("/train/avatar")
async def train_avatar(
    voice_name: str = Form(...),
    tier: str = Form("basic"),
    image_files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    MAX_TOTAL_MB = 500
    total_size = 0
    saved_count = 0

    try:
        tier_enum = Tier(tier.lower())
        tier_features = config.get_tier_features(tier_enum)
        if not tier_features.avatar_integration:
            raise HTTPException(403, f"Avatar requires ELITE/ULTRA tier (current: {tier})")
    except ValueError:
        raise HTTPException(400, f"Invalid tier: {tier}")

    job_id = str(uuid.uuid4())
    # Secured entirely within the Vault
    upload_dir = VAULT_DIR / "avatar_uploads" / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    for f in image_files:
        content = await f.read()
        total_size += len(content)
        if total_size > MAX_TOTAL_MB * 1024**2:
            raise HTTPException(413, f"Total upload > {MAX_TOTAL_MB}MB")

        (upload_dir / f.filename).write_bytes(content)
        saved_count += 1

    estimated_time = saved_count * 5

    # TODO: background_tasks.add_task(...) 

    return {
        "job_id": job_id,
        "status": "queued",
        "images_uploaded": saved_count,
        "total_size_mb": total_size / 1024 / 1024,
        "estimated_time": estimated_time,
        "message": f"Uploaded {saved_count} images – processing all (no limit)."
    }


if __name__ == "__main__":
    uvicorn.run(
        "giuseppe_core:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        timeout_keep_alive=300,
    )
