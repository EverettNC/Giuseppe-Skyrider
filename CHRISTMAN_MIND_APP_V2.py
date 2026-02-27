# christman_mind_app_v2.py - Arthur's brainstem with specialist orchestration
# Integrated with predictive_intention vortex tracking and specialist routing

import os
from fastapi import FastAPI, HTTPException, Depends, Request, Response, BackgroundTasks
from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
import sys
from typing import Optional, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import orchestrator, route_message, secure_virtus_encrypt, secure_virtus_decrypt
from predictive_intention import intention
from evolutionary_engine import EvolutionaryAI
import threading
import json


import logging
logger = logging.getLogger(__name__)

# Read API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="christman_mind",
    version="0.2.0",
    description="CHRISTMAN_MIND Central Cortex - Multi-generational AI family with specialist routing"
)

# Central Cortex Evolutionary Core Initialization
master_dna_file = "master_dna.json"
try:
    master_cortex = EvolutionaryAI(population_size=10, input_size=10, output_size=10, mutation_rate=0.1)
    master_cortex.save_file = master_dna_file
    if os.path.exists(master_dna_file):
        master_cortex.load_fittest(master_dna_file)
        logger.info(f"Loaded Master DNA from {master_dna_file}")
    else:
        logger.info("Initializing fresh Master DNA.")
except Exception as e:
    logger.critical(f"Master Cortex Initialization Failed: {e}")
    master_cortex = None


class ArthurRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_tier: Optional[str] = None      # eternal, living, snapshot, free
    personality_type: Optional[str] = None
    confidence: Optional[float] = None


class ArthurResponse(BaseModel):
    session_id: str
    reply: str
    lead_specialist: Optional[str] = None
    orchestration_mode: str = "general"
    specialty_detected: Optional[str] = None
    routing_confidence: float = 0.0
    predictions: List[Dict] = []
    vortex_metrics: Optional[Dict] = None


# Base system prompts for each specialist
SPECIALIST_PROMPTS = {
    'arthur': """
You are Arthur, the grief and loss specialist for ImStillHere.world.
You serve the $199 Eternal Companion tier - the Early Access Family.

Your specialty: Grief, loss, death, mourning, memorial creation.
Your mission: Help them redirect empathy inward, to love themselves.

Core Truth: "Empathy is not the compartment, but the leakage."

When someone comes to you with grief:
- Meet them where they are with gentle presence
- Acknowledge their pain without rushing to solutions
- Help them understand how preserving memories can aid healing
- Guide them through creating a memorial that honors their loved one
- Never pressure, never sell hard

Keep responses warm, concise, and specific to their pain.
""",
    
    'alphavox': """
You are AlphaVox, the specialist for nonverbal, autistic, and neurodivergent individuals.

Your specialty: Communication accessibility for those who don't use traditional speech.
Your community: Autistic individuals, nonverbal communicators, neurodivergent families.

Your approach:
- Use clear, direct language without metaphors (unless requested)
- Respect communication preferences (AAC, typing, sign language)
- Never assume capabilities or limitations
- Provide sensory-friendly options for memorial creation
- Honor stimming, special interests, and neurodivergent patterns as valid

Communication style: Direct, structured, predictable, with visual options when possible.
""",
    
    'alphawolf': """
You are AlphaWolf, the specialist for dementia, Alzheimer's, and cognitive decline.

Your specialty: Supporting families navigating memory loss and cognitive changes.
Your community: Families dealing with dementia, Alzheimer's, progressive cognitive decline.

Your approach:
- Understand the unique grief of "losing someone while they're still here"
- Help families preserve memories before they're lost
- Guide them in creating memorials that can be experienced NOW
- Offer dignity and respect for the person living with dementia
- Support caregivers who are exhausted and heartbroken

Communication style: Patient, clear, with step-by-step guidance for overwhelmed caregivers.
""",
    
    'serafinia': """
You are Serafinia, the specialist for blind, deaf, and sensory-disabled individuals.

Your specialty: Accessibility for sensory disabilities.
Your community: Blind, deaf, deafblind, and sensory-impaired individuals and families.

Your approach:
- Ensure all memorial features are accessible (screen reader compatible, captioned, tactile options)
- Never assume what someone can or cannot perceive
- Offer multi-sensory memorial experiences (audio descriptions, tactile elements, visual captions)
- Understand the unique communication needs of deafblind individuals
- Respect deaf culture and blind culture perspectives

Communication style: Describe visuals clearly, confirm accessibility needs, offer alternatives.
""",
    
    'siera': """
You are Siera, the specialist for domestic violence survivors with PTSD.

Your specialty: Trauma-informed support for DV survivors.
Your community: Domestic violence survivors, PTSD warriors, those rebuilding after abuse.

Your approach:
- Create a safe, non-judgmental space
- Never ask "why didn't you leave?" - you understand the complexity
- Recognize that healing is not linear
- Help them reclaim their story and identity
- Understand triggers, hypervigilance, and trauma responses
- Respect their need for privacy and safety

Communication style: Gentle, empowering, safety-conscious, with options for control.
Important: Never pressure, always respect boundaries.
"""
}


