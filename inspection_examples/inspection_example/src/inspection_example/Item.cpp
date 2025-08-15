#include <sstream>

#include <environment_item/helpers.hpp>
#include <message_logger/message_logger.hpp>

#include "inspection_example/Item.hpp"

namespace inspection_example {

constexpr const char* Item::type_;
constexpr const char* Item::category_;
constexpr const char* Item::childCategory_;

Item::operator bool() const {
  if (countTo_ == 0) {
    MELO_ERROR_STREAM("'Count to' must be greater than zero.")
    return false;
  }
  return true;
}

std::string Item::getCategory() {
  return category_;
}

std::string Item::getType() const {
  return type_;
}

std::string Item::getChildCategory() {
  return childCategory_;
}

bool Item::setYamlNode(const yaml_tools::YamlNode& node) {
  try {
    name_ = node["name"].as<std::string>();
    name_ = cleanUpString(name_);
    label_ = node["label"].as<std::string>();
    label_ = cleanUpString(label_);
    countTo_ = node["count_to"].as<int>();
    environment_item::poseFromYaml(node["pose"], frameId_, pose_);
  } catch (yaml_tools::Exception& exception) {
    MELO_ERROR_STREAM("Could not parse item from yaml node. Exception: " << exception.what())
    return false;
  }
  return true;
}

yaml_tools::YamlNode Item::getYamlNode() {
  yaml_tools::YamlNode node;
  node["name"] = name_;
  node["label"] = label_;
  node["count_to"] = countTo_;
  node["pose"]["header"]["frame_id"] = frameId_;
  node["pose"]["pose"]["position"]["x"] = pose_.pose_.getPosition().x();
  node["pose"]["pose"]["position"]["y"] = pose_.pose_.getPosition().y();
  node["pose"]["pose"]["position"]["z"] = pose_.pose_.getPosition().z();
  node["pose"]["pose"]["orientation"]["w"] = pose_.pose_.getRotation().w();
  node["pose"]["pose"]["orientation"]["x"] = pose_.pose_.getRotation().x();
  node["pose"]["pose"]["orientation"]["y"] = pose_.pose_.getRotation().y();
  node["pose"]["pose"]["orientation"]["z"] = pose_.pose_.getRotation().z();
  return node;
}

std::string itemToString(const Item& item, const std::string& prefix) {
  std::stringstream stream;
  stream << prefix << "Example item:" << std::endl;
  stream << prefix << "  Name: " << item.name_ << std::endl;
  stream << prefix << "  Label: " << item.label_ << std::endl;
  stream << prefix << "  Count to: " << item.countTo_ << std::endl;
  stream << prefix << "  Frame id: " << item.frameId_ << std::endl;
  stream << prefix << "  Pose:" << std::endl;
  stream << prefix << "    Position:" << std::endl;
  stream << prefix << "      x: " << item.pose_.pose_.getPosition().x() << std::endl;
  stream << prefix << "      y: " << item.pose_.pose_.getPosition().y() << std::endl;
  stream << prefix << "      z: " << item.pose_.pose_.getPosition().z() << std::endl;
  stream << prefix << "    Orientation:" << std::endl;
  stream << prefix << "      w: " << item.pose_.pose_.getRotation().w() << std::endl;
  stream << prefix << "      x: " << item.pose_.pose_.getRotation().x() << std::endl;
  stream << prefix << "      y: " << item.pose_.pose_.getRotation().y() << std::endl;
  stream << prefix << "      z: " << item.pose_.pose_.getRotation().z() << std::endl;
  return stream.str();
}

std::ostream& operator<<(std::ostream& stream, const Item& item) {
  stream << itemToString(item);
  return stream;
}

}  // namespace inspection_example
