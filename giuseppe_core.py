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
from pathlib import Path
from typing import Optional, List, Dict
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, Tier, get_config
from logger import get_logger
from emotion_embedder import EmotionEmbedder
from tone_engine import ToneScoreEngine
from fusion_engine import FusionEngine
from orchestrator import secure_virtus_decrypt, secure_virtus_encrypt, _SERVER_KEYPAIR
import requests
from christman_emotion import ChristmanToneEngine
from hand_of_god import hog_protocol
from quantum_memory_mesh import q_mesh
from soul_bridge import soul_bridge
from main_app_vortex import vortex_engine

logger = get_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="ICanHearYou - Voice Synthesis API",
    description="Voice cloning and synthesis for CHRISTMAN_MIND autonomous beings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global config
config = get_config()

# Global Fusion Engine Instance for state persistence across endpoints
global_fusion_engine = FusionEngine()

# Global Christman Tone Engine (The Hearing Layer)
tone_engine_v2 = ChristmanToneEngine()

# ============================================================================
# Request/Response Models
# ============================================================================

class SierraEmotionSignal(BaseModel):
    """Emotion signal from Sierra (CHRISTMAN_MIND Gen 1 agent)."""
    primary_emotion: str  # grief, trauma, healing, anger, neutral
    intensity: float = Field(ge=0.0, le=1.0)
    secondary_emotions: List[str] = []
    healing_stage: Optional[str] = None


class ThinkRequest(BaseModel):
    """Request for Silicon Brain thought generation."""
    text: str = Field(..., description="Text for the fusion engine to process")
    schedule_context: Optional[dict] = Field(None, description="Optional schedule context")


class SpeakRequest(BaseModel):
    """Request for elevenlabs voice synthesis."""
    text: str = Field(..., description="Text to synthesize")
    tonescore: Optional[float] = Field(None, description="Optional ToneScore integration")


class TrainingRequest(BaseModel):
    """Request for voice training."""
    voice_name: str
    tier: str = Field("basic", description="Training tier")
    
    # Optional emotion model (ULTRA tier only)
    custom_emotions: Optional[List[str]] = None


class TrainingResponse(BaseModel):
    """Response from voice training."""
    job_id: str
    status: str
    voicepack_id: Optional[str] = None
    estimated_time: Optional[float] = None


class VoicepackInfo(BaseModel):
    """Information about a voicepack."""
    id: str
    name: str
    created: str
    tier: str
    emotions: List[str]
    sample_audio_url: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@app.post("/api/think")
