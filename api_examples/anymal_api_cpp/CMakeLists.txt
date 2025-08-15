cmake_minimum_required(VERSION 3.16.3)
project(anymal_api_cpp)

if("$ENV{ROS_VERSION}" STREQUAL "1")
  # gersemi: off

# Compilation options.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_compile_options(-Wall -Wextra -Wpedantic)

## Create a list of catkin package dependencies used in header files of this package.
set(CATKIN_PACKAGE_HEADER_DEPENDENCIES
)

## Create a list of catkin package dependencies, now for both header and source files.
set(CATKIN_PACKAGE_DEPENDENCIES
  ${CATKIN_PACKAGE_HEADER_DEPENDENCIES}
  anymal_api_proto
)

# Find gRPC installation. gRPC links against Threads::Threads
find_package(PkgConfig REQUIRED)
pkg_check_modules(gRPC REQUIRED IMPORTED_TARGET grpc++)
find_package(Threads REQUIRED)

# Find Protobuf installation.
find_package(Protobuf 3 REQUIRED)

# Directory for generated headers in build space.
if (DEFINED CATKIN_DEVEL_PREFIX)
set(protocol_INCLUDE_DIR "${CATKIN_DEVEL_PREFIX}/${CATKIN_GLOBAL_INCLUDE_DESTINATION}")
else()
# For Debian generation 'CATKIN_DEVEL_PREFIX' and 'CATKIN_GLOBAL_INCLUDE_DESTINATION' are not defined.
# This would result in a '/' include path. To avoid this, we set the include path to a temporary directory in the source directory.
# Also we handle catkin_package() differently in this case to not include that tmp path.
set(protocol_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tmp")
endif()
if(NOT EXISTS ${protocol_INCLUDE_DIR})
  file(MAKE_DIRECTORY ${protocol_INCLUDE_DIR})
endif()

## Find catkin dependencies for building this package.
find_package(catkin REQUIRED
  COMPONENTS
    ${CATKIN_PACKAGE_DEPENDENCIES}
)

## Define catkin package.
if (DEFINED CATKIN_DEVEL_PREFIX)
catkin_package(
  INCLUDE_DIRS
    # When installed with install space, we need to include this folder:
    include
    # When installed without install space, we need to include this folder:
    ${protocol_INCLUDE_DIR}
  LIBRARIES
    ${PROJECT_NAME}
  CATKIN_DEPENDS
    ${CATKIN_PACKAGE_HEADER_DEPENDENCIES}
  DEPENDS
    Protobuf
    gRPC
)
else()
catkin_package(
  INCLUDE_DIRS
    # When installed with install space, we need to include this folder:
    include
  LIBRARIES
    ${PROJECT_NAME}
  CATKIN_DEPENDS
    ${CATKIN_PACKAGE_HEADER_DEPENDENCIES}
  DEPENDS
    Protobuf
    gRPC
)
endif()

####################
## Build Protobuf ##
####################

# Add Library target with protobuf sources.
# With cmake 3.21, we should be able to use the provided protobuf_generate() with the gRPC plugin instead of maintaining our own macro.
# https://github.com/protocolbuffers/protobuf/blob/main/docs/cmake_protobuf_generate.md#grpc-example
include(cmake/grpc_protobuf_macros.cmake)
generate_grpc_protobuf(
  SOURCE_DIR    ${ANYMAL_API_PROTO_DIR}
  NAMESPACE     ${ANYMAL_API_PROTO_NAMESPACE}
  PROTO_FILES   ${ANYMAL_API_PROTO_FILES}
  OUTPUT_DIR    ${protocol_INCLUDE_DIR}
  PLUGIN_EXE    /usr/bin/grpc_cpp_plugin
  LIBRARY_NAME  ${PROJECT_NAME}
)

#############
## Install ##
#############

## All install targets should use catkin DESTINATION variables.
## See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html.

## Mark executables and/or libraries for installation.
install(
  TARGETS
    ${PROJECT_NAME}
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Mark header files for installation.
install(
  DIRECTORY
    include/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}/..
)

# Mark generated header files for installation.
install(
  DIRECTORY
    ${protocol_INCLUDE_DIR}/anymal_api_proto/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}/../anymal_api_proto
  FILES_MATCHING
    PATTERN "*.pb.h"
)

##########
## Test ##
##########

