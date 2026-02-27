# Christman AI Proprietary.
# The Christman Voice SDK, ToneScore, Adaptive Response Mode Engine,
# Hold-Space Mode, and Gentle-Lift Mode are proprietary to The Christman AI Project
# / Everett Christman. No redistribution, reverse engineering, or commercial use
# without written permission.

"""ToneScore and tone analysis SDK API."""

from dataclasses import dataclass
from typing import Dict

from tone_analyzer import MultiLayerToneAnalyzer, ToneScoreCalculator


@dataclass
class ToneScoreResult:
    """Convenience container for ToneScore-related outputs."""
    score: float
    arousal: float
    valence: float
    intensity: float
    response_mode: Dict
    raw_layers: Dict


def analyze_tone(audio_path: str) -> Dict:
    """Run complete MultiLayerToneAnalyzer on an audio file."""
    analyzer = MultiLayerToneAnalyzer()
    result = analyzer.analyze_complete(audio_path)
    return result


def compute_tonescore(audio_path: str) -> ToneScoreResult:
    """Run full analysis and extract ToneScore plus emotion metrics."""
    analyzer = MultiLayerToneAnalyzer()
    result = analyzer.analyze_complete(audio_path)

    ts = result["layer_5_tonescore"]
    score = ts.get("score")
    if score is None:
        score = ToneScoreCalculator.calculate(
            arousal=ts["arousal"],
            valence=ts["valence"],
            emotion_intensity=ts["intensity"],
        )
    return ToneScoreResult(
        score=score,
        arousal=ts["arousal"],
        valence=ts["valence"],
        intensity=ts["intensity"],
        response_mode=ts["response_mode"],
        raw_layers=result,
    )
