#!/usr/bin/env bash

# Export python package and library paths.
export PYTHONPATH="/opt/ros/noetic/lib/python3/dist-packages"
export LD_LIBRARY_PATH="/opt/ros/noetic/lib:/opt/ros/noetic/lib/x86_64-linux-gnu"

# Client will not reconnect, we need to wait for the server.
echo "Wait for API server."
while ! nc -z ${SERVER_URL} ${SERVER_PORT}; do
  sleep 0.1
done
echo "API server is up."

# Run the specified example.
executable_with_args=${@:-"connection_example"}
echo "Command:"
echo "--------"
echo "/opt/ros/noetic/lib/anymal_sdk_python_example/${executable_with_args} --log-level ${LOG_LEVEL} --server ${SERVER_URL}:${SERVER_PORT} --credentials-dir ${CREDENTIALS_DIR}"
echo "Output:\n"
echo "-------"
/opt/ros/noetic/lib/anymal_sdk_python_example/${executable_with_args} --log-level ${LOG_LEVEL} --server ${SERVER_URL}:${SERVER_PORT} --credentials-dir ${CREDENTIALS_DIR}
