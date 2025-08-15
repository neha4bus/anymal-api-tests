cmake_minimum_required(VERSION 3.5.1)
project(state_machine_example)

set(CMAKE_CXX_STANDARD 17)
add_compile_options(-Wall -Wextra -Wpedantic)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CATKIN_PACKAGE_DEPENDENCIES
  actionlib_tutorials
  param_io
  roscpp
  state_machine
  state_machine_ros
)

find_package(catkin REQUIRED
  COMPONENTS
    ${CATKIN_PACKAGE_DEPENDENCIES}
)

catkin_package(
  INCLUDE_DIRS
    include
  LIBRARIES
    ${PROJECT_NAME}
  CATKIN_DEPENDS
    ${CATKIN_PACKAGE_DEPENDENCIES}
)

add_library(${PROJECT_NAME}
  src/${PROJECT_NAME}/CalculateFibonacciSeries.cpp
  src/${PROJECT_NAME}/CalculateTwoFibonacciSeriesSequentially.cpp
)
add_dependencies(${PROJECT_NAME}
  ${catkin_EXPORTED_TARGETS}
)
target_include_directories(${PROJECT_NAME} PRIVATE
  include
)
target_include_directories(${PROJECT_NAME} SYSTEM PUBLIC
  ${catkin_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME}
  ${catkin_LIBRARIES}
)

add_library(${PROJECT_NAME}_plugins
  src/${PROJECT_NAME}/plugins.cpp
)
add_dependencies(${PROJECT_NAME}_plugins
  ${catkin_EXPORTED_TARGETS}
)
target_include_directories(${PROJECT_NAME}_plugins PRIVATE
  include
)
target_include_directories(${PROJECT_NAME}_plugins SYSTEM PUBLIC
  ${catkin_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME}_plugins
  ${PROJECT_NAME}
  ${catkin_LIBRARIES}
)

add_executable(calculate_fibonacci_series
  src/calculate_fibonacci_series.cpp
)
add_dependencies(calculate_fibonacci_series
  ${catkin_EXPORTED_TARGETS}
)
target_include_directories(calculate_fibonacci_series PRIVATE
  include
)
target_include_directories(calculate_fibonacci_series SYSTEM PUBLIC
  ${catkin_INCLUDE_DIRS}
)
target_link_libraries(calculate_fibonacci_series
  ${PROJECT_NAME}
  ${catkin_LIBRARIES}
)

install(
  TARGETS
    ${PROJECT_NAME}
    ${PROJECT_NAME}_plugins
    calculate_fibonacci_series
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(
  DIRECTORY
    include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
)
install(
  DIRECTORY
    config
    launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
install(
  FILES
    state_machine_plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

if(CATKIN_ENABLE_TESTING)
  find_package(catkin REQUIRED
    COMPONENTS
      ${CATKIN_PACKAGE_DEPENDENCIES}
      rostest
  )

  add_rostest_gtest(test_${PROJECT_NAME}_node
    test/ros.test
    test/main.cpp
    test/TestPlugins.cpp
  )
  add_dependencies(test_${PROJECT_NAME}_node
    ${catkin_EXPORTED_TARGETS}
  )
  target_include_directories(test_${PROJECT_NAME}_node PRIVATE
    include
  )
  target_include_directories(test_${PROJECT_NAME}_node SYSTEM PUBLIC
    ${catkin_INCLUDE_DIRS}
  )
  target_link_libraries(test_${PROJECT_NAME}_node
    ${PROJECT_NAME}
    ${catkin_LIBRARIES}
  )

  find_package(cmake_code_coverage QUIET)
  if(cmake_code_coverage_FOUND)
    add_rostest_coverage()
  endif(cmake_code_coverage_FOUND)
endif()

find_package(cmake_clang_tools QUIET)
if(cmake_clang_tools_FOUND)
  add_default_clang_tooling(
    TARGETS
      ${PROJECT_NAME}
      ${PROJECT_NAME}_plugins
      calculate_fibonacci_series
      test_${PROJECT_NAME}_node
  )
endif(cmake_clang_tools_FOUND)
