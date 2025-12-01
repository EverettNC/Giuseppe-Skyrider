# Christman AI Proprietary.
# The Christman Voice SDK, ToneScore, Adaptive Response Mode Engine,
# Hold-Space Mode, and Gentle-Lift Mode are proprietary to The Christman AI Project
# / Everett Christman. No redistribution, reverse engineering, or commercial use
# without written permission.

"""High-level voice synthesis SDK entrypoints."""

from pathlib import Path
from typing import Optional, Dict

from engines.base_synthesizer import SynthesisResult
from utils.config import Tier

try:
    from engines.shorty_voice_engine_v2 import ShortyVoiceEngine
except ImportError:  # pragma: no cover - fallback until Shorty engine lands
    from engines.gpt_sovits_engine import GPTSoVITSEngine as ShortyVoiceEngine

from . import response_api


class VoiceSDK:
    """Opinionated wrapper that wires tone intelligence into synthesis."""

    def __init__(self, tier: Tier = Tier.ULTRA):
        self.tier = tier
        self.engine = ShortyVoiceEngine()

    def load_voice(self, reference_audio: Path) -> None:
        """Load a reference clip to condition the engine on a speaker."""
        self.engine.load_voice(reference_audio)

    def synthesize(
        self,
        text: str,
        tone_score: Optional[float] = None,
        emotion_params: Optional[Dict] = None,
        **kwargs,
    ) -> SynthesisResult:
        """Render speech from text plus optional tone/response guidance."""
        if emotion_params is None and tone_score is not None:
            emotion = response_api.get_response_emotion(tone_score, tier=self.tier)
            if hasattr(emotion, "to_dict"):
                emotion_params = emotion.to_dict()
            else:
                emotion_params = emotion

        result: SynthesisResult = self.engine.synthesize(
            text=text,
            emotion_params=emotion_params,
            **kwargs,
        )
        return result
