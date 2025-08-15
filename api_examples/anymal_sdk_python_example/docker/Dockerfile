##############
# Base image #
##############

# Start from Ubuntu 20.04.
FROM ubuntu:focal AS base

# Build arguments to be configured.
ARG username
ARG password
ARG ppa
ARG version

# Configure PPAs and install necessary tools.
RUN apt update && \
    apt install -y lsb-release gnupg2 ca-certificates curl bash netcat && \
    sh -c 'echo "deb [arch=amd64] https://packages-ros.anybotics.com/ros/${version}/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros.list' && \
    curl -fsSL https://packages.anybotics.com/gpg | apt-key add - && \
    sh -c 'echo "machine packages.anybotics.com login ${username} password ${password}" > /etc/apt/auth.conf.d/packages.anybotics.com.conf' && \
    chmod 600 /etc/apt/auth.conf.d/packages.anybotics.com.conf && \
    sh -c 'echo "deb [arch=amd64] https://packages.anybotics.com/${ppa}/${version}/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/anybotics.list' && \
    curl -fsSL https://packages.anybotics.com/gpg | apt-key add - && \
    apt update

#################
# Roscore image #
#################

FROM base AS api-roscore

RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-roslaunch

COPY bin/run_roscore.sh /bin/run_roscore.sh
ENTRYPOINT ["/bin/bash"]
CMD ["/bin/run_roscore.sh"]


###############
# Agent image #
###############

FROM base AS api-agent

RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-anymal-data-sync-agent

COPY bin/run_agent.sh /bin/run_agent.sh
ENTRYPOINT ["/bin/bash"]
CMD ["/bin/run_agent.sh"]


################
# Client image #
################

FROM base AS api-client

RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-anymal-sdk-python-example

COPY bin/run_example.sh /bin/run_example.sh
ENTRYPOINT ["/bin/run_example.sh"]
CMD []


########################
# Data-generator image #
########################

FROM base AS api-data-generator

RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-rosbag

COPY bin/run_data_generator.sh /bin/run_data_generator.sh
ENTRYPOINT ["/bin/run_data_generator.sh"]
CMD []


################
# Server image #
################

FROM base AS api-server

RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-noetic-anymal-data-sync-server

COPY bin/run_server.sh /bin/run_server.sh
ENTRYPOINT ["/bin/bash"]
CMD ["/bin/run_server.sh"]
