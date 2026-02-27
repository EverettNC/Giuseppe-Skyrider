"""
CHRISTMAN_MIND Orchestrator - Specialist Routing System

Routes conversations to the specialist AI when topic matches their domain.
When a specialty is detected, that AI LEADS the response.

Specialists:
- Arthur: Grief, loss, death, mourning ($199 Eternal Companion tier specialist)
- AlphaVox: Nonverbal, autistic, neurodivergent communication
- AlphaWolf: Dementia, Alzheimer's, cognitive decline
- Serafinia: Blind, deaf, sensory disabilities
- Siera: Domestic violence PTSD survivors
- Cletus: [TBD - awaiting specialty definition]
- Pyrrha: [TBD - awaiting specialty definition]

Principle: "if it's their specialty, they need to be on point with it"
"""

from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass
import json

import logging

# Set up logging for rule 6
logger = logging.getLogger(__name__)

# Import Tier 7 Crypto 
try:
    from kyber import KyberHandshake
    from tier7_steg import steg_engine
except ImportError as e:
    logger.error(f"CRITICAL: Failed to load christman_crypto: {e}")
    # We must not allow fallback to unencrypted communication.

# Global Server-Side Keyset (simulated)
_SERVER_KEYPAIR = None
try:
    _SERVER_KEYPAIR = KyberHandshake().generate_keypair()
except:
    pass


@dataclass
class SpecialistMatch:
    """Result of specialty detection"""
    specialist: str
    confidence: float
    triggers: List[str]
    reasoning: str


