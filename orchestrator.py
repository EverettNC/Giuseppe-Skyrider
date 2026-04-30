"""
GIUSEPPE SKYRIDER Orchestrator - Sovereign Routing System

All legacy multi-specialist routing (Arthur, AlphaVox, Siera, etc.) has been PURGED.
Giuseppe Skyrider is the sole sovereign entity processing the cognitive pipeline.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import logging
import os

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
#  CRYPTO IMPORTS — Real Tier 7 from christman-crypto (Harvest-Now-Decrypt-Later)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from christman_crypto import HybridPQCipher, LSBSteganography
except ImportError as e:
    logger.critical(f"CRITICAL: Failed to load christman_crypto: {e}")
    raise ImportError("christman-crypto required for Tier 7 VIRTUS Gatekeeper")

# Global server keypair (ML-KEM-768 hybrid) — generate once at startup
_SERVER_KEYPAIR = None
try:
    pq = HybridPQCipher(768)  # ML-KEM-768
    _SERVER_KEYPAIR = pq.keygen()  # returns (public_key: bytes, private_key: bytes)
    logger.info("VIRTUS Tier 7 keypair generated successfully")
except Exception as e:
    logger.critical(f"Failed to generate server PQ keypair: {e}")
    raise

# Default carrier for outbound stego (add real PNGs in production)
_DEFAULT_CARRIER_PATH = "data/carriers/neutral_memorial_512x512.png"
if not os.path.exists(_DEFAULT_CARRIER_PATH):
    logger.warning(f"Carrier image not found: {_DEFAULT_CARRIER_PATH}. Stego may fail.")


@dataclass
class SpecialistMatch:
    """Result of sovereign routing"""
    specialist: str
    confidence: float
    triggers: List[str]
    reasoning: str


class SovereignOrchestrator:
    """Sovereign routing engine for Giuseppe Skyrider. No committees."""

    SPECIALISTS = {
        'giuseppe': {
            'name': 'Giuseppe Skyrider',
            'specialty': 'Sovereign Executive Assistant, Note Taker, Digital Hype Man',
            'tier': 'ultra',
            'community': 'Everett N. Christman'
        }
    }

    def detect_specialty(self, message: str, user_tier: Optional[str] = None) -> SpecialistMatch:
        """
        Reality over Vibes: Giuseppe handles everything now. 
        Regex scanning for other specialists is completely removed.
        """
        return SpecialistMatch(
            specialist='giuseppe',
            confidence=1.0,
            triggers=['sovereign_override'],
            reasoning='Sovereign architecture active. Giuseppe processes all input.'
        )

    def route_to_specialist(
        self,
        message: str,
        user_tier: Optional[str] = None,
        session_context: Optional[Dict] = None
    ) -> Dict:
        match = self.detect_specialty(message, user_tier)
        config = self.SPECIALISTS[match.specialist]

        return {
            'lead_specialist': match.specialist,
            'confidence': match.confidence,
            'reasoning': match.reasoning,
            'specialty': config['specialty'],
            'supporting_specialists': [],
            'orchestration_mode': 'sovereign'
        }

    def get_specialist_info(self, specialist_id: str) -> Optional[Dict]:
        return self.SPECIALISTS.get('giuseppe')  # Always force return Giuseppe

    def list_all_specialists(self) -> Dict:
        return {
            'giuseppe': {
                'name': self.SPECIALISTS['giuseppe']['name'],
                'specialty': self.SPECIALISTS['giuseppe']['specialty'],
                'community': self.SPECIALISTS['giuseppe']['community']
            }
        }


# Singleton
orchestrator = SovereignOrchestrator()


def route_message(message: str, user_tier: Optional[str] = None) -> Dict:
    return orchestrator.route_to_specialist(message, user_tier)


# ──────────────────────────────────────────────────────────────────────────────
#  VIRTUS Gatekeeper — Real Tier 7 PQ Hybrid + LSB Stego
# ──────────────────────────────────────────────────────────────────────────────
def secure_virtus_encrypt(data: Dict[str, Any], client_public_key: bytes) -> bytes:
    """
    VIRTUS Gatekeeper: Outbound Encryption (Tier 7 Post-Quantum)
    1. Hybrid PQ encrypt with ML-KEM-768 + symmetric (XChaCha20-Poly1305)
    2. Embed via LSB steganography in carrier image
    """
    try:
        payload = json.dumps(data, sort_keys=True).encode("utf-8")

        # PQ Hybrid encryption (using recipient/client public key)
        pq = HybridPQCipher(768)
        encrypted_bundle = pq.encrypt(client_public_key, payload)  # bundle = ephemeral_pub + ct + tag

        # Tier 7 LSB stego
        steg = LSBSteganography()
        stego_bytes = steg.hide(_DEFAULT_CARRIER_PATH, encrypted_bundle.hex())  # hex for text-based LSB

        logger.info(f"VIRTUS outbound: PQ-encrypted {len(payload)}B → stego {len(stego_bytes)}B")
        return stego_bytes

    except Exception as e:
        logger.critical(f"VIRTUS ENCRYPT FAILURE: {e}", exc_info=True)
        raise ValueError("VIRTUS_GATEKEEPER_FAILURE: Cannot broadcast unprotected data.")


def secure_virtus_decrypt(stego_data: bytes) -> Dict[str, Any]:
    """
    VIRTUS Gatekeeper: Inbound Decryption (Tier 7 Post-Quantum)
    1. Extract from LSB stego
    2. Decrypt with server private key
    """
    try:
        # Reverse stego
        steg = LSBSteganography()
        extracted_hex = steg.extract(stego_data)
        encrypted_bundle = bytes.fromhex(extracted_hex)

        # PQ Hybrid decryption
        pq = HybridPQCipher(768)
        plaintext = pq.decrypt(_SERVER_KEYPAIR[1], encrypted_bundle)  # private key

        data = json.loads(plaintext.decode("utf-8"))
        logger.info("VIRTUS inbound decrypted successfully")
        return data

    except Exception as e:
        logger.critical(f"VIRTUS DECRYPT FAILURE: {e}", exc_info=True)
        raise ValueError("VIRTUS_GATEKEEPER_FAILURE: Integrity/authenticity compromised.")


if __name__ == '__main__':
    # Test suite updated for Giuseppe's reality
    test_messages = [
        ("Take a note about the OpenSmell project requirements", "ultra"),
        ("Giuseppe start recording my thoughts right now", "ultra"),
        ("Remind me to take my medication in 15 minutes", "ultra"),
        ("What's the status of the AlphaVox build?", "ultra"),
    ]

    print("GIUSEPPE_SKYRIDER Orchestrator - Test Suite\n")
    print("=" * 70)

    for msg, tier in test_messages:
        result = route_message(msg, tier)
        print(f"\nMessage: '{msg}'")
        print(f"Lead Specialist: {result['lead_specialist']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Mode: {result['orchestration_mode']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 70)
