#!/bin/bash
# Blogger Tools — click to launch

cd "$(dirname "$0")"

# Open browser after a short delay (gives Flask time to start)
(sleep 2 && xdg-open http://localhost:5000) &

python3 app.py
