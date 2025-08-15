\page page_inspection_example Inspection Example

# Inspection Example

## Overview

This package contains Ros independent containers and conversion functions. 

It is good practice to have a Ros abstraction layer. 
Therefore, it is necessary to create a container per Ros message and the corresponding conversion functions `fromRos` and `toRos`. 
Additionally, to be compatible with the environment tools it is necessary to have XmlRpc conversion functions for the inspectable item.

## Requirements

To build this package you have to install the following debian packages.

```
sudo apt update
sudo apt install ros-$ROS_DISTRO-any-measurements-dev ros-$ROS_DISTRO-environment-item-dev ros-$ROS_DISTRO-environment-item-ros-dev ros-$ROS_DISTRO-environment-utils-dev ros-$ROS_DISTRO-message-logger-dev
```

## Containers

The `inspection_example_msgs` has one message and one action which leads to the four containers:

* Item
* InspectionItemGoal
* InspectionItemFeedback
* InspectionItemResult

To be compatible with the environment tools, the `Item` inherits from the `environment_item::ItemBase` class.

## Conversions

1. There is a `fromRos()` and a `toRos()` method for each container. These methods can be used to convert the Ros message type to the non Ros container and vice versa.

2. There is a `fromXmlRpc()` and a `toXmlRpc()` method for the item. These methods have to be in the `environment_utils` namespace and can be used to read from and write to the Ros parameter server.
