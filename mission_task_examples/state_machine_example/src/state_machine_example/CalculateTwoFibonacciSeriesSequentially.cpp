#include "state_machine_example/CalculateTwoFibonacciSeriesSequentially.hpp"

#include <state_machine/Factory.hpp>

#include "state_machine_example/CalculateFibonacciSeries.hpp"

namespace state_machine_example {

void CalculateTwoFibonacciSeriesSequentially::setOrder(const int order) {
  // Reconfigure the child states, in this case we simply have to forward the order.
  dynamic_cast<CalculateFibonacciSeries*>(getState(name1_))->setOrder(order);
  dynamic_cast<CalculateFibonacciSeries*>(getState(name2_))->setOrder(order);
}

std::optional<int> CalculateTwoFibonacciSeriesSequentially::getOrder() const {
  // Get the oder from the child states. We can assume that they match, so we just get the one from the first child state.
  return dynamic_cast<CalculateFibonacciSeries*>(getState(name1_))->getOrder();
}

bool CalculateTwoFibonacciSeriesSequentially::constructImpl() {
  // This function is called immediately after construction of this state. Use it to configure this state, create child states, etc.
  using state_machine::outcomes::failure;
  using state_machine::outcomes::preemption;
  using state_machine::outcomes::success;
  // Set the possible outcomes of this state. This is required in order to check state machines for consistency. Note that as every state
  // must have the outcomes "preemption" and "failure", it is not necessary to specify them explicitly.
  setOutcomes(state_machine::Outcomes({success()}));
  // Configure whether this state machine should restart every time it is executed or continue from where it left off.
  setRestartOnExecution(true);
  // Create the child states.
  state_machine::Factory factory(getContext());
  auto state1 = factory.createState<CalculateFibonacciSeries>(name1_);
  if (state1 == nullptr) {
    return false;
  }
  auto state2 = factory.createState<CalculateFibonacciSeries>(name2_);
  if (state2 == nullptr) {
    return false;
  }
  // Add the child states, specifying the transitions.
  addState(std::move(state1),
           // If state 1 succeeds, proceed with state 2.
           {{success(), name2_},
            // If state 1 is preempted, preempt this sequence of states. This is the recommended behavior.
            {preemption(), preemption()},
            // If state 1 failed, do not continue with state 2. One could also specify to move on by putting `name2_` here.
            {failure(), failure()}});
  addState(std::move(state2),
           // If state 2 succeeds, this sequence of states succeeds.
           {{success(), success()},
            // If state 2 is preempted, preempt this sequence of states. This is the recommended behavior.
            {preemption(), preemption()},
            // If state 2 failed, this sequence of states failed.
            {failure(), failure()}});
  // Configure the initial state.
  setDefaultInitialState(name1_);
  return true;
}

void CalculateTwoFibonacciSeriesSequentially::saveSettingsImpl(state_machine::Settings& settings) const {
  // If the order has been set, store it in the settings.
  const auto order{getOrder()};
  if (order.has_value()) {
    settings.addParameter(state_machine::Parameter{"order", "int", order.value()});
  }
}

bool CalculateTwoFibonacciSeriesSequentially::loadSettingsImpl(const state_machine::Settings& settings) {
  // If the order is present in the settings, read and set it.
  if (settings.parameterIsRegistered("order")) {
    setOrder(settings.getParameter("order").getValue().as<int>());
  }
  return true;
}

}  // namespace state_machine_example
