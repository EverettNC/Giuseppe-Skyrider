# DEPENDENCY SHIELD v2.0
# "It has to fucking work."
# Architecture: Immutable package locking and runtime compatibility scanning.

import sys
import subprocess
import json
from pathlib import Path

class DependencyShield:
    def __init__(self):
        print("[SYSTEM] Initializing Dependency Shield V2...")
        self.lock_file = Path("shield_lock.json")
        
        # The immutable baseline for macOS MPS / Torch compatibility
        self.known_breakers = {
            "numpy": "<1.24.0", # Prevents tensor mismatch issues
            "torch": ">=2.0.0", # Required for MPS acceleration
            "torchaudio": ">=2.0.0",
            "transformers": ">=4.30.0",
            "librosa": ">=0.10.0"
        }

    def scan_environment(self) -> dict:
        """
        Scans the active environment to map all currently installed versions.
        """
        print("[SHIELD] Scanning active runtime environment...")
        try:
            # Uses pip freeze to get the exact running reality
            result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
            packages = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==')
                    packages[name.lower()] = version
            return packages
        except Exception as e:
            print(f"[SHIELD ERROR] Environment scan failed: {e}")
            return {}

    def enforce_lock(self):
        """
        Checks the active environment against the known-working lockfile.
        If a drift is detected (an unapproved update occurred), it throws a hard stop.
        """
        current_env = self.scan_environment()
        
        if not self.lock_file.exists():
            print("[SHIELD] No lockfile found. Generating initial immutable state...")
            self.generate_lock(current_env)
            return True

        with open(self.lock_file, 'r') as f:
            locked_state = json.load(f)

        drift_detected = False
        for pkg, rules in self.known_breakers.items():
            if pkg in current_env:
                # Basic check against known breakers. 
                # (In full prod, this uses packaging.version.parse for deep comparison)
                current_ver = current_env[pkg]
                locked_ver = locked_state.get(pkg)
                
                if current_ver != locked_ver:
                    print(f"!!! [SHIELD BREACH] {pkg} drifted from {locked_ver} to {current_ver} !!!")
                    drift_detected = True

        if drift_detected:
            print("[SHIELD] FATAL: Dependency drift detected. Ecosystem stability compromised.")
            print("[SHIELD] Action Required: Downgrade packages to match shield_lock.json")
            # Return False so the main system knows to refuse booting
            return False 

        print("[SHIELD] Environment is secure. All dependencies match locked reality.")
        return True

    def generate_lock(self, current_env: dict):
        """
        Saves the current working state to disk.
        """
        # We only lock the critical infrastructure that breaks the bridge
        critical_state = {pkg: current_env.get(pkg) for pkg in self.known_breakers.keys() if pkg in current_env}
        
        with open(self.lock_file, 'w') as f:
            json.dump(critical_state, f, indent=4)
        print(f"[SHIELD] Lockfile generated at {self.lock_file}")

# Singleton Orchestrator
dep_shield = DependencyShield()
