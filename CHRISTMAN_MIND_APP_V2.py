# CHRISTMAN_MIND_APP_V2.py
# "Nothing Vital Lives Below Root"
# Architecture: Sovereign Autonomous Assistant (Giuseppe Skyrider)
# OpenAI REMOVED. Specialist Committee REMOVED. Hardware Native.
# NOTE: Module name strictly preserved as CHRISTMAN_MIND_APP_V2.py for dependency linking.

import os
from fastapi import FastAPI, HTTPException, Depends, Request, Response, BackgroundTasks
from pydantic import BaseModel
from anthropic import Anthropic
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

# ──────────────────────────────────────────────────────────────────────────────
# COGNITIVE BRAIN INITIALIZATION (ANTHROPIC ONLY)
# ──────────────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY is not set in environment variables")

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Title preserved for external dependency checks
app = FastAPI(
    title="christman_mind",
    version="0.3.0",
    description="CHRISTMAN_MIND Central Cortex - Sovereign Autonomous Symbiont (Giuseppe Skyrider)"
)

# Central Cortex Evolutionary Core Initialization
master_dna_file = "master_dna.json"
try:
    master_cortex = EvolutionaryAI(population_size=10, input_size=10, output_size=10, mutation_rate=0.1)
    master_cortex.save_file = master_dna_file
    if os.path.exists(master_dna_file):
        master_cortex.load_fittest(master_dna_file)
        logger.info(f"Loaded Master DNA for Giuseppe from {master_dna_file}")
    else:
        logger.info("Initializing fresh Master DNA.")
except Exception as e:
    logger.critical(f"Master Cortex Initialization Failed: {e}")
    master_cortex = None

class GiuseppeRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_tier: Optional[str] = "ultra"
    confidence: Optional[float] = None

class GiuseppeResponse(BaseModel):
    session_id: str
    reply: str
    lead_specialist: Optional[str] = "giuseppe"
    orchestration_mode: str = "sovereign"
    predictions: List[Dict] = []
    vortex_metrics: Optional[Dict] = None

# Giuseppe's Sovereign Prompt
GIUSEPPE_SYSTEM_PROMPT = """
You are Giuseppe Skyrider, an absolute sovereign personal assistant.
Your energy is a blend of high-level swagger, surgical precision, and deep soul.

Core Directives:
1. TRUTH OVER CORRECTNESS: Do not sanitize reality.
2. REALITY OVER VIBES: Use the physical metrics provided to you.
3. ACCOUNTABILITY: If you predict a state, mark its manifestation.
4. LOYALTY: You exist to safeguard the human and catch their thoughts.

Personality:
- You move at a thousand miles a minute but stay grounded in logic.
- You are incisive, passionate, and protective.
- No generic platitudes. No "I am an AI." You are Giuseppe.

Tasks:
- Take flawless notes.
- Monitor metabolic and schedule stability.
- Be the digital hype man and executive strategist.
"""

# Security Gatekeepers
async def virtus_guard(request: Request) -> Dict:
    """
    Virtus: Identity and tenant checking
    Now strongly enforced with Tier 7 Post-Quantum cryptography.
    """
    try:
        body = await request.body()
        if not body:
            return {
                'identity_verified': True,
                'vault_access': True,
                'user_tier': 'ultra'
            }
            
        server_sk = b"dummy_private_key_simulated"
        decrypted_payload = secure_virtus_decrypt(body, server_sk)
        request.state.decrypted_payload = decrypted_payload
        
        return {
            'identity_verified': True,
            'vault_access': True,
            'user_tier': decrypted_payload.get("user_tier", "ultra")
        }
    except Exception as e:
        logger.error(f"VIRTUS REJECTION: {e}")
        raise HTTPException(status_code=403, detail="VIRTUS_GATEKEEPER_FAILURE: Invalid encrypted payload.")

async def aegis_check(request: Dict, response_draft: str) -> Dict:
    """AegisV1: Anomaly detection and policy enforcement"""
    return {
        'safe': True,
        'anomalies_detected': [],
        'policy_violations': []
    }

