\page page_inspection_example_plugin Inspection Example Plugin

# Inspection Example Plugin

## Overview

This package contains an inspection plugin. 
The plugin inherits from `any_inspection_ros::InspectionPluginBase` instead of `any_inspection_ros::InspectionPluginInterfaceRos`. 
This has the advantage, that an action server is already implemented and setup at the beginning.

## Requirements

To build this package you have to install the following debian packages.

```
sudo apt update
sudo apt install ros-$ROS_DISTRO-any-inspection-ros-dev ros-$ROS_DISTRO-inspection-example-dev ros-$ROS_DISTRO-inspection-example-msgs-dev ros-$ROS_DISTRO-message-logger-dev ros-$ROS_DISTRO-pluginlib ros-$ROS_DISTRO-roscpp
```
