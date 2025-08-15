#include <gtest/gtest.h>

#include "anymal_api_proto/anymal_api_proto.hpp"

namespace anymal_api_cpp {

TEST(TestGeneratedCode, useGeneratedCode) {  // NOLINT
  anymal_api_proto::NavigationGoal goal;
  EXPECT_EQ(goal.label(), "");
  goal.set_label("label");
  EXPECT_EQ(goal.label(), "label");
}

}  // namespace anymal_api_cpp
