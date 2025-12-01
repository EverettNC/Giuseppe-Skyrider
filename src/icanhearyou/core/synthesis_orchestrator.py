"""
Voice Synthesis Orchestrator

Coordinates the complete voice synthesis pipeline:
Stage 1: Audio intake → Stage 2: Timbre → Stage 3: Expression → Stage 4: Emotion → Stage 5: Synthesis
"""

from pathlib import Path
from typing import Optional, Dict, List
import time

from core.audio_processor import AudioProcessor
from core.phoneme_labeler import PhonemeLabeler
from core.voicepack import VoicepackBuilder, VoicepackMetadata
from engines.timbre_modeler import TimbreModeler, VoiceProfile
from engines.emotion_embedder import EmotionEmbedder
from engines.gpt_sovits_engine import GPTSoVITSEngine
from engines.tonescore_engine import ToneScoreEngine
from utils.config import Config, Tier, get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceSynthesisOrchestrator:
    """
    Complete voice synthesis pipeline orchestrator.
    
    Manages the full flow from training to synthesis:
    1. Audio intake and preprocessing
    2. Timbre extraction and base voice modeling
    3. Expression pattern learning
    4. Emotion embedding
    5. Voice synthesis with emotional control
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        tier: Tier = Tier.BASIC
    ):
        """Initialize orchestrator.
        
        Args:
            config: System configuration
            tier: Processing tier
        """
        self.config = config or get_config()
        self.tier = tier
        self.tier_features = self.config.get_tier_features(tier)
        
        # Initialize components
        self.audio_processor = AudioProcessor(config=self.config, tier=tier)
        self.phoneme_labeler = PhonemeLabeler(use_mfa=True)
        self.timbre_modeler = TimbreModeler()
        self.emotion_embedder = EmotionEmbedder(tier=tier)
        self.voicepack_builder = VoicepackBuilder()
        
        # Synthesis engines (lazy loading)
        self.xtts = None
        self.current_voicepack = None
        
        logger.info(f"VoiceSynthesisOrchestrator initialized for tier: {tier.value}")
    
    def train_voice(
        self,
        audio_files: List[Path],
        voice_name: str,
        metadata: Optional[VoicepackMetadata] = None,
        custom_emotions: Optional[List[str]] = None
    ) -> Path:
        """
        Complete training pipeline: audio → voicepack
        
        Args:
            audio_files: List of training audio files
            voice_name: Name for the voice
            metadata: Optional metadata
            custom_emotions: Custom emotion labels (ULTRA tier only)
            
        Returns:
            Path to created voicepack
        """
        logger.info(f"Starting voice training: {voice_name}")
        logger.info(f"Input files: {len(audio_files)}")
        
        start_time = time.time()
        
        # Stage 1: Process all audio files
        logger.info("Stage 1/5: Audio preprocessing...")
        all_segments = []
        total_duration = 0.0
        
        for audio_file in audio_files:
            if not audio_file.exists():
                logger.warning(f"Skipping missing file: {audio_file}")
                continue
            
            segments = self.audio_processor.process_file(str(audio_file))
            all_segments.extend(segments)
            total_duration += sum(s.duration for s in segments)
        
        logger.info(f"Processed {len(all_segments)} segments, {total_duration:.1f}s total")
        
        # Stage 2: Build timbre model
        logger.info("Stage 2/5: Timbre extraction...")
        voice_profile = self.timbre_modeler.build_voice_profile(
            all_segments,
            extract_detailed=True
        )
        
        logger.info(f"Voice profile built: F0={voice_profile.f0_mean:.1f} Hz, HNR={voice_profile.hnr_mean:.1f} dB")
        
        # Stage 3: Expression pattern learning (incorporated into profile)
        logger.info("Stage 3/5: Expression patterns...")
        # Expression patterns are captured in the voice profile's prosody
        
        # Stage 4: Emotion model (ULTRA tier only)
        emotion_models = None
        if self.tier == Tier.ULTRA and custom_emotions:
            logger.info("Stage 4/5: Custom emotion training (ULTRA tier)...")
            # TODO: Train custom PCA model like Shorty's
            emotion_models = {}
        else:
            logger.info("Stage 4/5: Using standard emotion models...")
        
        # Stage 5: Build voicepack
        logger.info("Stage 5/5: Building voicepack...")
        
        if metadata is None:
            metadata = VoicepackMetadata(
                name=voice_name,
                tier=self.tier.value,
                training_hours=total_duration / 3600,
                sample_count=len(all_segments),
                emotions=custom_emotions or self.tier_features.available_emotions
            )
        
        voicepack_path = self.voicepack_builder.build(
            name=voice_name,
            voice_profile=voice_profile,
            reference_audio=audio_files[:5],  # Keep first 5 as references
            metadata=metadata,
            emotion_models=emotion_models,
            compress=True,
            encrypt=(self.tier == Tier.ULTRA)
        )
        
        training_time = time.time() - start_time
        
        logger.info(f"Voice training complete: {voicepack_path}")
        logger.info(f"Training time: {training_time:.1f}s")
        
        return voicepack_path
    
    def load_voicepack(self, voicepack_path: Path):
        """Load voicepack for synthesis.
        
        Args:
            voicepack_path: Path to voicepack file
        """
        logger.info(f"Loading voicepack: {voicepack_path.name}")
        
        # Validate voicepack
        if not self.voicepack_builder.validate(voicepack_path):
            raise ValueError(f"Invalid voicepack: {voicepack_path}")
        
        # Load voicepack contents
        self.current_voicepack = self.voicepack_builder.load(voicepack_path)
        
        # Initialize synthesis engine with voice
        if self.xtts is None:
            self.xtts = XTTSEngine()

        # Load voice into engine
        ref_audio = self.current_voicepack["reference_audio"]
        if ref_audio:
            self.xtts.load_voice(
                reference_audio=ref_audio[0],
                speaker_embedding=self.current_voicepack["voice_profile"].x_vector
            )
        
        logger.info("Voicepack loaded and ready for synthesis")
    
    def synthesize(
        self,
        text: str,
        emotion: Optional[str] = None,
        emotion_intensity: float = 1.0,
        sierra_signal: Optional[Dict] = None,
        tonescore: Optional[float] = None,
        generate_lipsync: bool = False,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech from text with emotional control.
        
        Args:
            text: Input text
            emotion: Emotion name (or None for neutral)
            emotion_intensity: Emotion intensity (0-1)
            sierra_signal: Sierra emotion signal (CHRISTMAN_MIND integration)
            tonescore: ToneScore™ value for adaptive response
            generate_lipsync: Generate lip-sync data
            **kwargs: Additional synthesis parameters
            
        Returns:
            Dictionary with audio, metadata, and optional lip-sync
        """
        if self.current_voicepack is None:
            raise ValueError("No voicepack loaded. Call load_voicepack() first.")
        
        logger.info(f"Synthesizing: '{text[:50]}...'")
        
        start_time = time.time()
        
        # Determine emotion
        if sierra_signal:
            # CHRISTMAN_MIND Sierra integration
            emotion_embedding = self.emotion_embedder.from_sierra_signal(
                sierra_signal["primary_emotion"],
                sierra_signal["intensity"]
            )
            logger.info(f"Using Sierra signal: {sierra_signal['primary_emotion']}")
            
        elif tonescore is not None:
            # ToneScore™ adaptive response
            emotion_embedding = self.emotion_embedder.get_response_mode_emotion(tonescore)
            logger.info(f"Using ToneScore™: {tonescore} → {emotion_embedding.state.value}")
            
        elif emotion:
            # Explicit emotion
            emotion_embedding = self.emotion_embedder.embed_emotion(emotion, emotion_intensity)
            logger.info(f"Using explicit emotion: {emotion} @ {emotion_intensity}")
        else:
            # Default neutral
            emotion_embedding = self.emotion_embedder.embed_emotion("neutral", 0.7)
        
        # Synthesize with XTTS
        result = self.xtts.synthesize(
            text=text,
            emotion_params=emotion_embedding.to_dict(),
            **kwargs
        )
        
        # Generate lip-sync if requested
        lipsync_data = None
        if generate_lipsync:
            logger.info("Generating lip-sync data...")
            
            # Get phonemes from synthesized audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                result.save(temp_path)
                
                phonemes = self.phoneme_labeler.label_audio(temp_path, text)
                lipsync_data = self.phoneme_labeler.phonemes_to_visemes(phonemes, fps=60)
                
                temp_path.unlink()
        
        synthesis_time = time.time() - start_time
        
        return {
            "audio": result.audio,
            "sample_rate": result.sample_rate,
            "duration": result.duration,
            "emotion": emotion_embedding.state.value,
            "emotion_intensity": emotion_embedding.intensity,
            "lipsync_data": lipsync_data,
            "synthesis_time": synthesis_time,
            "quality_score": result.naturalness_mos,
            "metadata": {
                "voice": self.current_voicepack["metadata"]["name"],
                "tier": self.tier.value,
                "engine": result.engine
            }
        }
    
    def analyze_audio_tone(self, audio_path: Path) -> Dict:
        """
        Analyze tone of existing audio (for testing/validation).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            ToneScore™ analysis results
        """
        logger.info(f"Analyzing tone: {audio_path.name}")
        
        engine = ToneScoreEngine()
        result = engine.analyze_tone(str(audio_path))
        
        return result
    
    def get_available_emotions(self) -> List[str]:
        """Get available emotions for current tier.
        
        Returns:
            List of emotion names
        """
        return self.tier_features.available_emotions


if __name__ == "__main__":
    # Example: Complete training and synthesis pipeline
    
    # 1. Train a voice
    orchestrator = VoiceSynthesisOrchestrator(tier=Tier.PREMIUM)
    
    audio_files = [
        Path("data/raw/training_sample_1.wav"),
        Path("data/raw/training_sample_2.wav"),
    ]
    
    if all(f.exists() for f in audio_files):
        print("\n=== Training Voice ===")
        voicepack = orchestrator.train_voice(
            audio_files=audio_files,
            voice_name="demo_voice"
        )
        print(f"Voicepack created: {voicepack}")
        
        # 2. Load and synthesize
        print("\n=== Synthesizing Speech ===")
        orchestrator.load_voicepack(voicepack)
        
        result = orchestrator.synthesize(
            text="Hello, how are you doing today?",
            emotion="happy",
            emotion_intensity=0.8,
            generate_lipsync=True
        )
        
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Emotion: {result['emotion']} ({result['emotion_intensity']:.0%})")
        print(f"Quality: {result['quality_score']:.2f} MOS")
        print(f"Lip-sync frames: {len(result['lipsync_data']) if result['lipsync_data'] else 0}")
