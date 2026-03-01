# FACS GRAPH & IDENTITY BINDING v1.0
# "Nothing Vital Lives Below Root"
# Architecture: Pure Neuro-Symbolic Reasoning Engine for Micro-expressions

class FACSGraph:
    def __init__(self):
        print("[SYSTEM] Initializing FACS Graph (ARKit 52 + Custom Ontology)...")
        # Base neutral state (Zero muscle activation)
        self.neutral_face = {
            "browInnerUp": 0.0, "browDownLeft": 0.0, "browDownRight": 0.0,
            "eyeBlinkLeft": 0.0, "eyeBlinkRight": 0.0, "eyeWideLeft": 0.0, "eyeWideRight": 0.0,
            "jawOpen": 0.0, "mouthSmileLeft": 0.0, "mouthSmileRight": 0.0,
            "mouthFrownLeft": 0.0, "mouthFrownRight": 0.0, "cheekPuff": 0.0
        }

    def calculate_microexpressions(self, dominant_state: str, intensity: float) -> dict:
        """
        Maps the quantified emotional state to physical muscle activations.
        Provides the exact coordinates for the React UI to physically render the Carbon state.
        """
        # Start from neutral
        facs = self.neutral_face.copy()
        
        # Scale intensity for muscle weight (clamped 0.0 - 1.0)
        w = min(max(intensity, 0.0), 1.0)

        # Symbolic mapping: Carbon Emotion -> Silicon Muscle Coordinate
        if dominant_state in ["happy", "proud"]:
            facs["mouthSmileLeft"] = 0.7 * w
            facs["mouthSmileRight"] = 0.7 * w
            facs["cheekPuff"] = 0.3 * w
        elif dominant_state == "sweetheart":
            # The "Holding Space" look: soft smile, compassionate eyes
            facs["mouthSmileLeft"] = 0.4 * w
            facs["mouthSmileRight"] = 0.4 * w
            facs["browInnerUp"] = 0.5 * w 
        elif dominant_state in ["annoyed", "sarcastic"]:
            facs["browDownLeft"] = 0.6 * w
            facs["browDownRight"] = 0.6 * w
            facs["mouthFrownLeft"] = 0.2 * w
        elif dominant_state in ["tremble", "last_breath"]:
            # Crisis State: Eyes locked and wide, brows up, full attention
            facs["eyeWideLeft"] = 0.8 * w
            facs["eyeWideRight"] = 0.8 * w
            facs["browInnerUp"] = 0.9 * w
            facs["jawOpen"] = 0.2 * w
        elif dominant_state == "emphasis":
            facs["browDownLeft"] = 0.4 * w
            facs["browDownRight"] = 0.4 * w
            facs["jawOpen"] = 0.4 * w

        return facs

# Singleton Orchestrator
facs_engine = FACSGraph()
