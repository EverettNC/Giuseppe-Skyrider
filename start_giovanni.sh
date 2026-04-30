#!/bin/bash
# GIUSEPPE SKYRIDER BOOT SEQUENCE
# "Nothing Vital Lives Below Root" - Environment Auto-Silo
# Target Hardware: Apple Silicon (MPS Native)

# 1. Access the Conda logic (Assuming default miniconda path)
source ~/miniconda3/etc/profile.d/conda.sh

# 2. Silently activate the stable silo
conda activate skyrider

echo "========================================="
echo "🚀 LAUNCHING SKYRIDER ECOSYSTEM"
echo "========================================="

# 3. Boot the Brain (Python Backend)
# We use 'python' here because the skyrider silo is active
python giuseppe_core.py &

# 4. Wait a beat for the backend to claim its hardware
sleep 2

# 5. Boot the Face (Vite Frontend)
npm run dev
