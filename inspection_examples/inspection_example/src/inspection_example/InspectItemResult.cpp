#include <sstream>

#include "inspection_example/InspectItemResult.hpp"

namespace inspection_example {

std::string inspectItemResultToString(const InspectItemResult& result, const std::string& prefix) {
  std::stringstream stream;
  stream << prefix << "Result: " << std::endl;
  stream << prefix << "  Message: " << result.message_ << std::endl;
  return stream.str();
}

std::ostream& operator<<(std::ostream& stream, const InspectItemResult& inspectItemResult) {
  stream << inspectItemResultToString(inspectItemResult);
  return stream;
}

}  // namespace inspection_example
