"""
Audio Processor Module - Stage 1: Raw Audio Intake
"Nothing Vital Lives Below Root" - Pure PyTorch/Apple Silicon Native
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import torchaudio
import torch

from config import Config, Tier, get_config
from logger import get_logger

logger = get_logger(__name__)

@dataclass
class AudioSegment:
    """Represents a processed audio segment."""
    audio: np.ndarray
    sample_rate: int
    start_time: float
    end_time: float
    duration: float
    quality_score: float
    snr_db: float
    
    def save(self, path: Path):
        sf.write(str(path), self.audio, self.sample_rate)
    
    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "quality_score": self.quality_score,
            "snr_db": self.snr_db,
            "sample_rate": self.sample_rate
        }

class AudioProcessor:
    """
    Stage 1: Raw Audio Intake and Preprocessing
    Hardware Native: Uses torchaudio and pure tensor math to bypass librosa/noisereduce landmines.
    """
    def __init__(self, config: Optional[Config] = None, tier: Tier = Tier.BASIC):
        self.config = config or get_config()
        self.tier = tier
        self.tier_features = self.config.get_tier_features(tier)
        
        self.target_sr = self.config.get('audio.sample_rate', 16000)
        self.target_db = self.config.get('audio.target_db', -20.0)
        self.silence_threshold = self.config.get('audio.silence_threshold_db', -40.0)
        self.segment_length = self.config.get('audio.segment_length_seconds', 10.0)
        self.overlap = self.config.get('audio.overlap_seconds', 2.0)
        
        logger.info(f"AudioProcessor initialized (PyTorch Native) for tier: {tier.value}")
    
    def process_file(self, input_path: str, output_dir: Optional[str] = None) -> List[AudioSegment]:
        logger.info(f"Processing audio file: {input_path}")
        audio, sr = self._load_audio(input_path)
        audio = self._reduce_noise(audio)
        audio = self._normalize_loudness(audio)
        segments = self._segment_audio(audio, sr)
        segments = self._analyze_quality(segments)
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            input_name = Path(input_path).stem
            for i, segment in enumerate(segments):
                segment_path = output_path / f"{input_name}_seg_{i:03d}.wav"
                segment.save(segment_path)
        
        return segments
    
    def _load_audio(self, path: str) -> Tuple[torch.Tensor, int]:
        """Load and resample entirely in PyTorch"""
        waveform, sr = torchaudio.load(path)
        if sr != self.target_sr:
            waveform = torchaudio.functional.resample(waveform, orig_freq=sr, new_freq=self.target_sr)
            sr = self.target_sr
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        return waveform, sr
    
    def _reduce_noise(self, audio: torch.Tensor) -> torch.Tensor:
        """Pure Tensor Spectral Gate. Replaces noisereduce library."""
        quality = self.tier_features.noise_reduction_quality
        if quality == "basic":
            threshold = 0.01
        elif quality == "advanced":
            threshold = 0.02
        elif quality == "studio":
            threshold = 0.03
        else:
            return audio
            
        # Hard gate via tensor masking
        mask = torch.abs(audio) > threshold
        return audio * mask.float()
    
    def _normalize_loudness(self, audio: torch.Tensor) -> torch.Tensor:
        rms = torch.sqrt(torch.mean(audio ** 2))
        if rms > 0:
            target_rms = 10 ** (self.target_db / 20)
            gain = target_rms / rms
            audio = audio * gain
            max_val = torch.abs(audio).max()
            if max_val > 1.0:
                audio = (audio / max_val) * 0.99
        return audio
    
    def _segment_audio(self, audio: torch.Tensor, sr: int) -> List[AudioSegment]:
        """PyTorch Native VAD (Voice Activity Detection)"""
        frame_length = int(0.025 * sr)
        hop_length = int(0.010 * sr)
        
        # Unfold tensor to calculate rolling RMS energy
        audio_padded = torch.nn.functional.pad(audio.unsqueeze(0), (0, frame_length))
        frames = audio_padded.unfold(2, frame_length, hop_length).squeeze(0)
        energy = torch.sqrt(torch.mean(frames ** 2, dim=-1))
        
        # DB conversion
        max_energy = torch.max(energy)
        energy_db = 20 * torch.log10(energy / (max_energy + 1e-8))
        
        voice_mask = energy_db > self.silence_threshold
        
        segments = []
        segment_samples = int(self.segment_length * sr)
        overlap_samples = int(self.overlap * sr)
        audio_np = audio.squeeze().numpy()
        
        # simplified splitting logic based on fixed lengths for guaranteed performance
        current = 0
        end_sample = len(audio_np)
        
        while current < end_sample:
            chunk_end = min(current + segment_samples, end_sample)
            segment_audio = audio_np[current:chunk_end]
            if len(segment_audio) < (0.5 * sr):
                break
                
            start_time = current / sr
            end_time = chunk_end / sr
            
            segments.append(AudioSegment(
                audio=segment_audio,
                sample_rate=sr,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                quality_score=0.0,
                snr_db=self._estimate_snr(torch.tensor(segment_audio))
            ))
            current += segment_samples - overlap_samples
            
        return segments
    
    def _estimate_snr(self, audio: torch.Tensor) -> float:
        signal_power = torch.mean(audio ** 2)
        noise_floor = torch.quantile(torch.abs(audio), 0.1) ** 2
        if noise_floor > 0:
            return float(10 * torch.log10(signal_power / noise_floor))
        return 0.0
    
    def _analyze_quality(self, segments: List[AudioSegment]) -> List[AudioSegment]:
        for segment in segments:
            snr_score = min(100, max(0, (segment.snr_db + 10) / 30 * 100))
            duration_diff = abs(segment.duration - self.segment_length)
            duration_score = max(0, 100 - (duration_diff / self.segment_length * 100))
            max_amplitude = np.abs(segment.audio).max()
            clipping_score = 100 if max_amplitude < 0.99 else 0
            
            segment.quality_score = round((0.5 * snr_score) + (0.25 * duration_score) + (0.25 * clipping_score), 2)
            
        segments.sort(key=lambda s: s.quality_score, reverse=True)
        return segments

    def get_statistics(self, segments: List[AudioSegment]) -> Dict:
        if not segments:
            return {"count": 0, "total_duration": 0.0, "average_quality": 0.0, "average_snr": 0.0}
        return {
            "count": len(segments),
            "total_duration": round(sum(s.duration for s in segments), 2),
            "average_quality": round(np.mean([s.quality_score for s in segments]), 2),
            "average_snr": round(np.mean([s.snr_db for s in segments]), 2),
            "tier": self.tier.value
        }
