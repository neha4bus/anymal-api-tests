#include <gtest/gtest.h>
#include <ros/ros.h>

int main(int argc, char** argv) {
  ros::init(argc, argv, "test_state_machine_example");
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
