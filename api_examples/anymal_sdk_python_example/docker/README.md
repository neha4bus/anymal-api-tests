# Run the examples using docker

The following instructions assume that you have installed `docker` and `docker-compose` on the host machine.

## Available profiles

Different example configurations can be executed by using different `docker-compose` profiles.

The following profiles are supported:

- `inspection-demo`: The default profile. Runs the agent, server and the inspection_example client. A bagfile to replay robot inspection data needs to be provided.
- `inspection-client`: Runs the inspection_example client in standalone mode. Can be used together with the an existing API server and ANYmal.
- `connection-client`: Runs the connection_example client in standalone mode. Can be used together with the an existing API server and ANYmal.

## Build the docker images

To build the docker images, run the following command in the `docker` folder:

**Linux and macOS (Bash):**
``` bash
PPA_NAME=<ppa> PPA_USERNAME=<username> PPA_PASSWORD=<password> VERSION=<version> docker-compose --profile <profile> build
```

**Windows (Powershell):**
``` shell
$env:PPA_NAME="<ppa>";$env:PPA_USERNAME="<username>";$env:PPA_PASSWORD="<password>";$env:VERSION="<version>";docker-compose --profile <profile> build
```

Replace `<ppa>` with the PPA slug of the ANYbotics PPA `https://packages.anybotics.com/<ppa>/nightly/ubuntu` (e.g. `anymal`), `<username>` and `<password>` with the credentials for the PPA. Replace `<version>` with the ANYmal software version and `<profile>` with the `docker-compose` profile to build.

## Run the docker images

To run the docker images, run the following command in the `docker` folder:

**Linux and macOS (Bash):**
``` bash
<env>=<value> VERSION=<version> docker-compose up
```

**Windows (Powershell):**
``` shell
$env:<env>=<value>;$env:VERSION="<version>";docker-compose up
```

Replace `<version>` with the software version to run.
Depending on the chosen profile we need to pass environment variables.
Add the desired environment variable with the name `<env>` and value `<value>`.

Following variables might be interesting:

* `ROSBAG_FILE_PATH`: Required for profile `inspection-demo`.

  The path of the rosbag with inspection recordings to play back.

* `SERVER_URL`: Recommended for profile `inspection-client` and `connection-client`.

  The URL of the ANYmal API server. Default: 'localhost'.

* `SERVER_PORT`: Recommended for profile `inspection-client` and `connection-client`.

  The port of the ANYmal API server. Default: 11314.

* `CREDENTIALS_DIR`: Required for profile `inspection-client` and `connection-client` if the server to connect to has authentication enabled.

  The directory where the client credentials are stored. Default: '/none'.

* `LOGGER_LEVEL`: Optional.

  Set the logger level. Default: "debug". Options: demo, info, warn, error, critical.

Check the `docker-compose.yml` for a full list of environment variables.

For example, the `inspection-demo` profile required the variable `ROSBAG_FILE_PATH` to be set.

## Run examples with a graphical user interface

Examples that show graphical components need some more preparation steps in order for them to be executed properly.

### Installing an X server

By mounting the X server socket into the docker container, we can display the graphical user interface on the hosts display.
To install an X server follow the instructions

**Linux**

An X server should already be installed on your machine. Otherwise you can easily install one by using the package manager of your choice.

For example on Ubuntu:
```
sudo apt install xserver-xorg
```

**macOS**

1. Install the latest version of XQuartz
2. Start the XQuartz application, select `Preferences` menu, go to the `Security` tab and make sure you’ve got `Allow connections from network clients` checked.
3. Restart XQuartz to apply the settings.

**Windows**

Install the latest version of `VcXsrv`.
During the installation process use the default settings, however ensure to check the `Disable access control` checkbox.

### Execution with Display

The `DISPLAY` environment variable needs to be set, to define which display should be used for showing the GUI.
On top of that, we need to ensure that the x server can be accessed from the docker container, e.g. by disabling access restrictions.

The `docker-compose` command to execute is explained in the previous section.
To illustrate the usage, the `inspection-demo` profile is considered.
Replace `<rosbag-path>` with the path to the `rosbag` to play back and `<version>` with the software version to use.

**Linux (Bash)**

``` bash
xhost +
ROSBAG_FILE_PATH=<rosbag-path> VERSION=<version> docker-compose --profile inspection-demo up
xhost -
```

**macOS (Bash)**

``` bash
xhost +
DISPLAY=docker.for.mac.host.internal:0 ROSBAG_FILE_PATH=<rosbag-path> VERSION=<version> docker-compose --profile inspection-demo up
xhost -
```

**Windows (Powershell)**

``` shell
$env:DISPLAY="host.docker.internal:0";$env:ROSBAG_FILE_PATH="<rosbag-path>";$env:VERSION="<version>";docker-compose --profile inspection-demo up
```
