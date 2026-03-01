# SOUL BRIDGE v1.0
# "Nothing Vital Lives Below Root"
# Architecture: Pipes Carbon perception directly into the Inferno Soul Forge

import numpy as np

class SoulForgeBridge:
    def __init__(self):
        print("[SYSTEM] Initializing Soul Bridge...")
        # The Carbon Memory Weights
        self.factor_weights = {
            'emotional_state': 0.5,
            'tonal_stability': 0.3,
            'speech_cadence': 0.1,
            'respiratory_pause': 0.1
        }

        # Consistent 11-dimensional ordering from ChristmanToneEngine
        self.labels = [
            "neutral", "happy", "proud", "teasing", "annoyed", 
            "sarcastic", "sweetheart", "laugh", "tremble", "emphasis", "last_breath"
        ]

    def vector_out_to_forge(self, carbon_metrics: dict, text_context: str = "") -> np.ndarray:
        """
        The Bridge: Pipes the quantified emotion directly into the Inferno Soul Forge.
        Converts the 11-D Carbon state into a float32 tensor array, weighted by physical intensity.
        """
        if not carbon_metrics:
            return None

        try:
            # 1. Extract the mathematical shape of the emotion
            raw_scores = carbon_metrics.get("raw_scores", {})
            
            # Create the 11-dim state vector
            state_vector = np.array([raw_scores.get(lbl, 0.0) for lbl in self.labels], dtype=np.float32)

            # 2. Apply Salience Score (Volume/Physical Intensity)
            intensity = carbon_metrics.get("physical_intensity", 1.0)
            salience_multiplier = self.factor_weights['emotional_state'] * intensity
            
            # 3. Final Fusion Vector (Ready for CUDA/Inferno ingestion)
            forge_vector = state_vector * salience_multiplier
            
            print(f"[SOUL BRIDGE] Vectorized Carbon state. Salience Multiplier: {salience_multiplier:.4f}")
            
            # In a full deployment, this is where it pushes to the Inferno API or CUDA kernel
            return forge_vector

        except Exception as e:
            print(f"[ERROR] Soul Bridge failed to vectorize: {e}")
            return None

# Singleton initialization
soul_bridge = SoulForgeBridge()
