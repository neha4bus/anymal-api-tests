#!/usr/bin/env bash

# Sourcing.
source /opt/ros/noetic/setup.bash

# Waiting for the roscore to be started.
echo "Wait for roscore."
while ! nc -z localhost 11311; do
  sleep 1
done
echo "Roscore is up."

# Run the bagfile.
args=${@}
echo "Command:"
echo "--------"
echo "/opt/ros/noetic/lib/rosbag/play ${args} --wait-for-subscribers"
echo "Output:\n"
echo "-------"
/opt/ros/noetic/lib/rosbag/play /share/bagfile.bag ${args} --wait-for-subscribers
