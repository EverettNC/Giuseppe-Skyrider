# CHRISTMAN EMOTION & TONESCORE ENGINE v2.1 (SOVEREIGN EDITION)
# "Nothing Vital Lives Below Root" - Purged Librosa/LLVM dependencies.
# Architecture: soundfile + scipy + torch (Native Intel-Metal Bridge)

import torch
import numpy as np
import soundfile as sf
from scipy import signal
import hashlib
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification

class ChristmanToneEngine:
    def __init__(self, model_name="superb/wav2vec2-base-superb-er"):
        print(f"[SYSTEM] Initializing Sovereign Tone Engine: {model_name}")
        self.processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        
        # Hardware acceleration for macOS (Metal/MPS)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model.to(self.device)

        self.EMOTION_LABELS = [
            "neutral", "happy", "proud", "teasing", "annoyed", 
            "sarcastic", "sweetheart", "laugh", "tremble", "emphasis", "last_breath"
        ]

    def analyze_audio(self, wav_path: str) -> dict:
        try:
            # 1. Load Audio (Sovereign Method: Soundfile)
            data, sr = sf.read(wav_path)
            
            # Mix stereo to mono
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            # 2. Resample to 16kHz manually if needed (Reality over Library)
            if sr != 16000:
                num_samples = int(len(data) * 16000 / sr)
                data = signal.resample(data, num_samples)
                sr = 16000

            # 3. Physiological T1 Layer (Root Intensity Math)
            # RMS = Square root of the mean of the squares. No librosa needed.
            rms_energy = np.sqrt(np.mean(data**2))
            intensity_norm = np.clip(rms_energy * 400, 0, 1)

            # 4. Neural Paralinguistics T2 Layer
            input_values = self.processor(data, sampling_rate=sr, return_tensors="pt", padding=True).input_values
            input_values = input_values.to(self.device)

            with torch.no_grad():
                logits = self.model(input_values).logits
                probabilities = torch.softmax(logits, dim=-1)[0].cpu().numpy()

            emotion_scores = {
                self.EMOTION_LABELS[i] if i < len(self.EMOTION_LABELS) else f"unknown_{i}": round(float(p), 4)
                for i, p in enumerate(probabilities)
            }

            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            cadence_hash = hashlib.sha1(data.tobytes()).hexdigest()[:16]

            # 5. Actionable Routing Logic
            action_state = "NORMAL"
            if dominant_emotion in ["tremble", "last_breath"] or intensity_norm > 0.85:
                action_state = "HOLD_SPACE" 

            return {
                "modality": "audio",
                "dominant_state": dominant_emotion,
                "action_state": action_state,
                "physical_intensity": float(intensity_norm),
                "cadence_fingerprint": cadence_hash,
                "raw_scores": emotion_scores
            }

        except Exception as e:
            print(f"[ERROR] Sovereign ToneScore failed: {e}")
            return None

if __name__ == "__main__":
    engine = ChristmanToneEngine()
    # print(engine.analyze_audio("test.wav"))
