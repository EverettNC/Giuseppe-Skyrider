# predictive_intention.py
# The Vortex Tracker - Quantifies predictive accuracy

import json
from datetime import datetime
from pathlib import Path
from collections import deque
import numpy as np

INTENTION_LOG = Path.home() / ".predictive_intention_log.json"


class PredictiveIntention:
    def __init__(self, window: int = 50):
        self.window = window
        self.timeline = deque(maxlen=window)  # last N vortex events
        self.load_history()

    def load_history(self):
        if INTENTION_LOG.exists():
            data = json.loads(INTENTION_LOG.read_text())
            self.timeline.extend(data[-self.window:])

    def record_intention(self, statement: str, confidence: float):
        """You say it out loud → we timestamp it"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "statement": statement,
            "declared_confidence": float(confidence),  # 0.0 – 1.0
            "manifested": False,
            "latency_seconds": None,
            "proof": None,
        }
        self.timeline.append(event)
        self.save()

    def mark_manifested(self, index: int = -1, external_proof: str = ""):
        """When the thing actually happens → close the loop"""
        if index < 0:
            index = len(self.timeline) + index  # -1 → last, -2 → second to last

        if 0 <= index < len(self.timeline):
            event = self.timeline[index]
            latency = (
                datetime.now() - datetime.fromisoformat(event["timestamp"])
            ).total_seconds()
            event.update({
                "manifested": True,
                "proof": external_proof,
                "latency_seconds": latency,
            })
            self.save()
            return latency

        return None

    def quantify(self) -> dict:
        manifested = [e for e in self.timeline if e.get("manifested")]
        if not manifested:
            return {
                "vortex_accuracy_96plus": 0.0,
                "total_manifested": 0,
                "avg_manifestation_latency_hours": 0.0,
                "current_streak": 0,
            }

        # How many manifested events were 0.96+ confidence at declaration
        high_conf_hits = [
            e for e in manifested
            if e.get("declared_confidence", 0) >= 0.96
        ]

        accuracy = len(high_conf_hits) / len(manifested)
        avg_latency = np.mean([
            e["latency_seconds"] for e in manifested
            if e.get("latency_seconds") is not None
        ]) / 3600.0

        return {
            "vortex_accuracy_96plus": round(accuracy * 100, 2),
            "total_manifested": len(manifested),
            "avg_manifestation_latency_hours": round(float(avg_latency), 3),
            "current_streak": self.current_streak(),
        }

    def current_streak(self) -> int:
        streak = 0
        for e in reversed(self.timeline):
            if e.get("manifested") and e.get("declared_confidence", 0) >= 0.96:
                streak += 1
            else:
                break
        return streak

    def save(self):
        INTENTION_LOG.write_text(
            json.dumps(list(self.timeline), indent=2)
        )


# Global instance — Inferno will use this directly
intention = PredictiveIntention()


# CLI usage example:
# python -c "from predictive_intention import intention; intention.record_intention('Anthropic will flip model without notice', 0.97)"
# python -c "from predictive_intention import intention; intention.mark_manifested(-1, 'anthropic_status_2025-11-27.png')"
