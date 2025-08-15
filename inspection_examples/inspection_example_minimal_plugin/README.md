\page page_inspection_example_minimal_plugin Inspection Example Minimal Plugin

# Inspection Example Minimal Plugin

## Overview

This package contains a minimal inspection plugin. 
The minimal plugin can be either used as a minimal plugin interface to implement a custom routine (e.g. action/service server), 
or to implement an inspection task (e.g. reset inspection payload) that doesn't require an action server. For inspection tasks, 
which require an action server the **Inspection Example Plugin** is probably the better starting point.

## Requirements

To build this package you have to install the following debian packages.

```
sudo apt update
sudo apt install ros-$ROS_DISTRO-any-inspection-ros-dev ros-$ROS_DISTRO-message-logger-dev ros-$ROS_DISTRO-pluginlib
```
