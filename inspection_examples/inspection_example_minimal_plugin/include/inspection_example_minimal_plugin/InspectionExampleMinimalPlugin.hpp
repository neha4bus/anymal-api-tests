#pragma once

#include <any_inspection_ros/InspectionPluginInterfaceRos.hpp>

namespace inspection_example_minimal_plugin {

/**
 * A minimal inspection plugin.
 */
class InspectionExampleMinimalPlugin : public any_inspection_ros::InspectionPluginInterfaceRos {
 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  explicit InspectionExampleMinimalPlugin();

  ~InspectionExampleMinimalPlugin() override = default;

 private:
  /* ======================================================================== */
  /* Methods                                                                  */
  /* ======================================================================== */

  /**
   * Optional, will be called when constructing the plugin.
   * @return True if successful.
   */
  bool constructImpl() override;

  /**
   * Optional, will be called when shutting down the plugin.
   * @return True if successful.
   */
  bool shutdownImpl() override;

  /**
   * Optional, will be called from start(), which has to be called somewhere in the code.
   * @return True if successful.
   */
  bool startImpl() override;

  /**
   * Optional, will be called from stop(), which has to be called somewhere in the code.
   * @return True if successful.
   */
  bool stopImpl() override;

  /**
   * Optional, will be called from construct().
   * @return True if successful.
   */
  bool startActionServerImpl(const std::string& action) override;

  /**
   * Optional, will be called from shutdown().
   * @return True if successful.
   */
  bool shutdownActionServerImpl() override;
};

}  // namespace inspection_example_minimal_plugin
