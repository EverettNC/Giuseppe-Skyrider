# Christman AI Proprietary.
# The Christman Voice SDK, ToneScore, Adaptive Response Mode Engine,
# Hold-Space Mode, and Gentle-Lift Mode are proprietary to The Christman AI Project
# / Everett Christman. No redistribution, reverse engineering, or commercial use
# without written permission.

"""Adaptive response and emotion selection APIs."""

from typing import Dict

from core.tone_analyzer import ToneScoreCalculator
from engines.emotion_embedder import EmotionEmbedder
from utils.config import Tier


def get_response_mode(tone_score: float) -> Dict:
    """Return ToneScoreCalculator's recommended response mode."""
    return ToneScoreCalculator.get_response_mode(tone_score)


def get_response_emotion(tone_score: float, tier: Tier = Tier.ULTRA) -> Dict:
    """Derive synthesis-ready emotion parameters for a ToneScore."""
    embedder = EmotionEmbedder(tier=tier)
    embedding = embedder.get_response_mode_emotion(tone_score)
    return embedding.to_dict()
