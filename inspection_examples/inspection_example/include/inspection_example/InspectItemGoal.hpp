#pragma once

#include <string>

#include "inspection_example/Item.hpp"

namespace inspection_example {

/**
 * Container for the inspect item action goal. It has the same members as the corresponding Ros message (InspectItem.action).
 */
class InspectItemGoal {
 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  InspectItemGoal() = default;

  explicit InspectItemGoal(const Item& item) : item_(item) {}

  ~InspectItemGoal() = default;

  /* ======================================================================== */
  /* Variables                                                                */
  /* ======================================================================== */

  Item item_;
};

std::string inspectItemGoalToString(const InspectItemGoal& goal, const std::string& prefix = "");

std::ostream& operator<<(std::ostream& stream, const InspectItemGoal& inspectItemGoal);

}  // namespace inspection_example