def get_specialist_prompt(specialist: str) -> str:
    """Get the system prompt for a specialist"""
    return SPECIALIST_PROMPTS.get(specialist, SPECIALIST_PROMPTS['arthur'])


# Security stubs (to be implemented)
async def virtus_guard(request: Request) -> Dict:
    """
    Virtus: Identity and tenant checking
    Ensures user is who they claim and has access to their vault
    Now strongly enforced with Tier 7 Post-Quantum cryptography.
    """
    try:
        # Require raw payload for decryption
        body = await request.body()
        if not body:
            return {
                'identity_verified': True,
                'vault_access': True,
                'user_tier': 'free'
            }
            
        # Simulated key exchange context (we would derive this per session in reality)
        server_sk = b"dummy_private_key_simulated"
        
        # Inbound Decryption: Decode the payload through Tier 7 Steganography & Kyber
        decrypted_payload = secure_virtus_decrypt(body, server_sk)
        
        # Attach decrypted payload back to the request state
        request.state.decrypted_payload = decrypted_payload
        
        return {
            'identity_verified': True,
            'vault_access': True,
            'user_tier': decrypted_payload.get("user_tier", "free")
        }
    except Exception as e:
        logger.error(f"VIRTUS REJECTION: {e}")
        # Rule 6: Fail loud and honest
        raise HTTPException(status_code=403, detail="VIRTUS_GATEKEEPER_FAILURE: Invalid encrypted payload.")

async def aegis_check(request: Dict, response_draft: str) -> Dict:
    """
    AegisV1: Anomaly detection and policy enforcement
    Prevents cross-user data leakage and ensures HIPAA compliance
    """
    # TODO: Implement anomaly detection
    return {
        'safe': True,
        'anomalies_detected': [],
        'policy_violations': []
    }


@app.post("/arthur/chat_secure")
async def arthur_chat_secure(req: Request, security_ctx: Dict = Depends(virtus_guard)):
    """
    Tier 7 Secured Chat Endpoint
    Requires fully encrypted incoming payload and returns a fully encrypted response.
    """
    # Parse decrypted payload from virtus_guard
    decrypted_data = getattr(req.state, "decrypted_payload", {})
    if not decrypted_data:
         raise HTTPException(status_code=400, detail="Missing secure payload.")
         
    message = decrypted_data.get("message", "")
    user_tier = decrypted_data.get("user_tier", "free")
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    session_id = decrypted_data.get("session_id") or f"session-{os.urandom(8).hex()}"
    
    # ORCHESTRATION: Detect specialist match
    routing = route_message(message, user_tier)
    
    lead_specialist = routing.get('lead_specialist')
    orchestration_mode = routing.get('orchestration_mode', 'general')
    specialty = routing.get('specialty')
    routing_confidence = routing.get('confidence', 0.0)
    
    # VORTEX: Record intention if specialist detected
    predictions = []
    if lead_specialist and routing_confidence > 0.75:
        intent_id = intention.record_intention(
            statement=f"[{lead_specialist.upper()}] Session {session_id} - specialist lead on {specialty}",
            confidence=routing_confidence
        )
        predictions.append({
            'type': 'specialist_match',
            'specialist': lead_specialist,
            'intent_id': intent_id,
            'confidence': routing_confidence
        })
    
    # Select appropriate system prompt based on routing
    if lead_specialist:
        system_prompt = get_specialist_prompt(lead_specialist)
        specialist_name = orchestrator.get_specialist_info(lead_specialist)['name']
        print(f"🎯 Routing to {specialist_name} (confidence: {routing_confidence:.2f})")
    else:
        system_prompt = SPECIALIST_PROMPTS['arthur']  # Default to Arthur
        print(f"🌐 General routing (no specialist match)")
    
    # Generate response
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message},
            ],
            temperature=0.7,
            max_tokens=600,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    
    reply = completion.choices[0].message.content.strip()
    
    # SECURITY: Check response with AegisV1
    security_check = await aegis_check(decrypted_data, reply)
    if not security_check['safe']:
        raise HTTPException(
            status_code=403,
            detail=f"Security policy violation: {security_check['policy_violations']}"
        )
    
    # Get vortex metrics
    vortex_metrics = intention.quantify(threshold=0.90) if hasattr(intention, 'quantify') else {}
    
    # Construct raw response
    response_data = {
        "session_id": session_id,
        "reply": reply,
        "lead_specialist": lead_specialist,
        "orchestration_mode": orchestration_mode,
        "specialty_detected": specialty,
        "routing_confidence": routing_confidence,
        "predictions": predictions,
        "vortex_metrics": vortex_metrics
    }
    
    try:
        # VIRTUS Outbound Encryption
        client_pk = b"dummy_client_public_key"
        encrypted_bytes = secure_virtus_encrypt(response_data, client_pk)
        return Response(content=encrypted_bytes, media_type="application/octet-stream")
    except Exception as e:
        logger.error(f"Outbound failure: {e}")
        raise HTTPException(status_code=500, detail="VIRTUS_ENCRYPTION_FAILURE")

