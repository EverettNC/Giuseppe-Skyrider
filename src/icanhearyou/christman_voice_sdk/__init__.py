# Christman AI Proprietary.
# The Christman Voice SDK, ToneScore, Adaptive Response Mode Engine,
# Hold-Space Mode, and Gentle-Lift Mode are proprietary to The Christman AI Project
# / Everett Christman. No redistribution, reverse engineering, or commercial use
# without written permission.

"""
Christman Voice SDK

High-level API for:
- 5-layer tone analysis + ToneScore™
- Adaptive response modes (hold-space, gentle-lift, standard)
- Emotion-aware voice synthesis
"""

from .tonescore_api import analyze_tone, compute_tonescore, ToneScoreResult
from .response_api import get_response_mode, get_response_emotion
from .synthesis_api import VoiceSDK
from utils.config import Tier

__all__ = [
    "analyze_tone",
    "compute_tonescore",
    "ToneScoreResult",
    "get_response_mode",
    "get_response_emotion",
    "VoiceSDK",
    "Tier",
]