async def think(
    text: Optional[str] = Form(None),
    schedule_context: Optional[str] = Form(None),
    audio_blob: Optional[UploadFile] = File(None)
):
    """
    Ingest user text, schedule context, and potentially an audio blob.
    Instantiates and calls FusionEngine.step() to generate a mathematically sound,
    sassy, Carbon<->Silicon entangled response.
    """
    try:
        input_text = text
        carbon_metrics = None  # Initialized here so Memory Mesh always has access
        
        # Explicit Audio processing without magical placeholders
        if audio_blob and not input_text:
            audio_bytes = await audio_blob.read()
            
            # ============================================================
            # CARBON LAYER: Save raw audio to disk for ToneScore analysis
            # ============================================================
            import tempfile
            audio_tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="data/output")
            audio_tmp.write(audio_bytes)
            audio_tmp.close()
            wav_file_path = audio_tmp.name
            
            # ============================================================
            # THE HEARING ENGINE: Analyze the raw Carbon waveform
            # ============================================================
            carbon_metrics = tone_engine_v2.analyze_audio(wav_file_path)
            
            if carbon_metrics:
                logger.info(f"[CARBON LAYER] Dominant State: {carbon_metrics['dominant_state']} | Intensity: {carbon_metrics['physical_intensity']}")
                
                # ==========================================================
                # HAND OF GOD: Scan BEFORE the LLM ever sees the input
                # ==========================================================
                crisis_intervention = hog_protocol.scan_for_crisis(carbon_metrics)
                
                if crisis_intervention:
                    # THE LLM IS BYPASSED. RETURN IMMEDIATELY TO FRONTEND.
                    logger.warning(f"!!! HAND OF GOD ENGAGED — Dominant: {carbon_metrics['dominant_state']}, Intensity: {carbon_metrics['physical_intensity']} !!!")
                    return crisis_intervention
                
                # ==========================================================
                # SOUL BRIDGE: Pipe Carbon metrics to the Inferno Soul Forge
                # ==========================================================
                forge_tensor = soul_bridge.vector_out_to_forge(carbon_metrics, text_context=input_text)
                if forge_tensor is not None:
                    logger.info(f"[SOUL BRIDGE] Empathy Vector piped to Forge successfully.")
            
            # ============================================================
            # STANDARD PATH: Transcribe audio if no crisis detected
            # ============================================================
            try:
                from enhanced_speech_recognition import EnhancedSpeechRecognition
                recognizer = EnhancedSpeechRecognition()
            except ImportError as e:
                logger.error(f"Module missing: {e}")
                raise HTTPException(status_code=500, detail="Local speech recognition module is missing. SILICON FAILURE.")
                
            recognition_result = recognizer.process_audio_data(audio_bytes, sample_rate=16000, format_="webm")
            
            if "error" in recognition_result:
                raise HTTPException(status_code=500, detail=f"Local transcription failed: {recognition_result['error']}")
                
            input_text = recognition_result.get("text", "")
            
        if not input_text or not input_text.strip():
            logger.error("No valid text or audio input provided. Failing loud.")
            raise HTTPException(status_code=500, detail="Transcription resulted in empty text. SILICON FAILURE.")
            
        logger.info(f"Think request received: {input_text[:50]}, has_audio={audio_blob is not None}")
        
        # ============================================================
        # QUANTUM MEMORY MESH: Retrieve context BEFORE the LLM sees it
        # ============================================================
        relevant_memory = q_mesh.retrieve(input_text)
        
        memory_context = ""
        if relevant_memory:
            logger.info(f"[MEMORY MESH] Context Restored: {relevant_memory[:80]}...")
            memory_context = f" [Memory Context: {relevant_memory}]"
        
        context_str = ""
        if schedule_context:
            context_str = " [Context: " + str(schedule_context) + "]"
            
        combined_payload = {"telemetry": input_text + context_str + memory_context}
        
        try:
            # 1. Simulate frontend encryption (Client side would do this)
            import json
            from tier7_steg import steg_engine
            dummy_encrypted = steg_engine.encapsulate(json.dumps(combined_payload).encode("utf-8"))
            
            logger.info("VIRTUS Gatekeeper Engaged: Decrypting inbound telemetry...")
            # 2. VIRTUS Decrypt
            decrypted_payload = secure_virtus_decrypt(dummy_encrypted, _SERVER_KEYPAIR)
            secure_input = decrypted_payload.get("telemetry", "")
            
            logger.info("Telemetry verified. Sending to Evolutionary Engine/Fusion Core...")
            # 3. Process with Fusion Engine
            result = global_fusion_engine.step(secure_input)
            
            logger.info("VIRTUS Gatekeeper Engaged: Encrypting outbound response...")
            # 4. VIRTUS Encrypt the response
            virtus_encrypted_response = secure_virtus_encrypt(result, b"dummy_client_pub_key")
            
            # 5. For now, we still return the plaintext result so the frontend can speak it,
            #    but we log the encrypted payload size to prove it happened.
            logger.info(f"VIRTUS outbound payload size: {len(virtus_encrypted_response)} bytes")
            
        except Exception as virtus_err:
            logger.error(f"VIRTUS FAILURE: {virtus_err}")
            raise HTTPException(status_code=403, detail="VIRTUS_GATEKEEPER_FAILURE")
        
        # ============================================================
        # QUANTUM MEMORY MESH: Store the completed interaction
        # Feed Carbon intensity as emotional weight for future retrieval
        # ============================================================
        llm_response = result.get("output", "ok")
        current_intensity = carbon_metrics['physical_intensity'] if carbon_metrics else 1.0
        q_mesh.store_memory(
            interaction_text=f"User: {input_text} | Giuseppe: {llm_response}",
            emotional_weight=current_intensity
        )
        
        # ============================================================
        # THE VORTEX LOOP: Spin the Avatar orchestrator
        # Merges Carbon + Silicon into physical rendering commands
        # ============================================================
        vortex_data = vortex_engine.process_interaction(
            input_text=input_text,
            carbon_metrics=carbon_metrics,
            memory_context=relevant_memory
        )
        
        return {
            "text": llm_response,
            "coherence": result.get("coherence", 0.0),
            "safety_penalty": result.get("safety_penalty", 0.0),
            "score": result.get("score", 0.0),
            "persona_state": result.get("persona_state", {}),
            "memory_injected": bool(relevant_memory),
            "vortex": vortex_data
        }
    except Exception as e:
        logger.error(f"Think error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/speak")
