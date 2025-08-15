#pragma once

#include <functional>
#include <string>

#include <environment_item/Progress.hpp>

namespace inspection_example {

/**
 * Container for the inspect item action feedback. It has the same members as the corresponding Ros message (InspectItem.action).
 */
class InspectItemFeedback {
 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  InspectItemFeedback() = default;

  InspectItemFeedback(const std::string& message, const environment_item::Progress& progress)
      : message_(std::move(message)), progress_(progress) {}

  ~InspectItemFeedback() = default;

  /* ======================================================================== */
  /* Variables                                                                */
  /* ======================================================================== */

  std::string message_;

  environment_item::Progress progress_;
};

std::string inspectItemFeedbackToString(const InspectItemFeedback& feedback, const std::string& prefix = "");

std::ostream& operator<<(std::ostream& stream, const InspectItemFeedback& inspectItemFeedback);

}  // namespace inspection_example
