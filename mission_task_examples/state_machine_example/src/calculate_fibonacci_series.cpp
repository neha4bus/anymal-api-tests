#include <cstdlib>

#include <ros/init.h>
#include <ros/spinner.h>

#include <message_logger/message_logger.hpp>
#include <state_machine/Context.hpp>
#include <state_machine/Factory.hpp>

#include "state_machine_example/CalculateFibonacciSeries.hpp"

using state_machine::Context;
using state_machine::Factory;
using state_machine::StateName;
using state_machine_example::CalculateFibonacciSeries;

/**
 * This executable showcases the `CalculateFibonacciSeries` state in action.
 * Note that this is only an example. On the robot one could create a mission containing a `CalculateFibonacciSeries` state and run it.
 */
int main(int argc, char** argv) {
  ros::init(argc, argv, "state_machine_example_node");
  auto context{std::make_shared<Context>()};
  Factory factory{context};
  auto state{factory.createState<CalculateFibonacciSeries>(StateName{"CalculateFibonacciSeries"})};
  if (state == nullptr) {
    return EXIT_FAILURE;
  }
  state->setOrder(5);
  const auto inconsistencies{state->getInconsistencies()};
  if (!inconsistencies.empty()) {
    MELO_ERROR("The state is inconsistent:")
    MELO_ERROR_STREAM(inconsistencies)
    return EXIT_FAILURE;
  }
  MELO_INFO("Executing the state ...")
  ros::AsyncSpinner spinner{1};
  spinner.start();
  const auto outcome{state->execute()};
  spinner.stop();
  MELO_INFO_STREAM("The state has been executed with outcome '" << outcome << "'.")
  return EXIT_SUCCESS;
}
