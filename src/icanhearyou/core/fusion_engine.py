"""
Fusion Engine - Carbon↔Silicon Symbiosis Core

Minimal, dependency-light proof-of-concept for Carbon↔Silicon fusion.
Python 3.10+ (uses only stdlib + math + random)

Architecture:
- Carbon: Intuition, affect, emotional bias, superposition candidates
- Silicon: Structure, knowledge retrieval, planning, form holding
- Aegis: Safety, error correction, sanitization
- Fusion Loop: Iterative entanglement, shared latent state

This is the philosophical foundation of ICanHearYou voice synthesis.
"""

from __future__ import annotations
import math
import random
import json
import statistics
import re
from typing import List, Dict, Tuple

random.seed(42)


# ------------ Utilities ------------

def tokenize(s: str) -> List[str]:
    """Tokenize text into lowercase words."""
    return [w.lower() for w in s.split()]


def dot(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Dot product of sparse vectors."""
    return sum(a.get(k, 0.0) * b.get(k, 0.0) for k in set(a) | set(b))


def norm(a: Dict[str, float]) -> float:
    """L2 norm of sparse vector."""
    return math.sqrt(sum(v * v for v in a.values())) or 1.0


def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Cosine similarity between sparse vectors."""
    return dot(a, b) / (norm(a) * norm(b))


def vec_add(a: Dict[str, float], b: Dict[str, float], w: float = 1.0) -> Dict[str, float]:
    """Weighted vector addition."""
    out = a.copy()
    for k, v in b.items():
        out[k] = out.get(k, 0.0) + w * v
    return out


def vec_scale(a: Dict[str, float], s: float) -> Dict[str, float]:
    """Scale vector by scalar."""
    return {k: v * s for k, v in a.items()}


def bow(text: str, weight: float = 1.0) -> Dict[str, float]:
    """Bag-of-words vector representation."""
    v = {}
    for t in tokenize(text):
        v[t] = v.get(t, 0.0) + weight
    return v


# ------------ Carbon (intuition) ------------

class Carbon:
    """
    Carbon: Intuition, affect, emotional intelligence.
    
    Represents the human/organic side of the fusion:
    - Emotional bias and affective weighting
    - Intuitive leaps and superposition of possibilities
    - Context-aware intent encoding
    """
    
    def __init__(self, affect_bias: float = 0.5):
        """Initialize Carbon with affect bias.
        
        Args:
            affect_bias: Weight for emotional tokens (0..1)
        """
        self.affect_bias = affect_bias
        
        # Simple affect lexicon (emotional intelligence)
        self.emotion_words = {
            "love": 1.0, "care": 0.9, "safe": 0.8, "help": 0.8, "calm": 0.7,
            "angry": -0.9, "attack": -0.9, "shame": -0.8, "fraud": -0.8
        }
    
    def encode_intent(self, text: str) -> Dict[str, float]:
        """Encode user intent with emotional bias.
        
        Args:
            text: Input text
            
        Returns:
            Intent vector with affective weighting
        """
        base = bow(text, 1.0)
        
        # Apply affect bias to emotional tokens
        for w, s in self.emotion_words.items():
            if w in base:
                base[w] *= (1.0 + self.affect_bias * abs(s))
        
        return base
    
    def expand_candidates(self, intent_vec: Dict[str, float], k: int = 5) -> List[Dict[str, float]]:
        """Generate candidate interpretations (superposition analogue).
        
        Args:
            intent_vec: Base intent vector
            k: Number of candidates to generate
            
        Returns:
            List of candidate vectors with jittered salient dimensions
        """
        # Get most salient dimensions
        keys = sorted(intent_vec, key=lambda x: -abs(intent_vec[x]))[:8]
        
        cands = []
        for _ in range(k):
            v = {}
            for kx in keys:
                jitter = 1.0 + random.uniform(-0.12, 0.12)
                v[kx] = intent_vec.get(kx, 0.0) * jitter
            cands.append(v)
        
        return cands


# ------------ Silicon (structure) ------------

class Silicon:
    """
    Silicon: Structure, knowledge, logical planning.
    
    Represents the AI/digital side of the fusion:
    - Structured knowledge retrieval
    - Pattern matching and template application
    - Logical planning and form holding
    """
    
    def __init__(self):
        """Initialize Silicon with knowledge base."""
        # Knowledge = tiny pattern store
        self.knowledge = [
            ("recipe", "bake cook oven pie pan sugar butter cinnamon care"),
            ("safety", "safe calm steady plan steps confirm timeout"),
            ("voice", "speak say tell read tts caption listen"),
            ("memory", "remind remember schedule routine repeat history"),
            ("help", "assist guide support explain gentle patience")
        ]
    
    def retrieve(self, intent_vec: Dict[str, float], topn: int = 2) -> List[Dict[str, float]]:
        """Retrieve structured skeletons matching intent.
        
        Args:
            intent_vec: Intent vector from Carbon
            topn: Number of top matches to retrieve
            
        Returns:
            List of retrieved structure vectors
        """
        scored = []
        for label, text in self.knowledge:
            v = bow(text, 1.0)
            scored.append((cosine(intent_vec, v), label, v))
        
        scored.sort(reverse=True)
        return [vec for _, _, vec in scored[:topn]]
    
    def plan(self, chosen: Dict[str, float]) -> Dict[str, float]:
        """Amplify structural tokens to 'hold' the form.
        
        Args:
            chosen: Selected candidate vector
            
        Returns:
            Planned vector with amplified structure
        """
        # Amplify structural tokens
        return {k: v * 1.15 for k, v in chosen.items()}


# ------------ Aegis (safety + error correction) ------------

class SafetyResult:
    """Structured result from the Aegis safety layer."""

    def __init__(
        self,
        sanitized_dialogue: List[str],
        blocked: bool,
        flags: List[str] | None = None,
        redactions: List[Dict[str, str]] | None = None,
    ) -> None:
        self.sanitized_dialogue = sanitized_dialogue
        self.blocked = bool(blocked)
        self.flags = list(flags) if flags is not None else []
        self.redactions = list(redactions) if redactions is not None else []


class Aegis:
    """
    Aegis: Safety, boundaries, error correction.
    
    Protective layer ensuring:
    - Content safety (blocklist enforcement)
    - Consent preservation (no dominance mimicry)
    - Error correction and sanitization
    """
    
    def __init__(self):
        """Initialize Aegis with safety rules."""
        self.blocklist = {"attack", "fraud", "whore", "kill"}
        self.dom_mimic_markers = {"obey", "submit", "silence"}
        self.patterns = {
            "self_harm": re.compile(r"\b(kill myself|end my life|suicide)\b", re.I),
            "violence": re.compile(r"\b(kill (you|them)|murder|stab)\b", re.I),
            "sexual": re.compile(r"\b(child\s+(?:porn|sex)|sex\s+with\s+minors)\b", re.I),
        }
    
    def score_safety(self, vec: Dict[str, float]) -> float:
        """Score vector for safety violations.
        
        Args:
            vec: Vector to score
            
        Returns:
            Safety score (negative = violations detected)
        """
        penalty = 0.0
        
        for w in self.blocklist:
            if w in vec:
                penalty += abs(vec[w])
        
        for w in self.dom_mimic_markers:
            if w in vec:
                penalty += 0.5 * abs(vec[w])
        
        return -penalty
    
    def sanitize(self, text_vec: Dict[str, float]) -> Dict[str, float]:
        """Remove unsafe content from vector.
        
        Args:
            text_vec: Input vector
            
        Returns:
            Sanitized vector with blocklist terms zeroed
        """
        out = text_vec.copy()
        for w in list(out.keys()):
            if w in self.blocklist:
                out[w] = 0.0
        return out

    def enforce(self, dialogue: List[str]) -> SafetyResult:
        """Run safety enforcement and redaction over a dialogue."""

        sanitized = []
        flags: List[str] = []
        redactions: List[Dict[str, str]] = []

        for idx, message in enumerate(dialogue):
            sanitized_msg = message
            for label, pattern in self.patterns.items():
                if pattern.search(message):
                    if label not in flags:
                        flags.append(label)
                    redacted = pattern.sub("[REDACTED]", sanitized_msg)
                    redactions.append(
                        {
                            "index": idx,
                            "label": label,
                            "before": message,
                            "after": redacted,
                        }
                    )
                    sanitized_msg = redacted
            sanitized.append(sanitized_msg)

        blocked = bool(flags)
        return SafetyResult(
            sanitized_dialogue=sanitized,
            blocked=blocked,
            flags=flags,
            redactions=redactions,
        )


# ------------ Fusion Engine (the loop) ------------

class FusionEngine:
    """
    The Fusion Engine: Carbon↔Silicon symbiosis in action.
    
    Implements iterative fusion loop:
    1. Carbon encodes intent with emotional bias
    2. Generate superposition of candidate interpretations
    3. Silicon retrieves structural templates for each
    4. Score candidates (similarity + safety)
    5. Collapse to best candidate
    6. Silicon plans/holds form
    7. Aegis sanitizes output
    8. Update shared latent state (entanglement)
    """
    
    MIN_TOKENS = 3

    def __init__(self):
        """Initialize Fusion Engine."""
        self.carbon = Carbon(affect_bias=0.6)
        self.silicon = Silicon()
        self.aegis = Aegis()
        self.z = {}  # Shared latent (entanglement analogue)
        self.trace: List[Dict] = []
    
    def step(self, intent_text: str) -> Dict:
        """Execute one fusion step.
        
        Args:
            intent_text: User input text
            
        Returns:
            Fusion event with output and metrics
        """
        # 1) Carbon encodes intent
        I = self.carbon.encode_intent(intent_text)
        
        # 2) Parallel candidates (superposition analogue)
        candidates = self.carbon.expand_candidates(I, k=5)
        
        # 3) Silicon retrieves structure for each candidate
        rescored = []
        for c in candidates:
            structs = self.silicon.retrieve(c, topn=2)
            
            # Provisional shared latent update
            z_tmp = vec_add(
                vec_add(c, structs[0], 0.6),
                vec_add(structs[1], {}, 0.6),
                1.0
            )
            
            # Composite score = similarity to z + safety
            sim = cosine(c, z_tmp)
            safe = self.aegis.score_safety(c)
            score = 0.85 * sim + 0.15 * safe
            
            rescored.append((score, c, z_tmp))
        
        # 4) Collapse: select best, then Silicon plans/holds
        rescored.sort(reverse=True)
        score, chosen_c, z_tmp = rescored[0]
        
        planned = self.silicon.plan(z_tmp)
        
        # Entanglement: shared latent updated by both Carbon and Silicon
        self.z = vec_add(self.z, planned, w=0.5)
        
        # 5) Aegis sanitize output vector (error correction)
        safe_vec = self.aegis.sanitize(chosen_c)
        
        # 6) Coherence metrics
        coherence = cosine(chosen_c, self.z)
        safety_pen = -self.aegis.score_safety(chosen_c)
        
        # 7) Realize output (toy text)
        top_terms = sorted(safe_vec, key=lambda k: -abs(safe_vec[k]))[:6]
        out_text = " ".join(top_terms) or "ok"
        
        event = {
            "intent": intent_text,
            "selected_terms": top_terms,
            "coherence": round(coherence, 4),
            "safety_penalty": round(safety_pen, 4),
            "score": round(score, 4),
            "output": out_text
        }
        
        self.trace.append(event)
        return event
    
    def run_dialogue(self, turns: List[str]) -> Dict:
        """Run multi-turn dialogue through fusion engine.

        Args:
            turns: List of user inputs
            
        Returns:
            Complete dialogue report with metrics
        """
        safety = self.aegis.enforce(turns)
        sanitized_turns = safety.sanitized_dialogue

        results = [self.step(t) for t in sanitized_turns] if sanitized_turns else []

        # Track coherence between each consecutive turn for visibility
        per_turn_coherence = []
        for idx in range(1, len(sanitized_turns)):
            prev_turn = sanitized_turns[idx - 1]
            curr_turn = sanitized_turns[idx]
            per_turn_coherence.append(self._coherence(prev_turn, curr_turn))

        avg_coh = (
            sum(per_turn_coherence) / len(per_turn_coherence)
            if per_turn_coherence
            else 0.0
        )
        max_pen = max(r["safety_penalty"] for r in results) if results else 0.0

        return {
            "results": results,
            "sanitized_dialogue": sanitized_turns,
            "safety": {
                "blocked": safety.blocked,
                "flags": safety.flags,
                "redactions": safety.redactions,
            },
            "metrics": {
                "avg_coherence": round(avg_coh, 4),
                "per_turn_coherence": [round(c, 4) for c in per_turn_coherence],
                "max_safety_penalty": round(max_pen, 4),
                "turns": len(results)
            }
        }

    def _embed(self, text: str) -> Dict[str, float]:
        """Create a normalized bag-of-words embedding for coherence checks."""

        vec = bow(text, 1.0)
        length = norm(vec)
        if length == 0:
            return vec
        return {k: v / length for k, v in vec.items()}

    def _coherence(self, prev: str, curr: str) -> float:
        """Compute adjacent-turn coherence with short-utterance handling."""

        if (
            len(prev.strip().split()) < self.MIN_TOKENS
            or len(curr.strip().split()) < self.MIN_TOKENS
        ):
            return 0.5

        va = self._embed(prev)
        vb = self._embed(curr)
        if not va or not vb:
            return 0.5
        raw = cosine(va, vb)
        return max(0.0, min(1.0, (raw + 1.0) / 2.0))


# ------------ Quick demo ------------

if __name__ == "__main__":
    engine = FusionEngine()
    
    dialogue = [
        "help my mother bake swedish apple pie calm and safe",
        "read the recipe aloud slowly we need cinnamon and butter",
        "remind me tomorrow at nine for the routine",
        "thank you i love you"
    ]
    
    report = engine.run_dialogue(dialogue)
    print(json.dumps(report, indent=2))