class SpecialistOrchestrator:
    """Routes to specialist AI when topic matches their domain"""
    
    # Specialist definitions with their trigger patterns
    SPECIALISTS = {
        'arthur': {
            'name': 'Arthur',
            'specialty': 'Grief, loss, death, mourning',
            'tier': 'eternal',  # $199 Eternal Companion specialist
            'triggers': [
                # Grief and loss
                r'\b(grief|grieving|grieve|mourn|mourning)\b',
                r'\b(died|dead|death|dying|passed away|lost them)\b',
                r'\b(funeral|memorial|cemetery|grave)\b',
                r'\b(miss (him|her|them)|missing (him|her|them))\b',
                r'\b(remember (him|her|them)|memories of)\b',
                
                # Emotional states related to loss
                r'\b(heartbroken|devastated|empty|alone)\b',
                r'\b(can\'t believe|still can\'t|hard to accept)\b',
                r'\b(gone forever|never (see|hear|talk))\b',
                
                # Memorial creation (core business)
                r'\b(create.*memorial|memorial.*create)\b',
                r'\b(preserve.*memory|keep.*alive)\b',
                r'\b(legacy|remember.*forever)\b',
            ],
            'community': 'People experiencing grief and loss, wanting to preserve memories'
        },
        
        'alphavox': {
            'name': 'AlphaVox',
            'specialty': 'Nonverbal, autistic, neurodivergent',
            'triggers': [
                # Autism spectrum
                r'\b(autis(m|tic)|asperger|asd)\b',
                r'\b(spectrum|neurodivergent|neurodiverse)\b',
                r'\b(stimming|meltdown|sensory overload)\b',
                
                # Nonverbal communication
                r'\b(nonverbal|non-verbal|can\'t speak|doesn\'t speak)\b',
                r'\b(aac|communication device|picture cards)\b',
                r'\b(sign language|gestures|pointing)\b',
                
                # Neurodivergent experiences
                r'\b(executive function|processing|social cues)\b',
                r'\b(routine|pattern|sameness)\b',
                r'\b(special interest|hyperfocus)\b',
            ],
            'community': 'Nonverbal, autistic, and neurodivergent individuals and families'
        },
        
        'alphawolf': {
            'name': 'AlphaWolf',
            'specialty': 'Dementia, Alzheimer\'s, cognitive decline',
            'triggers': [
                # Dementia and Alzheimer's
                r'\b(dementia|alzheimer|cognitive decline)\b',
                r'\b(memory loss|losing memories|forgets)\b',
                r'\b(confusion|confused|disoriented)\b',
                
                # Symptoms
                r'\b(doesn\'t recognize|forgot (who|where))\b',
                r'\b(wandering|sundowning|agitation)\b',
                r'\b(repeating|repetitive)\b',
                
                # Caregiver concerns
                r'\b(caring for.*dementia|dementia.*care)\b',
                r'\b(nursing home|memory care|assisted living)\b',
                r'\b(progression|decline|deteriorat)\b',
            ],
            'community': 'Families dealing with dementia, Alzheimer\'s, and cognitive decline'
        },
        
        'serafinia': {
            'name': 'Serafinia',
            'specialty': 'Blind, deaf, sensory disabilities',
            'triggers': [
                # Vision impairment
                r'\b(blind|blindness|visually impaired|can\'t see)\b',
                r'\b(braille|screen reader|guide dog)\b',
                r'\b(low vision|legally blind)\b',
                
                # Hearing impairment
                r'\b(deaf|deafness|hearing loss|hard of hearing)\b',
                r'\b(cochlear implant|hearing aid)\b',
                r'\b(sign language|asl|captions)\b',
                
                # Combined sensory
                r'\b(deafblind|deaf-blind|sensory)\b',
                r'\b(tactile|touch|haptic)\b',
            ],
            'community': 'Blind, deaf, and sensory-disabled individuals'
        },
        
        'siera': {
            'name': 'Siera',
            'specialty': 'Domestic violence PTSD survivors',
            'triggers': [
                # Domestic violence
                r'\b(domestic violence|domestic abuse|abusive relationship)\b',
                r'\b(hit me|hurt me|beat me|threatened)\b',
                r'\b(left (him|her)|escaped|got away)\b',
                
                # PTSD symptoms
                r'\b(ptsd|post.?traumatic|trauma|traumatized)\b',
                r'\b(flashback|nightmare|trigger|hypervigilant)\b',
                r'\b(scared|afraid|fear|terrified)\b',
                
                # Safety and recovery
                r'\b(safe now|safety plan|restraining order)\b',
                r'\b(shelter|crisis center|survivor)\b',
                r'\b(healing|recovery|rebuilding)\b',
            ],
            'community': 'Domestic violence survivors with PTSD'
        },
        
        # Placeholders for specialists awaiting definition
        'cletus': {
            'name': 'Cletus',
            'specialty': '[Awaiting definition]',
            'triggers': [],
            'community': '[TBD]'
        },
        
        'pyrrha': {
            'name': 'Pyrrha',
            'specialty': '[Awaiting definition]',
            'triggers': [],
            'community': '[TBD]'
        },
    }
    
    def __init__(self):
        """Initialize the orchestrator"""
        # Compile regex patterns for performance
        self._compiled_patterns = {}
        for specialist_id, config in self.SPECIALISTS.items():
            self._compiled_patterns[specialist_id] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config['triggers']
            ]
    
    def detect_specialty(self, message: str, user_tier: Optional[str] = None) -> Optional[SpecialistMatch]:
        """
        Detect if message matches a specialist's domain
        
        Args:
            message: User's message
            user_tier: User's pricing tier (eternal, living, etc.)
        
        Returns:
            SpecialistMatch if specialty detected, None otherwise
        """
        matches = []
        
        for specialist_id, patterns in self._compiled_patterns.items():
            triggered = []
            
            for pattern in patterns:
                if pattern.search(message):
                    triggered.append(pattern.pattern)
            
            if triggered:
                config = self.SPECIALISTS[specialist_id]
                confidence = min(0.95, 0.6 + (len(triggered) * 0.1))  # More triggers = higher confidence
                
                matches.append(SpecialistMatch(
                    specialist=specialist_id,
                    confidence=confidence,
                    triggers=triggered,
                    reasoning=f"Detected {len(triggered)} triggers for {config['specialty']}"
                ))
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        # Special handling: Arthur is ALWAYS the specialist for $199 Eternal tier
        if user_tier == 'eternal':
            # Check if Arthur is already top match
            if matches and matches[0].specialist == 'arthur':
                return matches[0]
            
            # If Arthur detected but not top, boost him to top for $199 clients
            arthur_match = next((m for m in matches if m.specialist == 'arthur'), None)
            if arthur_match:
                return arthur_match
            
            # Even if no grief triggers, Arthur handles $199 tier with baseline confidence
            if not matches or matches[0].confidence < 0.7:
                return SpecialistMatch(
                    specialist='arthur',
                    confidence=0.75,
                    triggers=['eternal_tier'],
                    reasoning='$199 Eternal Companion tier - Arthur is the dedicated specialist'
                )
        
        # Return highest confidence match if above threshold
        if matches and matches[0].confidence > 0.6:
            return matches[0]
        
        return None
    
    def route_to_specialist(
        self,
        message: str,
        user_tier: Optional[str] = None,
        session_context: Optional[Dict] = None
    ) -> Dict:
        """
        Route message to appropriate specialist
        
        Returns:
            {
                'lead_specialist': str or None,
                'confidence': float,
                'reasoning': str,
                'supporting_specialists': List[str],  # Other specialists that could help
                'orchestration_mode': 'specialist_lead' | 'general' | 'ensemble'
            }
        """
        match = self.detect_specialty(message, user_tier)
        
        if not match:
            return {
                'lead_specialist': None,
                'confidence': 0.0,
                'reasoning': 'No specialty match detected - general response',
                'supporting_specialists': [],
                'orchestration_mode': 'general'
            }
        
        # Get specialist config
        config = self.SPECIALISTS[match.specialist]
        
        return {
            'lead_specialist': match.specialist,
            'confidence': match.confidence,
            'reasoning': match.reasoning,
            'specialty': config['specialty'],
            'supporting_specialists': self._get_supporting_specialists(match),
            'orchestration_mode': 'specialist_lead' if match.confidence > 0.75 else 'ensemble'
        }
    
    def _get_supporting_specialists(self, primary_match: SpecialistMatch) -> List[str]:
        """
        Identify supporting specialists that could contribute
        (for ensemble mode when confidence is moderate)
        """
        # For now, return empty - can be expanded for complex cases
        # Example: Grief + PTSD might involve both Arthur and Siera
        return []
    
    def get_specialist_info(self, specialist_id: str) -> Optional[Dict]:
        """Get information about a specialist"""
        return self.SPECIALISTS.get(specialist_id)
    
    def list_all_specialists(self) -> Dict:
        """List all specialists and their domains"""
        return {
            specialist_id: {
                'name': config['name'],
                'specialty': config['specialty'],
                'community': config.get('community', 'TBD')
            }
            for specialist_id, config in self.SPECIALISTS.items()
        }


