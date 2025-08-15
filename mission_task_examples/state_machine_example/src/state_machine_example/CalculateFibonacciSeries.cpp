#include "state_machine_example/CalculateFibonacciSeries.hpp"

#include <param_io/get_param.hpp>

namespace state_machine_example {

void CalculateFibonacciSeries::setOrder(const int order) {
  order_ = order;
}

std::optional<int> CalculateFibonacciSeries::getOrder() const {
  return order_;
}

bool CalculateFibonacciSeries::constructImpl() {
  // This function is called immediately after construction of this state. Use it to configure this state, read parameters, etc.
  // Do _not_ set up any ROS interfaces in here, because the states are also instantiate in the GUI, and you do not want those instances
  // to connect to the ROS system without ever being executed. Start up resp. shut down ROS interfaces in `runPreExecution()` resp.
  // `runPostExecution()`.
  using state_machine::outcomes::success;
  // Set the possible outcomes of this state. This is required in order to check state machines for consistency. Note that as every state
  // must have the outcomes "preemption" and "failure", it is not necessary to specify them explicitly.
  setOutcomes(state_machine::Outcomes({success()}));
  // Set the nominal (expected) outcome of this state. This is required to be able to "simulate" the state and show a preview in the mission
  // monitor.
  setNominalOutcome(success());
  // Read any ROS parameters you might have.
  param_io::getParam(getNodeHandle(), "/state_machine_example/calculate_fibonacci_series/action", action_);
  // In case there was a severe error, returning "false" will prevent the construction of this state.
  return true;
}

void CalculateFibonacciSeries::saveSettingsImpl(state_machine::Settings& settings) const {
  // Always store the order as parameter in the settings in order to make the field appear in the mission editor.
  // Use 0 as default if the order has not been set.
  settings.addParameter(state_machine::Parameter{"order", "int", order_.value_or(0)});
}

bool CalculateFibonacciSeries::loadSettingsImpl(const state_machine::Settings& settings) {
  // If the order is present in the settings, read and set it.
  if (settings.parameterIsRegistered("order")) {
    order_ = settings.getParameter("order").getValue().as<int>();
  }
  return true;
}

state_machine::Inconsistencies CalculateFibonacciSeries::getInconsistenciesImpl() const {
  // In this example we require that the order is either set by `setOrder()` or that it has been loaded through the settings.
  // If this did not happen, it makes the state inconsistent which is reported in the mission editor and prevents the execution of the
  // state.
  state_machine::Inconsistencies inconsistencies;
  if (!order_.has_value()) {
    inconsistencies.add(state_machine::Inconsistency("The order of '" + getNestedName().toString() + "' has not been set."));
  }
  return inconsistencies;
}

void CalculateFibonacciSeries::runPreExecution() {
  // When this state is executed, this is the first method to be called.
  // Use it to prepare the execution: Reset old data, start up ROS interfaces, etc.
  {
    // Clear potential feedback from the previous execution. Protect it with a mutex, because `getProgressImpl()` might be called at the
    // same time from a different thread.
    std::shared_lock lock(actionFeedbackMutex_);
    actionFeedback_.reset();
  }
  // Set up the ROS action client and configure its feedback callback.
  actionClient_ = std::make_shared<ActionClient>(getContext()->getTimeInterface(), getNodeHandle(), action_);
  actionClient_->setFeedbackCb([this](const ActionClient::FeedbackConstPtr& feedback) {
    std::unique_lock lock(actionFeedbackMutex_);
    actionFeedback_ = feedback;
  });
}

state_machine::Outcome CalculateFibonacciSeries::runMidExecution() {
  // This is the main function of the state's execution, determining the outcome of a state.
  using state_machine::outcomes::failure;
  using state_machine::outcomes::preemption;
  using state_machine::outcomes::success;

  // If the order has not been set, add an "error" report entry (it will also be printed to the console).
  // Return with outcome "failure".
  if (!order_.has_value()) {
    getContext()->getReportInterface()->addSimpleEntry(*this, report::Level::ERROR,
                                                       "Failed to calculate Fibonacci series: The order has not been set.");
    return failure();
  }

  // Add an entry to the report, mentioning that this state has been started.
  getContext()->getReportInterface()->addSimpleEntry(*this, report::Level::DEBUG,
                                                     "Calculating Fibonacci series of order '" + std::to_string(order_.value()) + "' ...");

  // Create a ROS action goal.
  Goal goal;
  goal.order = order_.value();

  // Execute the goal. Note that `execute()` also takes several timeout arguments if you want to deviate from the defaults.
  const auto actionGoalOutcome = actionClient_->execute(goal);

  // Analyze the outcome of the goal.
  if (state_machine_ros::actionGoalSucceeded(actionGoalOutcome)) {
    // The goal succeeded. Use the ROS action result to create a report entry.
    const ActionClient::ResultConstPtr result{actionClient_->getResult()};
    report::Entry entry{getContext()->getReportInterface()->createEntry(
        *this, report::Level::INFO, "Successfully calculated Fibonacci series of order '" + std::to_string(order_.value()) + "'.")};
    // Note that an entry has many properties which you can set, e.g. a value and a unit.
    entry.value_ = result->sequence.empty() ? 0 : result->sequence.back();
    getContext()->getReportInterface()->addEntry(entry);
    return success();
  } else if (state_machine_ros::actionGoalCancelled(actionGoalOutcome)) {
    // The goal has been preempted, either because `onPreemptionRequest()` has been called, or by another goal which has been sent.
    getContext()->getReportInterface()->addSimpleEntry(*this, report::Level::DEBUG,
                                                       "Calculating Fibonacci series of order '" + std::to_string(order_.value()) +
                                                           "' was cancelled: " + state_machine_ros::toString(actionGoalOutcome));
    return preemption();
  } else {
    // The goal and therefore the state has failed.
    getContext()->getReportInterface()->addSimpleEntry(*this, report::Level::ERROR,
                                                       "Failed to calculate Fibonacci series of order '" + std::to_string(order_.value()) +
                                                           "': " + state_machine_ros::toString(actionGoalOutcome));
    return failure();
  }
}

void CalculateFibonacciSeries::runPostExecution() {
  // When this state is executed, this is the last method to be called.
  // Use it to clean up the execution: Shut down ROS interfaces, etc.
  actionClient_.reset();
}

void CalculateFibonacciSeries::onPreemptionRequest() {
  // This method is called when the state is preempted, e.g. when an external entity commands to stop the execution of a state machine.
  // ROS actions are useful in this case because they can be cancelled.
  // The method does not need to be blocking.
  if (actionClient_) {
    actionClient_->cancelExecution();
  }
}

state_machine::Progress CalculateFibonacciSeries::getProgressImpl() const {
  // This method is called periodically to get the progress of the state's execution.
  // If you are calling a ROS action it might be a good idea to forwards the progress in its feedback message.
  state_machine::Progress progress;
  std::shared_lock lock(actionFeedbackMutex_);
  if (order_.has_value() && actionFeedback_ != nullptr) {
    // The progress is <current order> / <total order> without any specific unit.
    progress.setUnit(std::string{});
    progress.setGoal(static_cast<double>(order_.value()));
    progress.setDone(static_cast<double>(actionFeedback_->sequence.size()));
  }
  return progress;
}

}  // namespace state_machine_example