## GTest.
if (CATKIN_ENABLE_TESTING)
  find_package(catkin REQUIRED
    COMPONENTS
      ${CATKIN_PACKAGE_DEPENDENCIES}
  )

  catkin_add_gtest(test_${PROJECT_NAME}
    test/TestGeneratedCode.cpp
  )
  add_dependencies(test_${PROJECT_NAME}
    ${PROJECT_NAME}
  )
  target_include_directories(test_${PROJECT_NAME} PRIVATE
    include
  )
  target_include_directories(test_${PROJECT_NAME} SYSTEM PUBLIC
    ${protocol_INCLUDE_DIR}
    ${catkin_INCLUDE_DIRS}
  )
  target_link_libraries(test_${PROJECT_NAME}
    gtest_main
    ${PROJECT_NAME}
    ${catkin_LIBRARIES}
    ${Protobuf_LIBRARIES}
    ${gRPC_LIBRARIES}
  )

  ## Generate test coverage report -> ${PROJECT_BINARY_DIR}/cmake_code_coverage/${PROJECT_NAME}/index.html
  find_package(cmake_code_coverage QUIET)
  if (cmake_code_coverage_FOUND)
    add_gtest_coverage(
      TEST_BUILD_TARGETS
        test_${PROJECT_NAME}
    )
  endif (cmake_code_coverage_FOUND)
endif ()

###########
## Clang ##
###########

find_package(cmake_clang_tools QUIET)
if (cmake_clang_tools_FOUND)
  add_default_clang_tooling()
endif (cmake_clang_tools_FOUND)

  # gersemi: on
else() # ROS version 2
  ###############
  ## Configure ##
  ###############

  # Compilation options.
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
  add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
  )

  set(protocol_INCLUDE_DIR "${CMAKE_BINARY_DIR}/protobuf_out")
  if(NOT EXISTS ${protocol_INCLUDE_DIR})
    file(MAKE_DIRECTORY ${protocol_INCLUDE_DIR})
  endif()

  set(
    PACKAGE_DEPENDENCIES
    anymal_api_proto
    PkgConfig
    Threads
  )

  find_package(ament_cmake REQUIRED)
  find_package(Protobuf 3 REQUIRED)
  foreach(PKG ${PACKAGE_DEPENDENCIES})
    find_package(${PKG} REQUIRED)
  endforeach()

  # Find gRPC installation. gRPC links against Threads::Threads
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(gRPC REQUIRED IMPORTED_TARGET grpc++)
  ####################
  ## Build Protobuf ##
  ####################

  # Add Library target with protobuf sources.
  # With cmake 3.21, we should be able to use the provided protobuf_generate() with the gRPC plugin instead of maintaining our own macro.
  # https://github.com/protocolbuffers/protobuf/blob/main/docs/cmake_protobuf_generate.md#grpc-example
  include(cmake/grpc_protobuf_macros.cmake)

  generate_grpc_protobuf(
    SOURCE_DIR    ${ANYMAL_API_PROTO_DIR}
    NAMESPACE     ${ANYMAL_API_PROTO_NAMESPACE}
    PROTO_FILES   ${ANYMAL_API_PROTO_FILES}
    OUTPUT_DIR    ${protocol_INCLUDE_DIR}
    PLUGIN_EXE    /usr/bin/grpc_cpp_plugin
    LIBRARY_NAME  ${PROJECT_NAME}
  )
  target_include_directories(
    ${PROJECT_NAME}
    PUBLIC
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
      $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
  )

  target_link_libraries(${PROJECT_NAME} ${Protobuf_LIBRARIES})

  ament_target_dependencies(${PROJECT_NAME} Protobuf gRPC)
  #############
  ## Install ##
  #############

  ## Mark header files for installation.
  install(DIRECTORY include/ DESTINATION include/${PROJECT_NAME})
  # Mark generated header files for installation.
  install(
    DIRECTORY
      ${protocol_INCLUDE_DIR}/anymal_api_proto/
    DESTINATION include/${PROJECT_NAME}/anymal_api_proto
    FILES_MATCHING
    PATTERN
    "*.pb.h"
  )
  ament_export_dependencies(${PACKAGE_DEPENDENCIES})

  ##########
  ## Test ##
  ##########

  ## GTest.
  if(BUILD_TESTING)
    find_package(ament_cmake_gtest REQUIRED)

    ament_add_gtest(test_${PROJECT_NAME} test/TestGeneratedCode.cpp)
    target_link_libraries(test_${PROJECT_NAME} ${PROJECT_NAME})

    ## Generate test coverage report -> ${PROJECT_BINARY_DIR}/cmake_code_coverage/${PROJECT_NAME}/index.html
    find_package(cmake_code_coverage QUIET)
    if(cmake_code_coverage_FOUND)
      add_gtest_coverage(TEST_BUILD_TARGETS test_${PROJECT_NAME})
    endif(cmake_code_coverage_FOUND)
  endif()

  ament_package()
endif()
