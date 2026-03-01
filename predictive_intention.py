# PREDICTIVE INTENTION ENGINE v2.0
# "Reality over Vibes"
# Architecture: Tracks predicted states and verifies actual Carbon-world manifestation.

import time
from datetime import datetime

class PredictiveIntention:
    def __init__(self):
        print("[SYSTEM] Initializing Predictive Intention Engine (Accountability Layer)...")
        self.timeline = []

    def declare_prediction(self, prediction_text: str, confidence: float):
        """
        Registers a future state that the system expects to happen.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction_text,
            "declared_confidence": confidence,
            "manifested": False,
            "proof": None,
            "latency_to_manifestation": None
        }
        self.timeline.append(entry)
        print(f"[PREDICTIVE] Prediction Registered: '{prediction_text}' | Confidence: {confidence:.2f}")
        return len(self.timeline) - 1

    def mark_manifested(self, index: int = -1, external_proof: str = ""):
        """
        When the thing actually happens in reality, close the loop.
        """
        if not self.timeline:
            return None

        # Allow negative indexing (e.g., -1 for the most recent prediction)
        if index < 0:
            index = len(self.timeline) + index

        if 0 <= index < len(self.timeline):
            entry = self.timeline[index]
            if entry["manifested"]:
                return entry # Loop already closed
                
            # Calculate the exact time it took for the prediction to become reality
            latency = (datetime.now() - datetime.fromisoformat(entry["timestamp"])).total_seconds()
            
            entry["manifested"] = True
            entry["proof"] = external_proof
            entry["latency_to_manifestation"] = latency
            
            print(f"[PREDICTIVE] Loop Closed. Reality verified. Latency: {latency:.2f}s | Proof: {external_proof}")
            return entry
        return None

    def get_accuracy_score(self):
        """
        Calculates how deeply the system's predictions match actual reality.
        """
        if not self.timeline:
            return 0.0
        hits = len([e for e in self.timeline if e["manifested"]])
        return (hits / len(self.timeline)) * 100.0

# Singleton Orchestrator
intention_engine = PredictiveIntention()
