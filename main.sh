#!/bin/bash

# tmux kill-session -t "Life_of_Game"
tmux new-session -s "Life_of_Game" -n "Client" -d
tmux send-keys -t "Life_of_Game:0" './client -D' ENTER
tmux send-keys -t "Life_of_Game:0" 'status=$?' ENTER
tmux send-keys -t "Life_of_Game:0" 'if [ $status -ne 0 ]; then' ENTER
tmux send-keys -t "Life_of_Game:0" '  echo "Failed to start client: $status"' ENTER
tmux send-keys -t "Life_of_Game:0" '  exit $status' ENTER
tmux send-keys -t "Life_of_Game:0" 'fi' ENTER
sleep 1

# New version doesn't use the real server anymore
# tmux new-window -t "Life_of_Game:1" -n "Server"
# tmux send-keys -t "Life_of_Game:1" './server -D' ENTER
# tmux send-keys -t "Life_of_Game:1" 'status=$?' ENTER
# tmux send-keys -t "Life_of_Game:1" 'if [ $status -ne 0 ]; then' ENTER
# tmux send-keys -t "Life_of_Game:1" '  echo "Failed to start server: $status"' ENTER
# tmux send-keys -t "Life_of_Game:1" '  exit $status' ENTER
# tmux send-keys -t "Life_of_Game:1" 'fi' ENTER
# sleep 1

# Naive check runs checks once a minute to see if either of the processes exited.
# This illustrates part of the heavy lifting you need to do if you want to run
# more than one service in a container. The container exits with an error
# if it detects that either of the processes has exited.
# Otherwise it loops forever, waking up every 60 seconds

while sleep 60; do
  ps aux |grep server |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep client |grep -q -v grep
  PROCESS_2_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done


