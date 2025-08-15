cmake_minimum_required(VERSION 3.16.3)
project(inspection_example_msgs)

if("$ENV{ROS_VERSION}" STREQUAL "1")
  set(
    CATKIN_PACKAGE_DEPENDENCIES
    actionlib_msgs
    environment_item_msgs
    geometry_msgs
    message_generation
    std_msgs
  )

  find_package(catkin REQUIRED COMPONENTS ${CATKIN_PACKAGE_DEPENDENCIES})

  add_message_files(
    DIRECTORY
      msg
    FILES
      Item.msg
  )

  add_action_files(
    DIRECTORY
      action
    FILES
      InspectItem.action
  )

  generate_messages(
    DEPENDENCIES
      actionlib_msgs
      environment_item_msgs
      geometry_msgs
      std_msgs
  )

  catkin_package(
    CATKIN_DEPENDS
      actionlib_msgs
      environment_item_msgs
      geometry_msgs
      message_runtime
      std_msgs
  )
else() # ROS version 2
  ###############
  ## Configure ##
  ###############
  set(
    PACKAGE_DEPENDENCIES
    std_msgs
    geometry_msgs
    actionlib_msgs
    environment_item_msgs
  )

  find_package(ament_cmake REQUIRED)
  find_package(rosidl_default_generators)
  foreach(PKG ${PACKAGE_DEPENDENCIES})
    find_package(${PKG} REQUIRED)
  endforeach()
  add_action_files(
    OUTPUT_LIST GENERATED_MESSAGE_TYPES
    FILES
      InspectItem.action
  )
  rosidl_generate_interfaces(
    ${PROJECT_NAME}
    "msg/Item.msg"
    "action/InspectItem.action"
    ${GENERATED_MESSAGE_TYPES}
    DEPENDENCIES
      ${PACKAGE_DEPENDENCIES}
  )

  ament_export_dependencies(${PACKAGE_DEPENDENCIES})
  install(
    TARGETS
      DESTINATION
      lib/${PROJECT_NAME}
  )

  ament_package()
endif()