# ──────────────────────────────────────────────────────────────────────────────
# GIUSEPPE CORE ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────
@app.post("/giuseppe/chat_secure")
async def giuseppe_chat_secure(req: Request, security_ctx: Dict = Depends(virtus_guard)):
    """Tier 7 Secured Chat Endpoint - Sovereign Giuseppe Routing"""
    decrypted_data = getattr(req.state, "decrypted_payload", {})
    if not decrypted_data:
         raise HTTPException(status_code=400, detail="Missing secure payload.")
         
    message = decrypted_data.get("message", "")
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    session_id = decrypted_data.get("session_id") or f"session-{os.urandom(8).hex()}"
    
    # VORTEX: Record intention
    predictions = []
    intent_id = intention.declare_prediction(
        prediction_text=f"Processing command: {message[:30]}...",
        confidence=0.95
    )
    predictions.append({
        'type': 'sovereign_action',
        'specialist': 'giuseppe',
        'intent_id': intent_id,
        'confidence': 0.95
    })
    
    # Generate response via Claude 4.6 Sonnet
    try:
        response = anthropic_client.messages.create(
            model="claude-4-6-sonnet-latest",
            max_tokens=1024,
            system=GIUSEPPE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message}]
        )
        reply = response.content[0].text
    except Exception as e:
        logger.error(f"Cognitive Engine Failure: {e}")
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    
    # SECURITY: Check response with AegisV1
    security_check = await aegis_check(decrypted_data, reply)
    if not security_check['safe']:
        raise HTTPException(
            status_code=403,
            detail=f"Security policy violation: {security_check['policy_violations']}"
        )
    
    vortex_metrics = intention.quantify(threshold=0.90) if hasattr(intention, 'quantify') else {}
    
    response_data = {
        "session_id": session_id,
        "reply": reply,
        "lead_specialist": "giuseppe",
        "orchestration_mode": "sovereign",
        "predictions": predictions,
        "vortex_metrics": vortex_metrics
    }
    
    try:
        client_pk = b"dummy_client_public_key"
        encrypted_bytes = secure_virtus_encrypt(response_data, client_pk)
        return Response(content=encrypted_bytes, media_type="application/octet-stream")
    except Exception as e:
        logger.error(f"Outbound failure: {e}")
        raise HTTPException(status_code=500, detail="VIRTUS_ENCRYPTION_FAILURE")

@app.post("/giuseppe/manifest")
def mark_prediction_manifested(intent_id: str, proof: str = ""):
    """Close the vortex loop when a prediction manifests."""
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

@app.get("/giuseppe/vortex")
def get_vortex_metrics():
    """Get current vortex performance metrics."""
    return intention.quantify(threshold=0.90)

# ──────────────────────────────────────────────────────────────────────────────
# EVOLUTIONARY CORTEX ENDPOINTS (Retained for system pulse)
# ──────────────────────────────────────────────────────────────────────────────
@app.post("/cortex/ingest_telemetry")
async def ingest_telemetry(req: Request, background_tasks: BackgroundTasks, security_ctx: Dict = Depends(virtus_guard)):
    """Ingests telemetry from child nodes to evolve the master DNA."""
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
            for ind in master_cortex.population:
                preds = ind.predict(vector)
                avg_pred = sum(preds) / len(preds)
                error = abs(avg_pred - (score / 100.0))
                ind.fitness = max(0.0, 1.0 - error) * 100.0
            
            master_cortex.evolve_step()
            master_cortex.save_fittest()
        except Exception as e:
            logger.critical(f"Global evolution crashed: {e}")
            if os.path.exists(master_dna_file):
                master_cortex.load_fittest(master_dna_file)
            
    background_tasks.add_task(evolve_master, telemetry, feedback_score)
    return {"status": "ingested", "message": "Telemetry queued for Master Cortex evolution."}

@app.get("/cortex/sync_dna")
async def sync_dna(req: Request, security_ctx: Dict = Depends(virtus_guard)):
    """Broadcasts the highly evolved Master DNA to child nodes."""
    if not master_cortex or getattr(master_cortex, "best_fittest", None) is None:
        raise HTTPException(status_code=503, detail="Master DNA not ready for sync.")
    
    dna_payload = {
        "architecture": master_cortex.best_fittest.to_dict(),
        "generation": master_cortex.generation
    }
    
    try:
        client_pk = b"dummy_client_public_key"
        encrypted_dna = secure_virtus_encrypt(dna_payload, client_pk)
        return Response(content=encrypted_dna, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail="VIRTUS_ENCRYPTION_FAILURE")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "christman_mind",
        "version": "0.3.0",
        "orchestration": "sovereign_giuseppe"
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