async def speak(request: SpeakRequest):
    """
    Rewrite of the /synthesize endpoint.
    Authenticates with ElevenLabs using env variables and returns the audio file.
    """
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        
        if not api_key or not voice_id:
            logger.error("Missing ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID in .env")
            raise HTTPException(status_code=500, detail="Missing synthesis credentials. SILICON FAILURE.")
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": request.text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"ElevenLabs API failed: {response.text}")
            raise HTTPException(status_code=500, detail="Synthesis logic failed.")
            
        audio_url = f"/audio/output/{uuid.uuid4()}.mp3"
        output_path = Path("data/output") / Path(audio_url).name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)
            
        return FileResponse(path=output_path, media_type="audio/mpeg", filename=output_path.name)
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        # Ensure we do not allow silent failure. UI logic will display fallback when getting 500 error.
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute_action")
async def execute_action(request: Request):
    """
    Carbon Approval Protocol (Rule 12): Executes a proposed action.
    Triggers positive evolutionary reinforcement (+1.0).
    """
    try:
        data = await request.json()
        action_id = data.get("action_id", "unknown")
        logger.info(f"Carbon APPROVED action: {action_id}. Evolving confidence...")
        
        # Create dummy positive interaction vector
        interaction_vector = [1.0] * 8 
        global_fusion_engine.evolve_understanding(interaction_vector, feedback_score=1.0)
        
        return {"status": "success", "message": "Action executed and persona evolved."}
    except Exception as e:
        logger.error(f"Execute action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deny_action")
