#pragma once

#include <functional>
#include <string>

namespace inspection_example {

/**
 * Container for the inspect item action result. It has the same members as the corresponding Ros message (InspectItem.action).
 */
class InspectItemResult {
 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  InspectItemResult() = default;

  explicit InspectItemResult(const std::string& message) : message_(std::move(message)) {}

  ~InspectItemResult() = default;

  /* ======================================================================== */
  /* Variables                                                                */
  /* ======================================================================== */

  std::string message_;
};

std::string inspectItemResultToString(const InspectItemResult& result, const std::string& prefix = "");

std::ostream& operator<<(std::ostream& stream, const InspectItemResult& inspectItemResult);

using ResultFunction = std::function<void(const InspectItemResult&)>;

}  // namespace inspection_example
