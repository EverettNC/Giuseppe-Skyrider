"""
ToneScore™ Engine - Production Implementation
"Nothing Vital Lives Below Root" - Pure PyTorch/Apple Silicon Native
Multi-layer tone detection: raw audio → emotion → adaptive response
"""

import torchaudio
import torch
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

from logger import get_logger
logger = get_logger(__name__)

class ToneScoreEngine:
    """
    Hardware Native Tone Engine
    Replaces librosa/parselmouth dependency nightmare with direct PyTorch math.
    """
    def __init__(self, emotion_model: str = "superb/wav2vec2-base-superb-er", device: str = "auto"):
        logger.info("Initializing Native ToneScore™ engine...")
        
        if device == "auto":
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)
            
        logger.info(f"Tone Engine locked to hardware: {self.device}")
        
        try:
            self.wav2vec = Wav2Vec2ForSequenceClassification.from_pretrained(emotion_model)
            self.processor = Wav2Vec2Processor.from_pretrained(emotion_model)
            self.wav2vec.to(self.device)
            self.wav2vec.eval()
        except Exception as e:
            logger.warning(f"Failed to load emotion model: {e}")
            self.wav2vec = None
            
        self.emotion_labels = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
    
    def analyze_tone(self, audio_path: str) -> Dict:
        logger.info(f"Analyzing tone natively for: {audio_path}")
        
        # Load directly into tensors
        waveform, sr = torchaudio.load(audio_path)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
            
        # Layer 1: Native Physiological features
        pitch_freq = torchaudio.functional.detect_pitch_frequency(waveform, sr)
        pitch = pitch_freq[pitch_freq > 0].numpy()
        
        jitter = self._compute_jitter(pitch)
        shimmer = self._compute_shimmer(waveform)
        
        # Layer 2: VAD (Valence, Arousal, Dominance)
        arousal = self._compute_arousal(waveform, pitch, jitter)
        valence = self._compute_valence(waveform)
        dominance = self._compute_dominance(waveform, pitch)
        
        # Layer 3: Discrete emotions via HuggingFace MPS
        emotions = self._detect_emotions(waveform, sr)
        
        # Layer 4: ToneScore™ composite
        emotion_intensity = max(emotions.values()) * 100 if emotions else 0
        tone_score = (0.4 * arousal) + (0.35 * valence) + (0.25 * emotion_intensity)
        
        return {
            "arousal": int(arousal),
            "valence": int(valence),
            "dominance": int(dominance),
            "emotions": emotions,
            "emotion_intensity": int(emotion_intensity),
            "tone_score": int(tone_score),
            "interpretation": self._interpret_score(tone_score, emotions),
            "response_mode": self.adaptive_response_mode(tone_score),
            "physiological": {
                "pitch_mean": float(np.mean(pitch)) if len(pitch) > 0 else 0.0,
                "jitter": float(jitter),
                "shimmer": float(shimmer)
            }
        }
    
    def _compute_jitter(self, pitch: np.ndarray) -> float:
        """Calculate period-to-period instability"""
        if len(pitch) < 2: return 0.0
        periods = 1.0 / pitch
        period_diffs = np.abs(np.diff(periods))
        jitter = np.mean(period_diffs) / np.mean(periods)
        return min(1.0, float(jitter * 10))
        
    def _compute_shimmer(self, waveform: torch.Tensor) -> float:
        """Calculate amplitude instability"""
        frames = waveform.squeeze().unfold(0, 512, 256)
        amplitude = torch.sqrt(torch.mean(frames ** 2, dim=-1))
        if len(amplitude) < 2: return 0.0
        amp_diffs = torch.abs(torch.diff(amplitude))
        shimmer = torch.mean(amp_diffs) / torch.mean(amplitude)
        return min(1.0, float(shimmer * 5))
        
    def _compute_arousal(self, waveform: torch.Tensor, pitch: np.ndarray, jitter: float) -> float:
        energy = float(torch.mean(torch.sqrt(waveform ** 2)) * 100)
        pitch_score = min(100, (np.mean(pitch) / 250) * 100) if len(pitch) > 0 else 50
        jitter_score = jitter * 100
        arousal = (0.4 * energy) + (0.3 * pitch_score) + (0.3 * jitter_score)
        return min(100, max(0, float(arousal)))
        
    def _compute_valence(self, waveform: torch.Tensor) -> float:
        # Simplified native calculation (avoids complex spectral roll-offs without librosa)
        zcr = (waveform[:, 1:] * waveform[:, :-1] < 0).float().mean()
        smoothness = max(0, 100 - (float(zcr) * 1000))
        return min(100, max(0, smoothness))
        
    def _compute_dominance(self, waveform: torch.Tensor, pitch: np.ndarray) -> float:
        energy_score = float(torch.mean(torch.sqrt(waveform ** 2)) * 100)
        range_score = min(100, ((np.max(pitch) - np.min(pitch)) / 150) * 100) if len(pitch) > 0 else 50
        dominance = (0.6 * energy_score) + (0.4 * range_score)
        return min(100, max(0, float(dominance)))

    def _detect_emotions(self, waveform: torch.Tensor, sr: int) -> Dict[str, float]:
        if self.wav2vec is None:
            return {label: 0.14 for label in self.emotion_labels}
            
        try:
            if sr != 16000:
                waveform = torchaudio.functional.resample(waveform, sr, 16000)
                
            inputs = self.processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                logits = self.wav2vec(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
                
            return {label: float(probs[i]) if i < len(probs) else 0.0 for i, label in enumerate(self.emotion_labels)}
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return {label: 0.14 for label in self.emotion_labels}

    def _interpret_score(self, tone_score: float, emotions: Dict[str, float]) -> str:
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
        strength = emotions.get(dominant_emotion, 0.5)
        
        if tone_score > 80: state = "highly activated"
        elif tone_score > 60: state = "energized"
        elif tone_score > 40: state = "balanced"
        elif tone_score > 20: state = "subdued"
        else: state = "depleted"
        
        return f"{state}, showing {dominant_emotion} ({strength:.2%} confidence)"
        
    def adaptive_response_mode(self, tone_score: float) -> Dict:
        if tone_score > 75:
            return {"mode": "hold_space", "description": "High stress - create space", "cadence": "slower"}
        elif tone_score < 35:
            return {"mode": "gentle_lift", "description": "Low energy - provide gentle support", "timbre": "warmer"}
        else:
            return {"mode": "standard", "description": "Normal engagement", "adaptive": True}
