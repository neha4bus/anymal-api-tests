#include <pluginlib/class_list_macros.h>

#include <inspection_example/conversions.hpp>
#include <message_logger/message_logger.hpp>

#include "inspection_example_plugin/InspectionExamplePlugin.hpp"

// Register this inspection as a InspectionPluginInterface plugin.
PLUGINLIB_EXPORT_CLASS(inspection_example_plugin::InspectionExamplePlugin, any_inspection_ros::InspectionPluginInterfaceRos)

namespace inspection_example_plugin {

/* ========================================================================== */
/* Constructor/Destructor                                                     */
/* ========================================================================== */

InspectionExamplePlugin::InspectionExamplePlugin() : InspectionPluginBase_() {}

/* ========================================================================== */
/* Methods                                                                    */
/* ========================================================================== */

bool InspectionExamplePlugin::constructImpl() {
  MELO_DEBUG_STREAM("Construct plugin.")
  // Do some stuff to prepare the plugin.
  return true;
}

bool InspectionExamplePlugin::shutdownImpl() {
  MELO_DEBUG_STREAM("Shutdown plugin.")
  // Do some stuff to shutdown the plugin.
  return true;
}

bool InspectionExamplePlugin::startImpl() {
  MELO_DEBUG_STREAM("Start inspection for goal: " << getGoal().item.name)

  inspection_example::fromRos(getGoal().item, item_);

  if (!item_) {
    MELO_ERROR_STREAM("Cannot start inspection. The given item is invalid.")
    return false;
  }

  // Do some stuff to start the inspection. Subscribe to a sensor topic, start a worker, etc.

  // In this case a Ros timer is started to count towards a given number.
  counter_ = 0;
  timer_.reset(new ros::Timer());
  *timer_ = getNodeHandle().createTimer(ros::Duration(1.0), &InspectionExamplePlugin::onTimerCallback, this);
  timer_->start();

  return true;
}

bool InspectionExamplePlugin::stopImpl() {
  MELO_DEBUG_STREAM("Stop inspection for goal: " << item_.name_)

  // Do some stuff to stop the inspection.

  timer_->stop();

  return true;
}

inspection_example_msgs::InspectItemResult InspectionExamplePlugin::getResultImpl() {
  inspection_example_msgs::InspectItemResult result;
  result.message = "Counter is: " + std::to_string(counter_);
  return result;
}

/* ========================================================================== */
/* Callbacks                                                                  */
/* ========================================================================== */

void InspectionExamplePlugin::onTimerCallback(const ros::TimerEvent& /*event*/) {
  // Increment counter.
  ++counter_;

  MELO_DEBUG_STREAM("Run timer. Counter: " << counter_)

  // Publish feedback.
  inspection_example_msgs::InspectItemFeedback feedbackMsg;
  feedbackMsg.progress.goal = 100.0;
  feedbackMsg.progress.current = 100.0 * (static_cast<double>(item_.countTo_) / static_cast<double>(counter_));
  feedbackMsg.progress.unit = "%";
  feedbackMsg.message = "Counter is: " + std::to_string(counter_);
  publishFeedback(feedbackMsg);

  if (counter_ == item_.countTo_) {
    MELO_DEBUG_STREAM("Counter finished: ")
    // Stop the Ros timer.
    timer_->stop();

    // Set action succeeded.
    setSucceeded(getResultImpl());
  }
}

}  // namespace inspection_example_plugin
