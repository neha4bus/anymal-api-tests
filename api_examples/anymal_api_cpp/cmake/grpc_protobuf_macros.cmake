macro(generate_grpc_protobuf)

  set(options)
  set(oneValueArgs SOURCE_DIR NAMESPACE OUTPUT_DIR PLUGIN_EXE LIBRARY_NAME)
  set(multiValueArgs PROTO_FILES)
  cmake_parse_arguments(PROTOBUF_GEN "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # Check required input.
  if(NOT PROTOBUF_GEN_SOURCE_DIR OR NOT PROTOBUF_GEN_OUTPUT_DIR OR NOT PROTOBUF_GEN_PLUGIN_EXE OR NOT PROTOBUF_GEN_PROTO_FILES)
    message(FATAL_ERROR "SOURCE_DIR, PROTO_FILES, OUTPUT_DIR and PLUGIN_EXE must be provided.")
  endif()

  # Make sure output directory exists.
  if(NOT EXISTS ${PROTOBUF_GEN_OUTPUT_DIR})
    file(MAKE_DIRECTORY ${PROTOBUF_GEN_OUTPUT_DIR})
  endif()

  foreach (proto_file ${PROTOBUF_GEN_PROTO_FILES})
    # Get file properties.
    get_filename_component(proto_file_path ${PROTOBUF_GEN_SOURCE_DIR}/${PROTOBUF_GEN_NAMESPACE}/${proto_file} ABSOLUTE)
    get_filename_component(proto_file_dir "${PROTOBUF_GEN_SOURCE_DIR}" ABSOLUTE)
    get_filename_component(proto_name ${proto_file} NAME_WE)

    # Define output paths for the generated files.
    set(generated_proto_source "${PROTOBUF_GEN_OUTPUT_DIR}/${PROTOBUF_GEN_NAMESPACE}/${proto_name}.pb.cc")
    set(generated_proto_header "${PROTOBUF_GEN_OUTPUT_DIR}/${PROTOBUF_GEN_NAMESPACE}/${proto_name}.pb.h")
    set(generated_grpc_source "${PROTOBUF_GEN_OUTPUT_DIR}/${PROTOBUF_GEN_NAMESPACE}/${proto_name}.grpc.pb.cc")
    set(generated_grpc_header "${PROTOBUF_GEN_OUTPUT_DIR}/${PROTOBUF_GEN_NAMESPACE}/${proto_name}.grpc.pb.h")
    list(TRANSFORM catkin_INCLUDE_DIRS PREPEND "-I" OUTPUT_VARIABLE catkin_proto_includes)

    # Generate the source and header files using the protoc compiler.
    add_custom_command(
      OUTPUT "${generated_proto_source}" "${generated_proto_header}" "${generated_grpc_source}" "${generated_grpc_header}"
      COMMAND $<TARGET_FILE:protobuf::protoc>
      ARGS
        --grpc_out="generate_mock_code=true:${PROTOBUF_GEN_OUTPUT_DIR}"
        --cpp_out "${PROTOBUF_GEN_OUTPUT_DIR}"
        -I${proto_file_dir} ${catkin_proto_includes}
        --plugin=protoc-gen-grpc="${PROTOBUF_GEN_PLUGIN_EXE}"
        "${proto_file_path}"
      DEPENDS "${proto_file_path}"
    )

    # Append to list of sources.
    list(APPEND GRPC_SOURCES ${generated_proto_source} ${generated_grpc_source})
  endforeach ()

  # Add a library with the generated files.
  if(PROTOBUF_GEN_LIBRARY_NAME)
    add_library(${PROTOBUF_GEN_LIBRARY_NAME} ${GRPC_SOURCES})
    target_include_directories(${PROTOBUF_GEN_LIBRARY_NAME} SYSTEM PUBLIC
                               ${PROTOBUF_GEN_OUTPUT_DIR})
  endif()

endmacro()
