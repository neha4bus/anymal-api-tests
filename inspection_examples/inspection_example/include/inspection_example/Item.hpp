#pragma once

#include <iostream>
#include <string>

#include <any_measurements/Pose.hpp>

#include <environment_item/ItemBase.hpp>
#include <environment_item/Range.hpp>
#include <environment_item/Size.hpp>

namespace inspection_example {

/**
 * Container for the inspectable item. It has the same members as the corresponding Ros message (Item.msg).
 */
class Item : public environment_item::ItemBase {
  using Pose = any_measurements::Pose;

 public:
  /* ======================================================================== */
  /* Constructor/Destructor                                                   */
  /* ======================================================================== */

  Item() : environment_item::ItemBase(""){};

  Item(std::string& name, std::string& label, unsigned int countTo, std::string& frameId, const Pose& pose)
      : environment_item::ItemBase(name), label_(std::move(label)), countTo_(std::move(countTo)), frameId_(frameId), pose_(pose) {}

  ~Item() = default;

  /* ======================================================================== */
  /* Accessors                                                                */
  /* ======================================================================== */

  explicit operator bool() const;

  std::string getCategory() override;

  std::string getType() const override;

  std::string getChildCategory() override;

  bool setYamlNode(const yaml_tools::YamlNode& node) override;

  yaml_tools::YamlNode getYamlNode() override;

  /* ======================================================================== */
  /* Variables                                                                */
  /* ======================================================================== */

  std::string label_;

  unsigned int countTo_{0};

  std::string frameId_;

  Pose pose_;

  /* ======================================================================== */
  /* Constants                                                                */
  /* ======================================================================== */

  //! Define the item category. In this case it's an inspectable item and therefore 'inspection'.
  static constexpr auto category_ = "inspection";
  //! Define the unique item type. This is required to read from the Ros parameter server.
  static constexpr auto type_ = "inspection_example";
  //! Define the child category. In this case it can have children of the type 'navigation_zone', which define from where the item is
  //! visible.
  static constexpr auto childCategory_ = "navigation_zone";
};

std::string itemToString(const Item& item, const std::string& prefix = "");

std::ostream& operator<<(std::ostream& stream, const Item& item);

}  // namespace inspection_example
