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

from typing import Dict, List, Optional
import re
import unicodedata
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
#  CRYPTO IMPORTS & STUBS (unchanged from your version)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from christman_crypto.kyber import KyberHandshake
    from tier7_steg import Tier7Steganography
except ImportError as e:
    logger.error(f"CRITICAL: Failed to load christman_crypto: {e}")

_SERVER_KEYPAIR = None
try:
    _SERVER_KEYPAIR = KyberHandshake().generate_keypair()
except Exception:
    pass

steg_engine = Tier7Steganography()


@dataclass
class SpecialistMatch:
    """Result of specialty detection"""
    specialist: str
    confidence: float
    triggers: List[str]
    reasoning: str


class SpecialistOrchestrator:
    """Routes to specialist AI when topic matches their domain"""

    SPECIALISTS = {
        'arthur': {
            'name': 'Arthur',
            'specialty': 'Grief, loss, death, mourning',
            'tier': 'eternal',
            'triggers': [
                r'\b(grief|grieving|grieve|mourn|mourning)\b',
                r'\b(died|dead|death|dying|passed away|lost (him|her|them)|passed on)\b',
                r'\b(funeral|memorial|cemetery|grave)\b',
                r'\b(miss (him|her|them)|missing (him|her|them))\b',
                r'\b(remember (him|her|them)|memories of)\b',
                r'\b(heartbroken|devastated|empty|alone)\b',
                r'\b(can\'?t believe|still can\'?t|hard to accept)\b',
                r'\b(gone forever|never (see|hear|talk))\b',
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
                r'\b(autis(m|tic)|asperger|asd)\b',
                r'\b(spectrum|neurodivergent|neurodiverse)\b',
                r'\b(stimming|meltdown|sensory overload)\b',
                r'\b(nonverbal|non-verbal|doesn\'?t speak|can\'?t speak)\b',
                r'\b(aac|communication device|picture cards)\b',
                r'\b(sign language|gestures|pointing)\b',
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
                r'\b(dementia|alzheimer|cognitive decline)\b',
                r'\b(memory loss|losing memories|forgets)\b',
                r'\b(confusion|confused|disoriented)\b',
                r'\b(doesn\'?t recognize|forgot (who|where))\b',
                r'\b(wandering|sundowning|agitation)\b',
                r'\b(repeating|repetitive)\b',
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
                r'\b(blind|blindness|visually impaired|can\'?t see)\b',
                r'\b(braille|screen reader|guide dog)\b',
                r'\b(low vision|legally blind)\b',
                r'\b(deaf|deafness|hearing loss|hard of hearing)\b',
                r'\b(cochlear implant|hearing aid)\b',
                r'\b(sign language|asl|captions)\b',
                r'\b(deafblind|deaf-blind|sensory)\b',
                r'\b(tactile|touch|haptic)\b',
            ],
            'community': 'Blind, deaf, and sensory-disabled individuals'
        },
        'siera': {
            'name': 'Siera',
            'specialty': 'Domestic violence PTSD survivors',
            'triggers': [
                r'\b(domestic violence|domestic abuse|abusive relationship)\b',
                r'\b(hit me|hurt me|beat me|threatened)\b',
                r'\b(left (him|her)|escaped|got away)\b',
                r'\b(ptsd|post.?traumatic|trauma|traumatized)\b',
                r'\b(flashback|nightmare|trigger|hypervigilant)\b',
                r'\b(scared|afraid|fear|terrified)\b',
                r'\b(safe now|safety plan|restraining order)\b',
                r'\b(shelter|crisis center|survivor)\b',
                r'\b(healing|recovery|rebuilding)\b',
            ],
            'community': 'Domestic violence survivors with PTSD'
        },
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
        self._compiled_patterns = {}
        for specialist_id, config in self.SPECIALISTS.items():
            self._compiled_patterns[specialist_id] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config['triggers']
            ]

    def _normalize_message(self, message: str) -> str:
        """Normalize unicode, strip extra whitespace, remove some punctuation noise"""
        message = unicodedata.normalize('NFKC', message)
        message = re.sub(r'\s+', ' ', message.strip())
        return message

    def detect_specialty(self, message: str, user_tier: Optional[str] = None) -> Optional[SpecialistMatch]:
        message = self._normalize_message(message)
        matches = []

        for specialist_id, patterns in self._compiled_patterns.items():
            triggered = [p.pattern for p in patterns if p.search(message)]
            if triggered:
                config = self.SPECIALISTS[specialist_id]
                # Diminishing returns: base 0.55 + sqrt(n_triggers)*0.15, cap at 0.95
                n = len(triggered)
                confidence = min(0.95, 0.55 + (n ** 0.5) * 0.15 + (0.08 if n >= 3 else 0))
                matches.append(SpecialistMatch(
                    specialist=specialist_id,
                    confidence=confidence,
                    triggers=triggered,
                    reasoning=f"Detected {n} triggers for {config['specialty']}"
                ))

        matches.sort(key=lambda x: x.confidence, reverse=True)

        # Eternal tier ($199) forces Arthur priority
        if user_tier == 'eternal':
            arthur_match = next((m for m in matches if m.specialist == 'arthur'), None)
            if arthur_match:
                return arthur_match
            # Baseline even without triggers
            return SpecialistMatch(
                specialist='arthur',
                confidence=0.75,
                triggers=['eternal_tier_priority'],
                reasoning='$199 Eternal Companion tier → Arthur is the dedicated specialist'
            )

        if matches and matches[0].confidence > 0.6:
            return matches[0]

        return None

    def route_to_specialist(
        self,
        message: str,
        user_tier: Optional[str] = None,
        session_context: Optional[Dict] = None
    ) -> Dict:
        match = self.detect_specialty(message, user_tier)

        if not match:
            return {
                'lead_specialist': None,
                'confidence': 0.0,
                'reasoning': 'No specialty match detected - general response',
                'specialty': None,
                'supporting_specialists': [],
                'orchestration_mode': 'general'
            }

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
        # Placeholder — expand later for multi-specialist cases (e.g. grief + PTSD → Arthur + Siera)
        return []

    def get_specialist_info(self, specialist_id: str) -> Optional[Dict]:
        return self.SPECIALISTS.get(specialist_id)

    def list_all_specialists(self) -> Dict:
        return {
            sid: {
                'name': cfg['name'],
                'specialty': cfg['specialty'],
                'community': cfg.get('community', 'TBD')
            }
            for sid, cfg in self.SPECIALISTS.items()
        }


