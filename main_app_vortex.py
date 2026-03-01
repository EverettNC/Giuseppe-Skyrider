# MAIN APP VORTEX v1.0 (The Symbiotic Avatar Orchestrator)
# "Nothing Vital Lives Below Root"
# Architecture: The Vortex Loop (Intent -> Computation -> Interpretation -> New Intent)

import time
import torch
from facs_graph import facs_engine

class SymbioticAvatar:
    def __init__(self, user_id="ultra"):
        print(f"[VORTEX] INITIALIZING SYMBIOTIC AVATAR: {user_id}")
        self.user_id = user_id
        # Apple Silicon MPS acceleration
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.empathy_weight = 0.98 # High family system SYSTEM ALIGNED
        self.safety_rails = True
        
    def process_interaction(self, input_text: str, carbon_metrics: dict = None, memory_context: str = None):
        """
        The Vortex Loop: Merges Carbon (Hearing/Emotion) with Silicon (Logic/Memory).
        Generates the physical rendering commands for the frontend Avatar.
        """
        start_time = time.time()
        print("[VORTEX] SPINNING THE VORTEX LOOP...")

        # STEP 1: VECTOR OUT (The Emotional Manifold)
        dominant_state = "neutral"
        physical_intensity = 1.0
        if carbon_metrics:
            dominant_state = carbon_metrics.get("dominant_state", "neutral")
            physical_intensity = carbon_metrics.get("physical_intensity", 1.0)
        
        # STEP 2: REFLECTION (Visual State & FACS Prep)
        # Determines how the React UI should physically react
        eye_lock = True if physical_intensity > 0.6 else False
        # Calculate simulated breath frequency based on physical intensity
        breath_freq = 0.3 * (1.0 + physical_intensity) 
        
        # STEP 3: SPEAK (Prosody & Tone Directives)
        # Adjusts the TTS engine parameters based on the specific system alignments
        vocal_directive = "stoic"
        if dominant_state in ["tremble", "last_breath"]:
            vocal_directive = "Inferno: hold_space"
        elif dominant_state in ["sweetheart", "compassion"]:
            vocal_directive = "AlphaWolf: gentle"
        elif physical_intensity > 0.8:
            vocal_directive = "exaggerated"

        # Get the physical muscle coordinates based on the emotion and intensity
        muscle_coordinates = facs_engine.calculate_microexpressions(dominant_state, physical_intensity)

        # STEP 4: RENDER LOOP HANDOFF (Packaging for the UI)
        latency_ms = (time.time() - start_time) * 1000
        
        vortex_payload = {
            "avatar_state": {
                "emotion": dominant_state,
                "eye_lock": eye_lock,
                "breath_freq_hz": round(breath_freq, 2),
                "color_shift": "warm" if dominant_state in ["happy", "proud", "sweetheart"] else "cool",
                "facs_blendshapes": muscle_coordinates
            },
            "vocal_directive": vocal_directive,
            "vortex_latency_ms": round(latency_ms, 2)
        }
        
        print(f"[VORTEX] Loop Complete. Latency: {latency_ms:.2f}ms | State: {dominant_state.upper()}")
        return vortex_payload

# Singleton Orchestrator
vortex_engine = SymbioticAvatar()
