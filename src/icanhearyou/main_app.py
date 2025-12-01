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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config, Tier, get_config
from src.utils.logger import get_logger
from src.engines.emotion_embedder import EmotionEmbedder
from src.engines.tonescore_engine import ToneScoreEngine

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


# ============================================================================
# Request/Response Models
# ============================================================================

class SierraEmotionSignal(BaseModel):
    """Emotion signal from Sierra (CHRISTMAN_MIND Gen 1 agent)."""
    primary_emotion: str  # grief, trauma, healing, anger, neutral
    intensity: float = Field(ge=0.0, le=1.0)
    secondary_emotions: List[str] = []
    healing_stage: Optional[str] = None


class SynthesisRequest(BaseModel):
    """Request for voice synthesis."""
    text: str = Field(..., description="Text to synthesize")
    voicepack: str = Field(..., description="Voicepack identifier")
    
    # Emotion control (optional)
    emotion: Optional[str] = None
    emotion_intensity: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Sierra integration (optional)
    sierra_signal: Optional[SierraEmotionSignal] = None
    
    # ToneScore™ integration (optional)
    tonescore: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # Tier information
    tier: str = Field("basic", description="User tier: free, basic, premium, elite, ultra")
    
    # Avatar integration
    generate_lipsync: bool = Field(False, description="Generate lip-sync data for avatar")
    
    # Output format
    sample_rate: int = Field(16000, description="Output sample rate")
    format: str = Field("wav", description="Audio format: wav, mp3")


class SynthesisResponse(BaseModel):
    """Response from voice synthesis."""
    audio_url: str
    duration: float
    emotion_used: str
    emotion_intensity: float
    
    # Lip-sync data (if requested)
    lipsync_data: Optional[List[Dict]] = None
    
    # Metadata
    synthesis_time: float
    quality_score: Optional[float] = None
    tonescore: Optional[float] = None


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

@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    """
    Synthesize speech from text using specified voicepack.
    
    Integration with CHRISTMAN_MIND:
    - Accepts Sierra emotion signals
    - Responds to ToneScore™ values
    - Tier-aware processing
    """
    try:
        logger.info(f"Synthesis request: voicepack={request.voicepack}, tier={request.tier}")
        
        # Parse tier
        try:
            tier = Tier(request.tier.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")
        
        # Initialize emotion embedder for this tier
        embedder = EmotionEmbedder(tier=tier)
        
        # Determine emotion to use (priority order)
        if request.sierra_signal:
            # Sierra signal has highest priority (CHRISTMAN_MIND integration)
            emotion_embedding = embedder.from_sierra_signal(
                request.sierra_signal.primary_emotion,
                request.sierra_signal.intensity
            )
            logger.info(f"Using Sierra signal: {request.sierra_signal.primary_emotion} @ {request.sierra_signal.intensity}")
            
        elif request.tonescore is not None:
            # ToneScore™-based adaptive response
            emotion_embedding = embedder.get_response_mode_emotion(request.tonescore)
            logger.info(f"Using ToneScore™: {request.tonescore} → {emotion_embedding.state.value}")
            
        elif request.emotion:
            # Explicit emotion specified
            intensity = request.emotion_intensity or 1.0
            emotion_embedding = embedder.embed_emotion(request.emotion, intensity)
            logger.info(f"Using explicit emotion: {request.emotion} @ {intensity}")
            
        else:
            # Default to neutral
            emotion_embedding = embedder.embed_emotion("neutral", 0.7)
            logger.info("Using default neutral emotion")
        
        # TODO: Load voicepack and synthesize
        # For now, return placeholder response
        
        synthesis_start = datetime.now()
        
        # Placeholder: In production, this would call GPT-SoVITS/F5-TTS/StyleTTS2
        audio_url = f"/audio/output/{uuid.uuid4()}.wav"
        duration = 2.5  # seconds
        
        # Generate lip-sync data if requested
        lipsync_data = None
        if request.generate_lipsync:
            # Placeholder: Would generate ARKit blendshape weights @ 60fps
            lipsync_data = [
                {"time": 0.0, "viseme": "sil"},
                {"time": 0.1, "viseme": "aa"},
                # ... more frames
            ]
        
        synthesis_time = (datetime.now() - synthesis_start).total_seconds()
        
        return SynthesisResponse(
            audio_url=audio_url,
            duration=duration,
            emotion_used=emotion_embedding.state.value,
            emotion_intensity=emotion_embedding.intensity,
            lipsync_data=lipsync_data,
            synthesis_time=synthesis_time,
            quality_score=0.95,
            tonescore=request.tonescore
        )
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
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


@app.post("/alpha-vox/voice-gen")
async def generate_shorty_voice(
    text: str = Field(..., description="Text to synthesize"),
    emotion: str = Field(
        "neutral",
        description="Shorty's emotion",
        enum=[
            "neutral", "happy", "proud", "teasing", "annoyed",
            "sarcastic", "sweetheart", "laugh", "tremble",
            "emphasis", "last_breath"
        ]
    ),
    exaggeration: float = Field(0.0, ge=-1.0, le=1.0, description="Exaggeration factor")
):
    """
    Generate Shorty's emotional voice - ULTRA tier endpoint.

    Synthesizes speech with Shorty's precise emotional characteristics.
    Includes quantified emotion scores and exaggeration control.
    """
    try:
        from ..engines.shorty_voice_engine import ShortyVoiceEngine
        from pathlib import Path
        import tempfile

        logger.info(f"Shorty voice request: '{text[:30]}...' [{emotion}, exag={exaggeration:.2f}]")

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
            text=text,
            emotion=emotion,
            exaggeration=exaggeration,
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
            "tonescore_engine": "ready",
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
        "main_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        limit_max_requests=None,  # No limit on number of requests
        timeout_keep_alive=300,    # 5 minutes keep-alive for large uploads
    )
