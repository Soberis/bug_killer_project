#!/bin/bash

# This is a Linux shell script to start our BugKiller in the background

# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app using nohup
# > server.log: redirect output to a file
# 2>&1: redirect errors to the same file
# &: run in the background
nohup python app.py > server.log 2>&1 &

echo "BugKiller is now running in the background!"
echo "You can check the logs using: tail -f server.log"
