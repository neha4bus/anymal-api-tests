# Project configuration
cmake_minimum_required(VERSION 3.5.1)
project(anymal_sdk_python_example)

find_package(catkin REQUIRED COMPONENTS)

catkin_package()

catkin_python_setup()

catkin_install_python(
  PROGRAMS
    bin/anymal_state_example
    bin/anymal_physical_condition_example
    bin/auditive_example
    bin/connection_example
    bin/control_authority_example
    bin/control_example
    bin/control_status_example
    bin/inspection_example
    bin/mission_example
    bin/thermal_image_example
  DESTINATION
    ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(
  FILES
    bin/thermal_image_example.npy
    bin/audio_sample.wav
    bin/liveview_example.py
  DESTINATION
    ${CATKIN_PACKAGE_BIN_DESTINATION}
)
