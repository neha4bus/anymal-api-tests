#!/usr/bin/env bash

# Export library path.
export LD_LIBRARY_PATH="/opt/ros/noetic/lib:/opt/ros/noetic/lib/x86_64-linux-gnu"

# Client automatically reconnects to the server, there is no need to wait for it.

# Waiting for the roscore to be started.
echo "Wait for the roscore."
while ! nc -z localhost 11311; do
  sleep 1
done
echo "The roscore is up."

# Run the agent with the given options.
echo "Command:"
echo "--------"
echo "rosrun anymal_data_sync_agent ads_agentd --log-level ${LOG_LEVEL} --server ${SERVER_URL}:${SERVER_PORT} --id anymal-${ANYMAL_NAME}-${ANYMAL_PC} --credentials-dir ${CREDENTIALS_DIR}"
echo "Output:\n"
echo "-------"
/opt/ros/noetic/lib/anymal_data_sync_agent/ads_agentd --log-level ${LOG_LEVEL} --server ${SERVER_URL}:${SERVER_PORT} --id anymal-${ANYMAL_NAME}-${ANYMAL_PC} --credentials-dir ${CREDENTIALS_DIR}
