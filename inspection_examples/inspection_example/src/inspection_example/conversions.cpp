#include <environment_item_ros/conversions.hpp>

#include "inspection_example/conversions.hpp"

namespace inspection_example {

void ConversionTraits<inspection_example::Item, inspection_example_msgs::Item>::convert(const StructType& structType, RosType& rosType) {
  rosType.name = structType.name_;
  rosType.label = structType.label_;
  rosType.count_to = structType.countTo_;
  rosType.frame_id = structType.frameId_;
  rosType.pose.position.x = structType.pose_.pose_.getPosition().x();
  rosType.pose.position.y = structType.pose_.pose_.getPosition().y();
  rosType.pose.position.z = structType.pose_.pose_.getPosition().z();
  rosType.pose.orientation.w = structType.pose_.pose_.getRotation().x();
  rosType.pose.orientation.y = structType.pose_.pose_.getRotation().y();
  rosType.pose.orientation.z = structType.pose_.pose_.getRotation().z();
  rosType.pose.orientation.x = structType.pose_.pose_.getRotation().x();
}

void ConversionTraits<inspection_example::Item, inspection_example_msgs::Item>::convert(const RosType& rosType, StructType& structType) {
  structType.name_ = rosType.name;
  structType.label_ = rosType.label;
  structType.countTo_ = rosType.count_to;
  structType.frameId_ = rosType.frame_id;
  structType.pose_.pose_.getPosition().x() = rosType.pose.position.x;
  structType.pose_.pose_.getPosition().y() = rosType.pose.position.y;
  structType.pose_.pose_.getPosition().z() = rosType.pose.position.z;
  structType.pose_.pose_.getRotation().x() = rosType.pose.orientation.w;
  structType.pose_.pose_.getRotation().y() = rosType.pose.orientation.y;
  structType.pose_.pose_.getRotation().z() = rosType.pose.orientation.z;
  structType.pose_.pose_.getRotation().x() = rosType.pose.orientation.x;
}

void ConversionTraits<inspection_example::InspectItemGoal, inspection_example_msgs::InspectItemGoal>::convert(const StructType& structType,
                                                                                                              RosType& rosType) {
  toRos(structType.item_, rosType.item);
}

void ConversionTraits<inspection_example::InspectItemGoal, inspection_example_msgs::InspectItemGoal>::convert(const RosType& rosType,
                                                                                                              StructType& structType) {
  fromRos(rosType.item, structType.item_);
}

void ConversionTraits<inspection_example::InspectItemFeedback, inspection_example_msgs::InspectItemFeedback>::convert(
    const StructType& structType, RosType& rosType) {
  rosType.message = structType.message_;
  environment_item_ros::toRos(structType.progress_, rosType.progress);
}

void ConversionTraits<inspection_example::InspectItemFeedback, inspection_example_msgs::InspectItemFeedback>::convert(
    const RosType& rosType, StructType& structType) {
  structType.message_ = rosType.message;
  environment_item_ros::fromRos(rosType.progress, structType.progress_);
}

void ConversionTraits<inspection_example::InspectItemResult, inspection_example_msgs::InspectItemResult>::convert(
    const StructType& structType, RosType& rosType) {
  rosType.message = structType.message_;
}

void ConversionTraits<inspection_example::InspectItemResult, inspection_example_msgs::InspectItemResult>::convert(const RosType& rosType,
                                                                                                                  StructType& structType) {
  structType.message_ = rosType.message;
}

}  // namespace inspection_example
