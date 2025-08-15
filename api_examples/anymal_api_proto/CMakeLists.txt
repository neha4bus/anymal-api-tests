cmake_minimum_required(VERSION 3.5.1)
project(anymal_api_proto)

if("$ENV{ROS_VERSION}" STREQUAL "1")
    find_package(catkin REQUIRED)

    catkin_package(
      CFG_EXTRAS
        proto_sources.cmake
    )

    #############
    ## Install ##
    #############

    install(
        DIRECTORY proto
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
        FILES_MATCHING
        PATTERN "*.proto"
    )

    install(DIRECTORY cmake DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})

    ###########
    ## Clang ##
    ###########

    find_package(cmake_clang_tools QUIET)
    if(cmake_clang_tools_FOUND)
        add_default_clang_tooling()
    endif(cmake_clang_tools_FOUND)
else() # ROS version 2
    ###############
    ## Configure ##
    ###############

    set(PACKAGE_DEPENDENCIES)

    find_package(ament_cmake REQUIRED)
    foreach(PKG IN LISTS PACKAGE_DEPENDENCIES)
        find_package(${PKG} REQUIRED)
    endforeach()

    #############
    ## Install ##
    #############

    install(
        DIRECTORY proto
        DESTINATION share/${PROJECT_NAME}
        FILES_MATCHING
        PATTERN "*.proto"
    )

    install(DIRECTORY cmake DESTINATION share/${PROJECT_NAME})

    ament_export_dependencies(${PACKAGE_DEPENDENCIES})

    ament_package(
      CONFIG_EXTRAS "cmake/proto_sources.cmake"
    )
endif()
