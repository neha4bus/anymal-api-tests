cmake_minimum_required(VERSION 3.5.1)
project(playground_data)

if("$ENV{ROS_DISTRO}" STREQUAL "noetic")

  # Perform a ROS dependent build (legacy).
  find_package(catkin REQUIRED)

  catkin_package()

  install(
    DIRECTORY
      configs
      environments
      missions
      models
      slam_maps
      waypoints
      worlds
    DESTINATION
      ${CATKIN_PACKAGE_SHARE_DESTINATION}
  )

else()

  # Perform a ROS independent build.
  install(
    DIRECTORY
      configs
      environments
      missions
      models
      slam_maps
      waypoints
      worlds
    DESTINATION
      ${CMAKE_INSTALL_PREFIX}/share/playground_data
  )

endif()
