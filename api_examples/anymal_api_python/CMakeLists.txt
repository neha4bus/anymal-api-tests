cmake_minimum_required(VERSION 3.13)
project(anymal_api_python)

find_package(catkin REQUIRED
  COMPONENTS
    anymal_api_proto
)

find_package(Protobuf 3 REQUIRED)

catkin_python_setup()

catkin_package()

# Generate absolute paths to the proto files, required by protobuf_generate().
foreach (ANYMAL_API_PROTO_FILE ${ANYMAL_API_PROTO_FILES})
  list(APPEND ANYMAL_API_PROTO_PATHS "${ANYMAL_API_PROTO_DIR}/${ANYMAL_API_PROTO_NAMESPACE}/${ANYMAL_API_PROTO_FILE}")
endforeach()

# Delete the generated files before generating them again, except for __init__.py.
file(GLOB_RECURSE GENERATED_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/${ANYMAL_API_PROTO_NAMESPACE}/*.py)
list(FILTER GENERATED_FILES EXCLUDE REGEX ".*__init__.py")
if (GENERATED_FILES)
  add_custom_target(delete-python-files ALL
    COMMAND ${CMAKE_COMMAND} -E remove ${GENERATED_FILES}
  )
endif()

# Now generate the files.
protobuf_generate(
  OUT_VAR PY_SOURCES
  LANGUAGE python
  IMPORT_DIRS ${ANYMAL_API_PROTO_DIR}
  PROTOS ${ANYMAL_API_PROTO_PATHS}
  PROTOC_OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src
)
set(GENERATION_DEPENDENCIES ${PY_SOURCES})
if (GENERATED_FILES)
  set (GENERATION_DEPENDENCIES ${GENERATION_DEPENDENCIES} delete-python-files)
endif()
add_custom_target(generate-python-files ALL
  DEPENDS ${GENERATION_DEPENDENCIES}
)

if(CATKIN_ENABLE_TESTING)
  find_package(cmake_python_coverage REQUIRED)
  add_pytest_with_coverage(test/test_generated_code.py ${ANYMAL_API_PROTO_NAMESPACE})
endif()