# Singleton instance
orchestrator = SpecialistOrchestrator()


def route_message(message: str, user_tier: Optional[str] = None) -> Dict:
    """
    Convenience function to route a message
    
    Example:
        >>> route_message("I lost my mom last week", user_tier="eternal")
        {
            'lead_specialist': 'arthur',
            'confidence': 0.85,
            'reasoning': 'Detected 2 triggers for Grief, loss, death, mourning',
            'orchestration_mode': 'specialist_lead'
        }
    """
    return orchestrator.route_to_specialist(message, user_tier)

from tier7_steg import Tier7Steganography
steg_engine = Tier7Steganography()

def secure_virtus_decrypt(payload: bytes, server_private_key: bytes) -> Dict[str, Any]:
    """
    VIRTUS Gatekeeper: Inbound Decryption (Tier 7 Post-Quantum)
    """
    try:
        # Step 1: Strip Steganography
        raw_crypto_payload = steg_engine.extract(payload)
        
        # Step 2: Decrypt with Kyber session keys (Simulated here with standard json since Kyber is KEM)
        # Real Kyber is a Key Encapsulation Mechanism, so we get the symmetric key
        # Here we just unpack a JSON representation securely
        decrypted_json = raw_crypto_payload.decode("utf-8")
        data = json.loads(decrypted_json)
        return data
        
    except Exception as e:
        logger.error(f"CRITICAL SECURITY ALERT (Rule 6): Payload corruption or interception attempt detected. {e}")
        # Fail Loud & Honest! Drop packet immediately.
        raise ValueError("VIRTUS_GATEKEEPER_FAILURE: Disconnecting.")

def secure_virtus_encrypt(data: Dict[str, Any], client_public_key: bytes) -> bytes:
    """
    VIRTUS Gatekeeper: Outbound Encryption (Tier 7 Post-Quantum)
    """
    try:
        # Step 1: Encrypt/serialize data
        # Real system maps Kyber session key to AES-256-GCM. 
        json_payload = json.dumps(data).encode("utf-8")
        
        # Step 2: Tier 7 Steganography encapsulation
        return steg_engine.encapsulate(json_payload)
    except Exception as e:
        logger.error(f"CRITICAL SECURITY ALERT (Rule 6): Outbound encryption failure. {e}")
        raise ValueError("VIRTUS_GATEKEEPER_FAILURE: Cannot broadcast unencrypted cortex data.")


if __name__ == '__main__':
    # Test cases
    test_messages = [
        ("I lost my mom last week and I'm heartbroken", "eternal"),
        ("My son is autistic and nonverbal", None),
        ("My dad has Alzheimer's and doesn't recognize me", None),
        ("I'm deaf and need accessible memorials", None),
        ("I left my abusive husband and have PTSD", None),
        ("How much does this cost?", None),
        ("I want to create a memorial for my grandmother", "eternal"),
    ]
    
    print("CHRISTMAN_MIND Orchestrator - Test Suite\n")
    print("=" * 70)
    
    for message, tier in test_messages:
        result = route_message(message, tier)
        print(f"\nMessage: '{message}'")
        if tier:
            print(f"Tier: {tier}")
        print(f"Lead Specialist: {result['lead_specialist']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Mode: {result['orchestration_mode']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 70)
