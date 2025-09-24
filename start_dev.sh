#!/bin/bash

# Kill existing session if it exists
tmux kill-session -t chautari 2>/dev/null

# Create a new tmux session named 'chautari'
tmux new-session -d -s chautari

# Split the window vertically (top and bottom)
tmux split-window -v

# Split the bottom pane horizontally (left and right)
tmux split-window -h

# Run commands in each pane
# Top pane: make run
tmux select-pane -t 0
tmux send-keys 'make worker' Enter

# Bottom left pane: make worker
tmux select-pane -t 1  
tmux send-keys 'make run' Enter

# Bottom right pane: make beat
tmux select-pane -t 2
tmux send-keys 'make beat' Enter

# Focus on the top pane
tmux select-pane -t 0

# Attach to the session
tmux attach-session -t chautari