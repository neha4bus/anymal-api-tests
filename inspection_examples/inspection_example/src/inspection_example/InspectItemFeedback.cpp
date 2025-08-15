#include <sstream>

#include "inspection_example/InspectItemFeedback.hpp"

namespace inspection_example {

std::string inspectItemFeedbackToString(const InspectItemFeedback& feedback, const std::string& prefix) {
  std::stringstream stream;
  stream << prefix << "Feedback: " << std::endl;
  stream << prefix << "  Message: " << feedback.message_ << std::endl;
  stream << progressToString(feedback.progress_, prefix + "  ");
  return stream.str();
}

std::ostream& operator<<(std::ostream& stream, const InspectItemFeedback& inspectItemFeedback) {
  stream << inspectItemFeedbackToString(inspectItemFeedback);
  return stream;
}

}  // namespace inspection_example
