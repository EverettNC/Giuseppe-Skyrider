import logging
import threading
import json
from typing import List, Dict, Any

from logger import get_logger
from evolutionary_engine import EvolutionaryAI

logger = get_logger(__name__)

class NLPIntegrationService:
    """
    Dynamically evolving comprehension system replacing static keyword-matching.
    Learns from user interactions and physically alters its hidden layers to adapt.
    """
    
    VECTOR_SIZE = 256
    
    def __init__(self):
        # Legacy tracking list
        self.academic_discussions = []
        
        # Legacy static keywords for fallback safety (Rule 6)
        self.intent_keywords = {
            "academic": ["research", "paper", "study", "analysis", "data", "science"],
            "emotional": ["feel", "sad", "angry", "happy", "help", "care", "support"],
            "system": ["update", "status", "reboot", "stop", "start", "config"]
        }
        
        # 1. Update Initialization: Instantiate evolutionary model
        try:
            self.evo_brain = EvolutionaryAI(
                population_size=10, 
                input_size=self.VECTOR_SIZE, 
                output_size=1, 
                mutation_rate=0.1
            )
            # Load the fittest individual to persist learning
            self.evo_brain.load_fittest("nlp_fittest.json")
            logger.info("NLPIntegrationService initialized with Evolutionary Core.")
        except Exception as e:
            logger.error(f"Failed to initialize Evolutionary Engine in NLP: {e}")
            self.evo_brain = None

    # 2. Local Text Vectorization (Axiom 3: CPU Friendly)
    def vectorize_text(self, text: str) -> List[float]:
        """
        Lightweight CPU-friendly text-to-vector hashing function.
        Converts a string into a flat numerical array matching the VECTOR_SIZE.
        No CUDA/external APIs required.
        """
        vec = [0.0] * self.VECTOR_SIZE
        if not text:
            return vec
            
        words = text.lower().replace(".", "").replace(",", "").split()
        for word in words:
            # Simple string hash mapping word to index
            idx = sum(ord(c) for c in word) % self.VECTOR_SIZE
            vec[idx] += 1.0
            
        # Normalize the vector (L2 norm)
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
            
        return vec

    # 4. Dynamic Intent Classification
    def determine_intent(self, user_input: str) -> str:
        """
        Predicts intent domain dynamically using the evolved model.
        Falls back to static keyword matching if evolution fails.
        """
        try:
            if not getattr(self, "evo_brain", None):
                raise ValueError("Evolutionary Engine not initialized")
                
            vector = self.vectorize_text(user_input)
            
            # Predict using the apex model (output is [0..1])
            prediction = self.evo_brain.population[0].predict(vector)[0]
            
            logger.info(f"Evolutionary intent prediction score: {prediction:.3f}")
            
            # Use prediction to select domain (dynamic classification)
            if prediction > 0.66:
                domain = "academic"
            elif prediction > 0.33:
                domain = "emotional"
            else:
                domain = "system"
                
            return domain
            
        except Exception as e:
            # 5. Safety & Fallback (Rule 6 & Rule 1)
            logger.error(f"Evolutionary prediction failed: {e}. Falling back to static keyword matching.")
            return self._legacy_determine_intent(user_input)

    def _legacy_determine_intent(self, user_input: str) -> str:
        """Fallback static keyword matching to ensure continuity."""
        lower_input = user_input.lower()
        
        scores = {intent: 0 for intent in self.intent_keywords}
        for intent, keywords in self.intent_keywords.items():
            for kw in keywords:
                if kw in lower_input:
                    scores[intent] += 1
                    
        best_intent = max(scores, key=scores.get)
        if scores[best_intent] == 0:
            return "general"  # Default generic intent
        return best_intent

    # 3. Overhaul learn_from_interaction()
    def learn_from_interaction(self, user_input: str, feedback_score: float):
        """
        The Evolution Trigger: Learns from user feedback by altering hidden layers.
        Replaces simple data appending with active dynamic evolution.
        
        Args:
            user_input: The text the user provided.
            feedback_score: User feedback, where +1 is positive and -1 is negative.
        """
        # Keep legacy tracking operative
        self.academic_discussions.append({
            "input": user_input,
            "feedback": feedback_score
        })
        
        def evolve_task():
            try:
                if not getattr(self, "evo_brain", None):
                    raise ValueError("Evolutionary Engine not initialized")
                    
                vector = self.vectorize_text(user_input)
                
                # Target fitness mapping (feedback_score -1.0 to 1.0 mapped to target 0.0 to 1.0)
                target = (feedback_score + 1.0) / 2.0 
                
                # Evaluate the population on the recent input vector
                for ind in self.evo_brain.population:
                    pred = ind.predict(vector)[0]
                    # Compute error between prediction and target
                    error = abs(pred - target)
                    # Set fitness: lower error -> higher fitness
                    ind.fitness = max(0.0, 1.0 - error) * 100.0
                    
                # Core evolution cycle: select, crossover, mutate 
                self.evo_brain.evolve_step()
                # Persist the apex individual
                self.evo_brain.save_fittest("nlp_fittest.json")
                
                logger.info(f"NLP Evolutionary comprehension updated (Generation {self.evo_brain.generation})")

            except Exception as e:
                # 5. Safety & Fallback (Rule 6 & Rule 1)
                logger.error(f"Evolutionary Engine fallback. Failed to evolve NLP understanding: {e}")

        # Run evolution in background to prevent blocking
        thread = threading.Thread(target=evolve_task)
        thread.start()

if __name__ == "__main__":
    import sys
    # Initialize logger for terminal output
    logging.basicConfig(level=logging.INFO)
    
    nlp = NLPIntegrationService()
    test_input = "research paper on the new study data"
    print(f"Input: '{test_input}'")
    print("Intent:", nlp.determine_intent(test_input))
    print("Learning from feedback...")
    nlp.learn_from_interaction(test_input, 1.0)
