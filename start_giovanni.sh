#!/bin/bash
echo "🚀 Launching Giovanni Skyrider Ecosystem..."

# 1. Start the Python Backend (The Silicon Spine)
python3 giuseppe_core.py & 

# 2. Wait for backend to bind to port 8001
sleep 2 

# 3. Start the Vite Frontend (The Carbon Interface)
npm run dev
