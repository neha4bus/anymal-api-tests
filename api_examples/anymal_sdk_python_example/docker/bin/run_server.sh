#!/usr/bin/env bash

# Export library path.
export LD_LIBRARY_PATH="/opt/ros/noetic/lib:/opt/ros/noetic/lib/x86_64-linux-gnu"

# Run the server.
echo "Command:"
echo "--------"
echo "/opt/ros/noetic/lib/anymal_data_sync_server/ads_serverd --log-level ${LOG_LEVEL} --insecure --ephemeral --unauthenticated --server-cert ${CREDENTIALS_DIR}/root.crt"
echo "Output:\n"
echo "-------"
/opt/ros/noetic/lib/anymal_data_sync_server/ads_serverd --log-level ${LOG_LEVEL} --insecure --ephemeral --unauthenticated --ca-cert ${CREDENTIALS_DIR}/root.crt --server-cert ${CREDENTIALS_DIR}/ads.local.crt
