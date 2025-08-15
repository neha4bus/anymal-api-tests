#pragma once

#include <optional>

#include <actionlib_tutorials/FibonacciAction.h>
#include <ros/node_handle.h>

#include <state_machine/State.hpp>
#include <state_machine_ros/ActionClient.hpp>
#include <state_machine_ros/RosInterface.hpp>

namespace state_machine_example {

/**
 * This class implements a simple state. In this example its purpose is to calculate the fibonacci series up to a given order.
 * The order is a parameter which can be set using `setOrder()`, and it is also stored in the state's settings making it editable with the
 * state machine editor.
 * Upon execution, the state sends an action goal to a ROS action server running in another ROS node and waits for its completion.
 * Depending on the action result, the state returns "success", "preemption", or "failure".
 */
class CalculateFibonacciSeries : public state_machine::State, public state_machine_ros::RosInterface {
 public:
  /**
   * Empty constructor.
   * Every state is constructed using a `state_machine::Factory`, which requires the states to provide an empty constructor.
   * It is recommended to just set it to `default` and perform any required steps at construction time by overriding `constructImpl()`.
   */
  CalculateFibonacciSeries() = default;

  /**
   * Set the order to the fibonacci series to calculate.
   * @param order Order.
   */
  void setOrder(int order);

  /**
   * Get the order to the fibonacci series to calculate.
   * @return Order, std::nullopt if it has not been set yet.
   */
  std::optional<int> getOrder() const;

 private:
  // Typedefs to shorten the code.
  using Goal = actionlib_tutorials::FibonacciGoal;
  using Action = actionlib_tutorials::FibonacciAction;
  using ActionClient = state_machine_ros::ActionClient<Action>;
  using ActionClientPtr = state_machine_ros::ActionClientPtr<Action>;

  //! Method which is called immediately after the state's construction.
  bool constructImpl() override;
  //! Method which is called to save all parameters of a state into the settings. Override this if your state has a parameter (in this case
  //! the order) and you want to execute your state as a plugin.
  void saveSettingsImpl(state_machine::Settings& settings) const override;
  //! Method which is called to load all parameters of a state from the settings. Override this if your state has a parameter (in this case
  //! the order) and you want to execute your state as a plugin.
  bool loadSettingsImpl(const state_machine::Settings& settings) override;
  //! Method which is called to determine potential inconsistencies in this state.
  state_machine::Inconsistencies getInconsistenciesImpl() const override;
  //! Method called before the actual execution happens.
  void runPreExecution() override;
  //! Method representing the actual execution of the state. It is the only method which is mandatory to override.
  state_machine::Outcome runMidExecution() override;
  //! Method called after the actual execution happens.
  void runPostExecution() override;
  //! Method which is called when a preemption has been requested.
  void onPreemptionRequest() override;
  //! Method which is called to determine the progress of this state.
  state_machine::Progress getProgressImpl() const override;

  //! ROS action client to perform the fibonacci calculation.
  ActionClientPtr actionClient_;
  //! ROS action "topic".
  std::string action_{"/fibonacci"};
  //! The order of the fibonacci series to calculate. We use `std::optional` instead of a magic number to know whether it has been
  //! initialized or not.
  std::optional<int> order_;
  //! Mutex protecting the feedback from simultaneous access by different threads.
  mutable std::shared_mutex actionFeedbackMutex_;
  //! Feedback of the action. Used to provide the state's progress.
  ActionClient::FeedbackConstPtr actionFeedback_;
};

}  // namespace state_machine_example

STATE_MACHINE_SPECIALIZE_TYPE_TO_STRING(state_machine_example::CalculateFibonacciSeries)
