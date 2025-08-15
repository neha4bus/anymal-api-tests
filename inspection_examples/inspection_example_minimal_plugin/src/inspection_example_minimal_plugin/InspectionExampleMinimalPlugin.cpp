#include <pluginlib/class_list_macros.h>

#include <message_logger/message_logger.hpp>

#include "inspection_example_minimal_plugin/InspectionExampleMinimalPlugin.hpp"

// Register this inspection as a InspectionPluginInterface plugin.
PLUGINLIB_EXPORT_CLASS(inspection_example_minimal_plugin::InspectionExampleMinimalPlugin, any_inspection_ros::InspectionPluginInterfaceRos)

namespace inspection_example_minimal_plugin {

/* ========================================================================== */
/* Constructor/Destructor                                                     */
/* ========================================================================== */

InspectionExampleMinimalPlugin::InspectionExampleMinimalPlugin() : any_inspection_ros::InspectionPluginInterfaceRos() {}

/* ========================================================================== */
/* Methods                                                                    */
/* ========================================================================== */

bool InspectionExampleMinimalPlugin::constructImpl() {
  MELO_DEBUG_STREAM("Construct plugin.")
  // Do some stuff to prepare the plugin.
  return true;
}

bool InspectionExampleMinimalPlugin::shutdownImpl() {
  MELO_DEBUG_STREAM("Shutdown plugin.")
  // Do some stuff to shutdown the plugin.
  return true;
}

bool InspectionExampleMinimalPlugin::startImpl() {
  MELO_DEBUG_STREAM("Start inspection plugin.")
  // Do some stuff to start the inspection plugin.
  return true;
}

bool InspectionExampleMinimalPlugin::stopImpl() {
  MELO_DEBUG_STREAM("Stop inspection plugin.")
  // Do some stuff to stop the inspection inspection plugin.
  return true;
}

bool InspectionExampleMinimalPlugin::startActionServerImpl(const std::string& /*action*/) {
  MELO_DEBUG_STREAM("Start action server.")
  // Optional: If needed start an action server.
  return true;
}

bool InspectionExampleMinimalPlugin::shutdownActionServerImpl() {
  MELO_DEBUG_STREAM("Start action server.")
  // Optional: If needed stop an action server.
  return true;
}

}  // namespace inspection_example_minimal_plugin
