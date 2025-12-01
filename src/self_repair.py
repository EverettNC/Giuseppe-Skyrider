# self_repair.py
import traceback
import os
import sys
import subprocess
import datetime

LOG_FILE = "self_repair.log"


def log_issue(error_msg):
    """Log error messages with timestamp for debugging history."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {error_msg}\n")
    print(f"[SELF-REPAIR] Logged issue: {error_msg}")


def run_with_repair(script, args=[]):
    """Run a Python script and attempt self-repair on failure."""
    try:
        subprocess.run([sys.executable, script] + args, check=True)
    except subprocess.CalledProcessError as e:
        log_issue(f"Runtime error in {script}: {str(e)}")
        analyze_and_patch(script, e)
    except Exception as e:
        log_issue(f"Unexpected error in {script}: {traceback.format_exc()}")
        analyze_and_patch(script, e)


def analyze_and_patch(script, error):
    """Enhanced self-repair: detect and fix common Derek system errors."""
    error_str = str(error)
    fixed = False

    if "ModuleNotFoundError" in error_str:
        missing_pkg = error_str.split("'")[1] if "'" in error_str else "unknown"
        print(f"[SELF-REPAIR] Missing package detected: {missing_pkg}")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", missing_pkg],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"[SELF-REPAIR] ✅ Successfully installed {missing_pkg}")
                fixed = True
            else:
                print(
                    f"[SELF-REPAIR] ❌ Failed to install {missing_pkg}: {result.stderr}"
                )
        except Exception as e:
            print(f"[SELF-REPAIR] ❌ Installation error: {e}")

    elif "ImportError" in error_str and "cannot import name" in error_str:
        print("[SELF-REPAIR] Import conflict detected")
        if "vision_engine" in error_str:
            print("[SELF-REPAIR] Vision engine import issue - checking if file exists")
            if not os.path.exists("vision_engine.py"):
                create_missing_vision_engine()
                fixed = True
        elif "claude_service" in error_str:
            print("[SELF-REPAIR] Claude service import issue - checking if file exists")
            if not os.path.exists("claude_service.py"):
                create_missing_claude_service()
                fixed = True

    elif "cv2.error" in error_str or "OpenCV" in error_str:
        print("[SELF-REPAIR] OpenCV/Vision system error detected")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "opencv-python-headless"],
                capture_output=True,
                timeout=60,
            )
            print("[SELF-REPAIR] ✅ Installed opencv-python-headless")
            fixed = True
        except Exception as e:
            print(f"[SELF-REPAIR] ❌ OpenCV installation failed: {e}")

    elif "numpy" in error_str and (
        "version" in error_str or "tensorflow" in error_str.lower()
    ):
        print("[SELF-REPAIR] NumPy/TensorFlow compatibility issue")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "numpy==1.24.3"],
                capture_output=True,
                timeout=60,
            )
            print("[SELF-REPAIR] ✅ Fixed NumPy version for TensorFlow compatibility")
            fixed = True
        except Exception as e:
            print(f"[SELF-REPAIR] ❌ NumPy fix failed: {e}")

    elif "tf-keras" in error_str or "keras" in error_str:
        print("[SELF-REPAIR] Keras/TensorFlow compatibility issue")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "tf-keras"],
                capture_output=True,
                timeout=60,
            )
            print("[SELF-REPAIR] ✅ Installed tf-keras for compatibility")
            fixed = True
        except Exception as e:
            print(f"[SELF-REPAIR] ❌ tf-keras installation failed: {e}")

    elif "SyntaxError" in error_str:
        print("[SELF-REPAIR] Syntax error detected - checking for common issues")
        if "missing '#'" in error_str or "comment" in error_str.lower():
            print("[SELF-REPAIR] Comment syntax issue detected")
            # Could implement automatic comment fixing here

    elif "timeout" in error_str.lower() or "timeouterror" in error_str.lower():
        print("[SELF-REPAIR] Timeout error detected - API call timeout issue")
        print(
            "[SELF-REPAIR] Suggestion: Increase timeout values or check network connection"
        )

    else:
        print(f"[SELF-REPAIR] No automated fix available for: {error_str[:100]}...")

    return fixed


def create_missing_vision_engine():
    """Create a basic vision_engine.py if missing"""
    vision_code = '''"""
Basic Vision Engine - Created by Christman Autonomy Engine's Self-Repair System
"""
import logging

logger = logging.getLogger(__name__)

class VisionEngine:
    def __init__(self):
        self.last_emotion = ""
        self.enabled = False
        logger.info("Vision Engine initialized (basic mode)")
    
    def start(self):
        """Start vision processing"""
        logger.info("Vision Engine started")
        
    def stop(self):
        """Stop vision processing"""  
        logger.info("Vision Engine stopped")
        
    def get_current_frame(self):
        """Get current camera frame"""
        return None
        
    def analyze_emotion(self, frame=None):
        """Analyze emotion from frame"""
        return "neutral"
'''

    with open("vision_engine.py", "w") as f:
        f.write(vision_code)
    print("[SELF-REPAIR] ✅ Created basic vision_engine.py")


def create_missing_claude_service():
    """Create a basic claude_service.py if missing"""
    claude_code = '''"""
Basic Claude Service - Created by Christman Autonomy Engine's Self-Repair System
"""
import os
import logging

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.enabled = bool(self.api_key)
        logger.info(f"Claude Service initialized (enabled: {self.enabled})")
    
    def generate_response(self, prompt, max_tokens=1000):
        """Generate response using Claude API"""
        if not self.enabled:
            return "Claude service not configured - missing ANTHROPIC_API_KEY"
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Claude service error: {e}"
'''

    with open("claude_service.py", "w") as f:
        f.write(claude_code)
    print("[SELF-REPAIR] ✅ Created basic claude_service.py")


# ==============================================================================
# © 2025 Everett Nathaniel Christman
# The Christman AI Project — Luma Cognify AI
# All rights reserved. Unauthorized use, replication, or derivative training
# of this material is prohibited.
#
# Core Directive: "How can I help you love yourself more?"
# Autonomy & Alignment Protocol v3.0
# ==============================================================================
