#pragma once

#include <optional>

#include <state_machine/StateMachine.hpp>
#include <state_machine/StateName.hpp>
#include <state_machine_ros/RosInterface.hpp>

namespace state_machine_example {

/**
 * This class implements a state machine which runs two states in sequence. In this example its purpose is to run two
 * `CalculateFibonacciSeries` states after each other. The order is a parameter which can be set using `setOrder()`, and it is also stored
 * in the state's settings making it editable with the state machine editor. Depending on the result of the child states, this state returns
 * "success", "preemption", or "failure".
 */
class CalculateTwoFibonacciSeriesSequentially : public state_machine::StateMachine, public state_machine_ros::RosInterface {
 public:
  /**
   * Empty constructor.
   * Every state is constructed using a `state_machine::Factory`, which requires the states to provide an empty constructor.
   * It is recommended to just set it to `default` and perform any required steps at construction time by overriding `constructImpl()`.
   */
  CalculateTwoFibonacciSeriesSequentially() = default;

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
  //! Method which is called immediately after the state's construction.
  bool constructImpl() override;
  //! Method which is called to save all parameters of a state into the settings. Override this if your state has a parameter (in this case
  //! the order) and you want to execute your state as a plugin.
  void saveSettingsImpl(state_machine::Settings& settings) const override;
  //! Method which is called to load all parameters of a state from the settings. Override this if your state has a parameter (in this case
  //! the order) and you want to execute your state as a plugin.
  bool loadSettingsImpl(const state_machine::Settings& settings) override;

  const state_machine::StateName name1_{"CalculateFibonacciSeries1"};
  const state_machine::StateName name2_{"CalculateFibonacciSeries2"};
};

}  // namespace state_machine_example

STATE_MACHINE_SPECIALIZE_TYPE_TO_STRING(state_machine_example::CalculateTwoFibonacciSeriesSequentially)
