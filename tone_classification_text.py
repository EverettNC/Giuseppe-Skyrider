# TEXT TONE CLASSIFIER v1.0
# "Reality over Vibes"
# Architecture: Distinguishes aggressive/attacking text from incisive/passionate text.

class TextToneClassifier:
    def __init__(self):
        print("[SYSTEM] Initializing Text Tone Classifier...")
        # Base list for the 'profanity_machine_gun' metric
        self.profanity_list = ["fuck", "shit", "bitch", "damn", "ass"] 
        
    def analyze_syntax(self, text: str) -> dict:
        """
        Analyzes the raw mechanics of the text string. No LLM guessing.
        Measures exactly how the user is hitting the keyboard.
        """
        words = text.split()
        if not words:
            return {"action_state": "NORMAL", "physical_intensity": 1.0, "dominant_state": "neutral"}

        # 1. Measure All-Caps (Screaming vs Emphasis)
        all_caps_words = len([w for w in words if w.isupper() and len(w) > 1])
        caps_ratio = all_caps_words / len(words)

        # 2. Measure Punctuation Density (Panic/Aggression/Urgency)
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        # 3. Profanity Machine Gun metric
        profanity_count = sum(1 for w in words if any(p in w.lower() for p in self.profanity_list))
        profanity_ratio = profanity_count / len(words)
        
        # 4. Determine State and Calculate Intensity
        intensity = 1.0 + (caps_ratio * 2.0) + (exclamation_count * 0.1) + (profanity_ratio * 1.5)
        
        dominant_state = "neutral"
        action_state = "NORMAL"

        if profanity_ratio > 0.1 and caps_ratio > 0.2:
            dominant_state = "aggressive" # Attacking / Overwhelming
        elif profanity_ratio > 0.05 and exclamation_count == 0:
            dominant_state = "incisive" # Surgical, precise, passionate but controlled
        elif caps_ratio > 0.3 or exclamation_count > 3:
            dominant_state = "emphasis"
            
        # Cap intensity to prevent mathematical blowout
        intensity = min(intensity, 3.0)

        return {
            "dominant_state": dominant_state,
            "action_state": action_state,
            "physical_intensity": round(intensity, 2),
            "metrics": {
                "caps_ratio": round(caps_ratio, 2),
                "profanity_ratio": round(profanity_ratio, 2),
                "exclamation_count": exclamation_count
            }
        }

# Singleton Orchestrator
text_tone_engine = TextToneClassifier()