# Singleton
orchestrator = SpecialistOrchestrator()


def route_message(message: str, user_tier: Optional[str] = None) -> Dict:
    return orchestrator.route_to_specialist(message, user_tier)


# ──────────────────────────────────────────────────────────────────────────────
#  secure_virtus_encrypt — YOUR ORIGINAL VERSION (with big warning)
# ──────────────────────────────────────────────────────────────────────────────
# WARNING: This function DOES NOT provide real encryption.
#          It only serializes → steganography (hiding, NOT confidentiality).
#          It IGNORES client_public_key entirely.
#          The name/docstring/exception claim post-quantum protection → misleading.
#          For real Tier-7 PQ hybrid (ML-KEM + AES-GCM), see earlier suggestions.
def secure_virtus_encrypt(data: Dict[str, Any], client_public_key: bytes) -> bytes:
    """
    VIRTUS Gatekeeper: Outbound Encryption (Tier 7 Post-Quantum)
    """
    try:
        json_payload = json.dumps(data).encode("utf-8")
        return steg_engine.encapsulate(json_payload)
    except Exception as e:
        logger.error(f"CRITICAL SECURITY ALERT (Rule 6): Outbound encryption failure. {e}")
        raise ValueError("VIRTUS_GATEKEEPER_FAILURE: Cannot broadcast unencrypted cortex data.")


if __name__ == '__main__':
    test_messages = [
        ("I lost my mom last week and I'm heartbroken", "eternal"),
        ("My son is autistic and nonverbal, he can't speak at all", None),
        ("My dad has Alzheimer's and doesn't recognize me anymore", None),
        ("I'm deaf and need accessible memorials with captions", None),
        ("I left my abusive husband last year, still have PTSD flashbacks", None),
        ("How much does the eternal tier cost?", None),
        ("I want to create a memorial for my grandmother who passed away", "eternal"),
    ]

    print("CHRISTMAN_MIND Orchestrator - Test Suite\n")
    print("=" * 70)

    for msg, tier in test_messages:
        result = route_message(msg, tier)
        print(f"\nMessage: '{msg}'")
        if tier:
            print(f"Tier: {tier}")
        print(f"Lead Specialist: {result['lead_specialist']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Mode: {result['orchestration_mode']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 70)
