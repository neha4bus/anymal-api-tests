#include <sstream>

#include "inspection_example/InspectItemGoal.hpp"

namespace inspection_example {

std::string inspectItemGoalToString(const InspectItemGoal& goal, const std::string& prefix) {
  std::stringstream stream;
  stream << prefix << "Goal: " << std::endl;
  stream << itemToString(goal.item_, prefix + "  ");
  return stream.str();
}

std::ostream& operator<<(std::ostream& stream, const InspectItemGoal& inspectItemGoal) {
  stream << inspectItemGoalToString(inspectItemGoal);
  return stream;
}

}  // namespace inspection_example
