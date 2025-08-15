if("$ENV{ROS_VERSION}" STREQUAL "1")
  if(NOT anymal_api_proto_INSTALL_PREFIX STREQUAL "")
    # There is an install space (either in /opt/ros or in the catkin workspace).
    set(ANYMAL_API_PROTO_DIR ${anymal_api_proto_INSTALL_PREFIX}/share/anymal_api_proto/proto)
  else()
    # There is no install space.
    set(ANYMAL_API_PROTO_DIR ${anymal_api_proto_SOURCE_PREFIX}/proto)
  endif()
else() # ROS version 2
  set(ANYMAL_API_PROTO_DIR ${CMAKE_CURRENT_LIST_DIR}/../proto)
endif()

set(ANYMAL_API_PROTO_NAMESPACE anymal_api_proto)

set(ANYMAL_API_PROTO_FILES
  assets.proto
  common.proto
  connection.proto
  control.proto
  environment.proto
  error_state.proto
  inspection.proto
  introspection.proto
  liveview.proto
  mission_description.proto
  mission.proto
  navigation.proto
  spatial.proto
  state_estimation.proto
  subscribe.proto
  task.proto
  user_notification.proto
)
