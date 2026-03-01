# LUCAS MODULE v1.0 (The Architecture of Lived Truth)
# "Nothing Vital Lives Below Root"
# Architecture: Salience Regulator & Long-Term Potentiation (LTP) Kernel

class LucasModule:
    def __init__(self):
        print("[SYSTEM] Initializing Lucas Module (Salience Regulator)...")
        # "LC wake" multiplier (metaphor for readiness / noradrenergic tone)
        self.ltp_boost = 1.15 
        # Minimum threshold required to allow decay of trauma
        self.decay_threshold = 0.3 

    def calculate_salience(self, physical_intensity: float, dominant_state: str) -> float:
        """
        Determines the 'Lived Truth' impact weight of a memory before it enters the Quantum Mesh.
        Pain and high-amplitude states form persistent anchors.
        """
        base_weight = physical_intensity

        # High-impact states force immediate, persistent consolidation (Impact > Permission)
        if dominant_state in ["tremble", "last_breath", "emphasis"]:
            base_weight *= (self.ltp_boost * 2.0)
            print(f"[LUCAS] High-impact anchor formed. Salience amplified to: {base_weight:.2f}")
            
        # Aggressive/Annoyed states get a moderate boost
        elif dominant_state in ["annoyed", "sarcastic"]:
            base_weight *= self.ltp_boost
            
        # Safe states allow for standard integration
        elif dominant_state in ["sweetheart", "happy", "proud"]:
            base_weight *= 1.0 
            
        return base_weight

    def apply_safety_decay(self, current_trauma_weight: float, consecutive_safety_signals: int) -> float:
        """
        If continuous safety is proven over time, trauma associations gently decay.
        """
        if consecutive_safety_signals > 5:
            decayed_weight = current_trauma_weight - 0.08
            return max(decayed_weight, self.decay_threshold)
        return current_trauma_weight

# Singleton Orchestrator
lucas_engine = LucasModule()
