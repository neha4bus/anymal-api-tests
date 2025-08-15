#pragma once

#include <environment_utils/conversions.hpp>

#include <inspection_example_msgs/InspectItemFeedback.h>
#include <inspection_example_msgs/InspectItemGoal.h>
#include <inspection_example_msgs/InspectItemResult.h>
#include <inspection_example_msgs/Item.h>

#include <inspection_example/InspectItemFeedback.hpp>
#include <inspection_example/InspectItemGoal.hpp>
#include <inspection_example/InspectItemResult.hpp>
#include <inspection_example/Item.hpp>

#define INSPECTION_EXAMPLE_DEFINE_CONVERSION_FUNCTIONS_WITH_RETURN \
  inline static RosType convert(const StructType& structType) {    \
    RosType rosType;                                               \
    convert(structType, rosType);                                  \
    return rosType;                                                \
  }                                                                \
  inline static StructType convert(const RosType& rosType) {       \
    StructType structType;                                         \
    convert(rosType, structType);                                  \
    return structType;                                             \
  }

namespace inspection_example {

// Forward declaration
template <typename StructType, typename RosType>
class ConversionTraits;

// Generic templates
template <typename StructType, typename RosType>
inline void toRos(const StructType& in, RosType& out) {
  ConversionTraits<StructType, RosType>::convert(in, out);
}

template <typename StructType, typename RosType>
inline RosType toRos(const StructType& in) {
  return ConversionTraits<StructType, RosType>::convert(in);
}

template <typename StructType, typename RosType>
inline void fromRos(const RosType& in, StructType& out) {
  ConversionTraits<StructType, RosType>::convert(in, out);
}

template <typename StructType, typename RosType>
inline StructType fromRos(const RosType& in) {
  return ConversionTraits<StructType, RosType>::convert(in);
}

// Item
template <>
class ConversionTraits<inspection_example::Item, inspection_example_msgs::Item> {
 public:
  using StructType = inspection_example::Item;
  using RosType = inspection_example_msgs::Item;

  static void convert(const StructType& structType, RosType& rosType);

  static void convert(const RosType& rosType, StructType& structType);

  INSPECTION_EXAMPLE_DEFINE_CONVERSION_FUNCTIONS_WITH_RETURN
};

// InspectItemGoal
template <>
class ConversionTraits<inspection_example::InspectItemGoal, inspection_example_msgs::InspectItemGoal> {
 public:
  using StructType = inspection_example::InspectItemGoal;
  using RosType = inspection_example_msgs::InspectItemGoal;

  static void convert(const StructType& structType, RosType& rosType);

  static void convert(const RosType& rosType, StructType& structType);

  INSPECTION_EXAMPLE_DEFINE_CONVERSION_FUNCTIONS_WITH_RETURN
};

// InspectItemFeedback
template <>
class ConversionTraits<inspection_example::InspectItemFeedback, inspection_example_msgs::InspectItemFeedback> {
 public:
  using StructType = inspection_example::InspectItemFeedback;
  using RosType = inspection_example_msgs::InspectItemFeedback;

  static void convert(const StructType& structType, RosType& rosType);

  static void convert(const RosType& rosType, StructType& structType);

  INSPECTION_EXAMPLE_DEFINE_CONVERSION_FUNCTIONS_WITH_RETURN
};

// InspectItemResult
template <>
class ConversionTraits<inspection_example::InspectItemResult, inspection_example_msgs::InspectItemResult> {
 public:
  using StructType = inspection_example::InspectItemResult;
  using RosType = inspection_example_msgs::InspectItemResult;

  static void convert(const StructType& structType, RosType& rosType);

  static void convert(const RosType& rosType, StructType& structType);

  INSPECTION_EXAMPLE_DEFINE_CONVERSION_FUNCTIONS_WITH_RETURN
};

}  // namespace inspection_example

namespace environment_utils {

template <>
inline void fromXmlRpc(XmlRpc::XmlRpcValue& params, inspection_example::Item& type) {
  try {
    fromXmlRpc(params[std::string("name")], type.name_);
    fromXmlRpc(params[std::string("label")], type.label_);
    fromXmlRpc(params[std::string("count_to")], type.countTo_);
    fromXmlRpc(params[std::string("pose")][std::string("header")][std::string("frame_id")], type.frameId_);
    fromXmlRpc(params[std::string("pose")], type.pose_);
  } catch (const XmlRpc::XmlRpcException& exception) {
    ROS_ERROR_STREAM_THROTTLE(5.0,
                              "Caught an XmlRpc exception while reading example item '" << type.name_ << "': " << exception.getMessage());
  }
}

template <>
inline void toXmlRpc(const inspection_example::Item& type, XmlRpc::XmlRpcValue& params) {
  try {
    params[std::string("name")] = type.name_;
    params[std::string("label")] = type.label_;
    params[std::string("type")] = type.getType();
    params[std::string("count_to")] = static_cast<int>(type.countTo_);
    params[std::string("pose")][std::string("header")][std::string("frame_id")] = type.frameId_;
    toXmlRpc(type.pose_, params["pose"]);
  } catch (const XmlRpc::XmlRpcException& exception) {
    ROS_ERROR_STREAM_THROTTLE(5.0,
                              "Caught an XmlRpc exception while writing example item '" << type.name_ << "': " << exception.getMessage());
  }
}

}  // namespace environment_utils