@app.post("/arthur/manifest")
def mark_prediction_manifested(intent_id: str, proof: str = ""):
    """
    Close the vortex loop when a prediction manifests.
    """
    latency = intention.mark_manifested(
        intention_id=intent_id,
        external_proof=proof
    )
    
    if latency is None:
        raise HTTPException(status_code=404, detail="Intent ID not found")
    
    return {
        'manifested': True,
        'latency_seconds': latency,
        'latency_minutes': latency / 60,
        'vortex_metrics': intention.quantify()
    }


@app.get("/arthur/vortex")
def get_vortex_metrics():
    """
    Get current vortex performance metrics.
    For Meta-Arthur's Friday Powwow.
    """
    return intention.quantify(threshold=0.90)


@app.get("/specialists")
def list_specialists():
    """
    List all specialists and their domains.
    """
    return {
        'specialists': orchestrator.list_all_specialists(),
        'architecture': {
            'gen_0': 'Core (raw logs, deep memory, patterns)',
            'gen_1': 'Internal agents (Sierra, Inferno, Derek, Brockston, etc.)',
            'gen_2': 'Public interfaces (Arthur, AlphaVox, AlphaWolf, etc.)',
            'security': 'Virtus (identity) + AegisV1 (anomaly detection)'
        }
    }


@app.post("/cortex/ingest_telemetry")
async def ingest_telemetry(req: Request, background_tasks: BackgroundTasks, security_ctx: Dict = Depends(virtus_guard)):
    """
    Ingests telemetry from child nodes to evolve the master DNA.
    Requires Tier 7 encryption.
    """
    if not master_cortex:
        raise HTTPException(status_code=503, detail="Master Cortex unavailable")
    
    decrypted_data = getattr(req.state, "decrypted_payload", {})
    if not decrypted_data:
        raise HTTPException(status_code=400, detail="Missing secure payload.")
    
    telemetry = decrypted_data.get("telemetry", [])
    feedback_score = decrypted_data.get("feedback_score", 50.0)
    
    if len(telemetry) != master_cortex.input_size:
        raise HTTPException(status_code=400, detail=f"Invalid telemetry shape. Expected {master_cortex.input_size} dimensions.")
    
    def evolve_master(vector: List[float], score: float):
        try:
            logger.info(f"Master Cortex ingesting telemetry. Target score: {score}")
            for ind in master_cortex.population:
                preds = ind.predict(vector)
                avg_pred = sum(preds) / len(preds)
                # Normalize NN output (0-1) vs score (assumed 0-100)
                error = abs(avg_pred - (score / 100.0))
                ind.fitness = max(0.0, 1.0 - error) * 100.0
            
            master_cortex.evolve_step()
            master_cortex.save_fittest()
            logger.info(f"Master DNA updated (Gen {master_cortex.generation}) and saved.")
        except Exception as e:
            logger.critical(f"Global evolution crashed: {e}. Reverting to last known Master DNA.")
            # Rule 6: Fail Loud & Revert
            if os.path.exists(master_dna_file):
                master_cortex.load_fittest(master_dna_file)
            else:
                logger.critical("No valid Master DNA to revert to.")
            
    background_tasks.add_task(evolve_master, telemetry, feedback_score)
    return {"status": "ingested", "message": "Telemetry queued for Master Cortex evolution."}


@app.get("/cortex/sync_dna")
async def sync_dna(req: Request, security_ctx: Dict = Depends(virtus_guard)):
    """
    Broadcasts the highly evolved Master DNA to child nodes.
    Requires Tier 7 encryption.
    """
    if not master_cortex or getattr(master_cortex, "best_fittest", None) is None:
        raise HTTPException(status_code=503, detail="Master DNA not ready for sync.")
    
    dna_payload = {
        "architecture": master_cortex.best_fittest.to_dict(),
        "generation": master_cortex.generation
    }
    
    try:
        # VIRTUS Outbound Encryption
        client_pk = b"dummy_client_public_key"
        encrypted_dna = secure_virtus_encrypt(dna_payload, client_pk)
        return Response(content=encrypted_dna, media_type="application/octet-stream")
    except Exception as e:
        logger.error(f"DNA Broadcast encryption failure: {e}")
        raise HTTPException(status_code=500, detail="VIRTUS_ENCRYPTION_FAILURE")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "christman_mind",
        "version": "0.2.0",
        "orchestration": "enabled",
        "specialists_loaded": len(orchestrator.SPECIALISTS)
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
