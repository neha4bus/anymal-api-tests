#pragma once

#include <memory>

#include <ros/ros.h>

#include <inspection_example_msgs/InspectItemAction.h>
#include <any_inspection_ros/InspectionPluginBase.hpp>
#include <inspection_example/Item.hpp>

namespace inspection_example_plugin {

//! Alias for the templated base class.
using InspectionPluginBase_ =
    any_inspection_ros::InspectionPluginBase<inspection_example_msgs::InspectItemAction, inspection_example_msgs::InspectItemGoal,
                                             inspection_example_msgs::InspectItemFeedback, inspection_example_msgs::InspectItemResult>;

/**
 * An inspection plugin.
 */
class InspectionExamplePlugin : public InspectionPluginBase_ {
 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  explicit InspectionExamplePlugin();

  ~InspectionExamplePlugin() override = default;

 private:
  /* ======================================================================== */
  /* Variables                                                                */
  /* ======================================================================== */

  //! The Ros independent item container.
  inspection_example::Item item_;

  //! Ros timer.
  std::unique_ptr<ros::Timer> timer_;
  //! Current counter.
  unsigned int counter_{0};

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
   * This basically starts the inspection for the received goal.
   * Optional, will be called when a new goal arrives.
   * @return True if successful.
   */
  bool startImpl() override;

  /**
   * This basically stops the inspection for the active goal.
   * Optional, will be called when a goal is preempted, a new goal arrives and the old one is still active, or
   * the plugin shuts down and a goal is still active.
   * @return True if successful.
   */
  bool stopImpl() override;

  /**
   * Returns the current result. This is e.g. called when a goal preempts.
   * @return Result.
   */
  inspection_example_msgs::InspectItemResult getResultImpl() override;

  /* ======================================================================== */
  /* Callbacks                                                                */
  /* ======================================================================== */

  /**
   * A timer to do some example work.
   * @param event Timer event.
   */
  void onTimerCallback(const ros::TimerEvent& event);
};

}  // namespace inspection_example_plugin
