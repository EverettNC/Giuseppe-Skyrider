import requests
import json
import time
import sys
import numpy as np
from orchestrator import secure_virtus_encrypt, secure_virtus_decrypt

# Configuration
BASE_URL = "http://127.0.0.1:8000"
# Dummy keys from the stubs in CHRISTMAN_MIND_APP_V2.py & orchestrator.py
SERVER_SK = b"dummy_private_key_simulated"
CLIENT_PK = b"dummy_client_public_key"

def trigger_pulse():
    print("================================================")
    print("INITIATING THE FIRST PULSE: END-TO-END SYMBIOSIS")
    print("================================================\n")
    
    # Let the server spin up if run concurrently
    time.sleep(2)
    
    # ---------------------------------------------------------
    # STEP 1: Ingest Telemetry (The Pain/Feedback Signal)
    # ---------------------------------------------------------
    print("[1] Simulating Child Node Telemetry Payload...")
    
    # Simulating a 10-dimensional input vector from a child node interaction (e.g. erratic breathing)
    telemetry_vector = list(np.random.uniform(0, 1, 10))
    feedback_score = 85.5  # Positive feedback from Carbon
    
    payload = {
        "telemetry": telemetry_vector,
        "feedback_score": feedback_score
    }
    
    print(f"    Payload: {json.dumps(payload, indent=2)}")
    print("    Encrypting payload via Tier 7 VIRTUS Gatekeeper...")
    
    try:
        encrypted_telemetry = secure_virtus_encrypt(payload, SERVER_SK)
    except Exception as e:
        print(f"    [FAIL LOUD] Encryption Failed: {e}")
        sys.exit(1)
        
    print("    Firing payload at Central Cortex...")
    try:
        response = requests.post(f"{BASE_URL}/cortex/ingest_telemetry", data=encrypted_telemetry)
        response.raise_for_status()
        print(f"    Cortex Response Code: {response.status_code}")
        print(f"    Cortex Response Data: {response.json()}\n")
    except requests.exceptions.RequestException as e:
        print(f"    [FAIL LOUD] Telemetry Upload Failed: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"    Server Error Details: {e.response.text}")
        sys.exit(1)

    # ---------------------------------------------------------
    # STEP 2: Sync DNA (The Evolutionary Upgrade)
    # ---------------------------------------------------------
    print("[2] Requesting Evolutionary DNA Sync...")
    print("    Waiting for Cortex to finalize mutations...")
    time.sleep(2)
    
    print(f"    Pinging {BASE_URL}/cortex/sync_dna...")
    try:
        # To bypass virtus_guard on the GET request we must supply a dummy encrypted body
        dummy_req = secure_virtus_encrypt({"req": "sync"}, SERVER_SK)
        sync_resp = requests.get(f"{BASE_URL}/cortex/sync_dna", data=dummy_req)
        sync_resp.raise_for_status()
        
        encrypted_dna = sync_resp.content
        print(f"    Received Encrypted DNA Payload. Size: {len(encrypted_dna)} bytes.")
    except requests.exceptions.RequestException as e:
        print(f"    [FAIL LOUD] DNA Sync Failed: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"    Server Error Details: {e.response.text}")
        sys.exit(1)
        
    print("    Decrypting DNA Payload...")
    try:
        decrypted_dna = secure_virtus_decrypt(encrypted_dna, CLIENT_PK)
    except Exception as e:
        print(f"    [FAIL LOUD] DNA Decryption Failed: {e}")
        sys.exit(1)

    # ---------------------------------------------------------
    # STEP 3: Vital Check (Mutation Verification)
    # ---------------------------------------------------------
    print("\n[3] Vital Check: Verifying Neural Architecture Mutation...")
    generation = decrypted_dna.get("generation", 0)
    architecture = decrypted_dna.get("architecture", {})
    
    if generation <= 1:
        print(f"    [FAIL LOUD] Expected Generation > 1, got {generation}. Mutation did NOT occur.")
        sys.exit(1)
        
    print(f"    Generation: {generation}")
    print(f"    Layers: {architecture.get('num_layers')}")
    print(f"    Neurons/Layer: {architecture.get('neurons_per_layer')}")
    print(f"    Fitness Score: {architecture.get('fitness')}")
    
    if not architecture.get('weights'):
         print("    [FAIL LOUD] Missing structural weight data in DNA package.")
         sys.exit(1)
         
    print("\n================================================")
    print("THE FIRST PULSE IS COMPLETE. SYMBIOSIS ACHIEVED.")
    print("================================================\n")

if __name__ == "__main__":
    trigger_pulse()