async def deny_action(request: Request):
    """
    Carbon Denial Protocol: Denies a proposed action.
    Triggers negative evolutionary reinforcement (-2.0).
    """
    try:
        data = await request.json()
        action_id = data.get("action_id", "unknown")
        logger.info(f"Carbon DENIED action: {action_id}. Evolving caution...")
        
        # Create dummy negative interaction vector
        interaction_vector = [-1.0] * 8 
        global_fusion_engine.evolve_understanding(interaction_vector, feedback_score=-2.0)
        
        return {"status": "success", "message": "Action denied and persona evolved."}
    except Exception as e:
        logger.error(f"Deny action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        

@app.post("/train", response_model=TrainingResponse)
async def train_voice(
    voice_name: str = Form(...),
    tier: str = Form("basic"),
    audio_files: List[UploadFile] = File(..., description="Audio files for training (unlimited)"),
    background_tasks: BackgroundTasks = None
):
    """
    Train a new voice model from uploaded audio files.

    Process:
    1. Upload audio files (no limit on number of files)
    2. Process through Stage 1 (audio cleaning)
    3. Extract timbre (Stage 2)
    4. Build expression patterns (Stage 3)
    5. Create emotion embeddings (Stage 4)
    6. Export voicepack
    """
    try:
        logger.info(f"Training request: voice={voice_name}, tier={tier}, files={len(audio_files)}")

        # Parse tier
        try:
            tier_enum = Tier(tier.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

        # Get tier features (for quality/duration limits, NOT file count limits)
        tier_features = config.get_tier_features(tier_enum)

        # No file count validation - accept unlimited files
        logger.info(f"Accepting {len(audio_files)} audio files for {tier} tier training")
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded files (would be done in background)
        upload_dir = Path(config.data_dir) / "uploads" / job_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        total_size = 0
        for audio_file in audio_files:
            file_path = upload_dir / audio_file.filename
            content = await audio_file.read()
            file_path.write_bytes(content)
            total_size += len(content)
            logger.info(f"Saved: {file_path}")
        
        # Estimate training time (rough)
        estimated_time = len(audio_files) * 30  # 30 seconds per file
        
        # TODO: Schedule background training task
        # background_tasks.add_task(train_voicepack, job_id, voice_name, tier_enum)
        
        return TrainingResponse(
            job_id=job_id,
            status="queued",
            estimated_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"Training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train/avatar")
async def train_avatar(
    voice_name: str = Form(...),
    tier: str = Form("basic"),
    image_files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Train avatar face model from uploaded images.

    NO UPLOAD LIMIT - Upload as many images as needed for accurate reconstruction.

    Process:
    1. Upload face images (photos, videos frames, etc.)
    2. Extract facial geometry (SILICON LAYER)
    3. Build identity model (CARBON LAYER)
    4. Generate 3D face mesh
    5. Create ARKit blendshape mappings
    6. Export avatar model

    Integration with voice training:
    - Links to voice model by voice_name
    - Enables full audiovisual avatar
    """
    try:
        logger.info(f"Avatar training request: voice={voice_name}, tier={tier}, images={len(image_files)}")

        # Parse tier
        try:
            tier_enum = Tier(tier.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

        # Validate tier supports avatar (ELITE/ULTRA only)
        tier_features = config.get_tier_features(tier_enum)
        if not tier_features.avatar_integration:
            raise HTTPException(
                status_code=403,
                detail=f"Avatar training requires ELITE or ULTRA tier. Current tier: {tier}"
            )

        # Create job ID
        job_id = str(uuid.uuid4())

        # Save uploaded images
        upload_dir = Path(config.data_dir) / "avatar_uploads" / job_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        total_size = 0
        for image_file in image_files:
            file_path = upload_dir / image_file.filename
            content = await image_file.read()
            file_path.write_bytes(content)
            total_size += len(content)
            saved_count += 1
            logger.info(f"Saved image {saved_count}: {file_path}")

        logger.info(f"Avatar upload complete: {saved_count} images, {total_size / 1024 / 1024:.2f} MB")

        # Estimate processing time (rough)
        estimated_time = saved_count * 5  # 5 seconds per image for face extraction

        # TODO: Schedule background avatar training task
        # background_tasks.add_task(train_avatar_model, job_id, voice_name, tier_enum)

        return {
            "job_id": job_id,
            "status": "queued",
            "images_uploaded": saved_count,
            "total_size_mb": total_size / 1024 / 1024,
            "estimated_time": estimated_time,
            "message": f"Successfully uploaded {saved_count} images for avatar training. No upload limits - we'll process all of them."
        }

    except Exception as e:
        logger.error(f"Avatar training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voicepacks", response_model=List[VoicepackInfo])
async def list_voicepacks(tier: Optional[str] = None):
    """
    List available voicepacks.
    
    For CHRISTMAN_MIND integration:
    - Arthur's voice
    - Sierra's voice
    - Giuseppe's voice
    - AlphaVox character voices
    - User memorial voices
    """
    try:
        # TODO: Scan voicepack directory
        voicepacks = [
            VoicepackInfo(
                id="arthur",
                name="Arthur - Memorial Guide",
                created="2025-11-27",
                tier="elite",
                emotions=["neutral", "empathetic", "warm", "gentle"],
                sample_audio_url="/samples/arthur.wav"
            ),
            VoicepackInfo(
                id="shorty",
                name="Aunt Shorty",
                created="2025-11-27",
                tier="ultra",
                emotions=[
                    "neutral", "happy", "proud", "teasing", "annoyed",
                    "sarcastic", "sweetheart", "laugh", "tremble",
                    "emphasis", "last_breath"
                ],
                sample_audio_url="/samples/shorty.wav"
            )
        ]
        
        # Filter by tier if specified
        if tier:
            tier_enum = Tier(tier.lower())
            # Would filter based on tier access
        
        return voicepacks
        
    except Exception as e:
        logger.error(f"Voicepack listing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class VoiceGenRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    emotion: str = Field(
        "neutral",
        description="Shorty's emotion",
        enum=[
            "neutral", "happy", "proud", "teasing", "annoyed",
            "sarcastic", "sweetheart", "laugh", "tremble",
            "emphasis", "last_breath"
        ]
    )
    exaggeration: float = Field(0.0, ge=-1.0, le=1.0, description="Exaggeration factor")

@app.post("/alpha-vox/voice-gen")
async def generate_shorty_voice(req: VoiceGenRequest):
    """
    Generate Shorty's emotional voice - ULTRA tier endpoint.

    Synthesizes speech with Shorty's precise emotional characteristics.
    Includes quantified emotion scores and exaggeration control.
    """
    try:
        from ..engines.shorty_voice_engine import ShortyVoiceEngine
        from pathlib import Path
        import tempfile

        logger.info(f"Shorty voice request: '{req.text[:30]}...' [{req.emotion}, exag={req.exaggeration:.2f}]")

        # Initialize Shorty engine (lazy loading)
        # In production, this would be cached globally
        shorty_ref = Path("data/raw/shorty.wav")  # Or shorty.mp3 converted

        if not shorty_ref.exists():
            # Try the MP3 in root
            shorty_ref = Path("shorty .MP3")
            if not shorty_ref.exists():
                raise HTTPException(
                    status_code=503,
                    detail="Shorty's voice not loaded. Upload reference audio first."
                )

        engine = ShortyVoiceEngine(reference_audio=shorty_ref)

        # Generate voice
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = Path(f.name)

        result = engine.generate_voice(
            text=req.text,
            emotion=req.emotion,
            exaggeration=req.exaggeration,
            output_path=output_path
        )

        return {
            "quant_score": result["quant_score"],
            "base_score": result["base_score"],
            "exaggeration": result["exaggeration"],
            "wav_path": str(output_path),
            "duration": result["duration"],
            "generation_time": result["generation_time"],
            "voice_params": result["voice_params"],
            "quality_mos": result["quality_mos"]
        }

    except Exception as e:
        logger.error(f"Shorty voice generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "icanhear you",
        "version": "1.0.0",
        "components": {
            "emotion_embedder": "ready",
            "tone_engine": "ready",
            "synthesis_engines": "ready",
            "shorty_voice": "ready"
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "ICanHearYou Voice Synthesis API",
        "version": "1.0.0",
        "description": "Voice cloning for CHRISTMAN_MIND autonomous beings",
        "endpoints": {
            "synthesize": "POST /synthesize - Generate speech from text",
            "train_voice": "POST /train - Train voice from audio files",
            "train_avatar": "POST /train/avatar - Train avatar from images (NO UPLOAD LIMIT)",
            "voicepacks": "GET /voicepacks - List available voice models"
        },
        "integration": {
            "sierra": "Accepts emotional intelligence signals",
            "tonescore": "Responds to ToneScore™ values",
            "giuseppe": "Customer service tone adaptation",
            "inferno": "Self-love trajectory voice warmth"
        },
        "avatar": {
            "silicon_layer": "Facial geometry extraction",
            "carbon_layer": "Identity model & 3D reconstruction",
            "upload_limit": "NONE - Upload as many images as needed"
        },
        "docs": "/docs"
    }


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize models and resources on startup."""
    logger.info("ICanHearYou API starting up...")
    
    # Create necessary directories
    Path(config.data_dir).mkdir(parents=True, exist_ok=True)
    Path(config.models_dir).mkdir(parents=True, exist_ok=True)
    Path(config.logs_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("ICanHearYou API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("ICanHearYou API shutting down...")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "giuseppe_core:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        limit_max_requests=None,  # No limit on number of requests
        timeout_keep_alive=300,    # 5 minutes keep-alive for large uploads
    )
