# ANYmal API Documentation

## Overview

The ANYmal API is a comprehensive gRPC-based interface for controlling and interacting with ANYmal quadruped robots. The API provides multi-language support with implementations in C++, Python, and Protocol Buffers definitions.

## API Structure

### Core Components

- **anymal_api_proto**: Protocol Buffer definitions for all services and messages
- **anymal_api_cpp**: C++ generated code and bindings  
- **anymal_api_python**: Python generated code and bindings
- **anymal_sdk_python_example**: Complete Python SDK with usage examples

### Version Information
- Current Version: 0.1.7 (API bindings)
- SDK Version: 0.7.10 (Python SDK examples)
- License: Proprietary

## Core Services

### 1. Connection Management

**ConnectionService** - Monitor robot connectivity status

```protobuf
service ConnectionService {
  rpc GetConnectionState(GetConnectionStateRequest) returns (GetConnectionStateResponse);
}
```

**Connection States:**
- `CS_DISCONNECTED`: Robot not connected
- `CS_PARTIAL`: Partially connected (limited functionality)
- `CS_CONNECTED`: Fully connected

### 2. Control Authority

**ControlAuthorityService** - Manage robot control permissions

```protobuf
service ControlAuthorityService {
  rpc ControlAuthority(stream ControlAuthorityClientMsg) returns (stream ControlAuthorityServerMsg);
  rpc GetControlAuthorityStatus(GetControlAuthorityStatusRequest) returns (GetControlAuthorityStatusResponse);
}
```

**Client Types (Priority Order):**
- `CLCT_ON_SITE`: Highest priority (on-site operator)
- `CLCT_REMOTE`: Medium priority (remote operator)  
- `CLCT_AUTOMATED`: Lowest priority (automated systems)

**Control Flow:**
1. Request control authority with client type
2. Send periodic heartbeats (every 15 seconds)
3. Release control when done

### 3. Safety Controls

**ProtectiveStopService** - Emergency stop functionality`
``protobuf
service ProtectiveStopService {
  rpc ProtectiveStop(ProtectiveStopRequest) returns (ProtectiveStopServiceResponse);
}
```

**PowerCutService** - Complete power shutdown

```protobuf
service PowerCutService {
  rpc PowerCut(PowerCutRequest) returns (PowerCutServiceResponse);
}
```

**Safety Commands:**
- `SCMD_ENGAGE`: Activate safety stop/power cut
- `SCMD_DISENGAGE`: Deactivate safety stop/power cut

### 4. User Interaction Modes

**UserInteractionModeService** - Control robot operation modes

```protobuf
service UserInteractionModeService {
  rpc GetUserInteractionMode(GetUserInteractionModeRequest) returns (GetUserInteractionModeResponse);
  rpc SetUserInteractionMode(SetUserInteractionModeRequest) returns (SetUserInteractionModeResponse);
}
```

**Interaction Modes:**
- `UIM_AUTONOMOUS`: Robot runs predefined/ad-hoc missions
- `UIM_MANUAL`: Direct control via OPC/Field Operator/API
- `UIM_AUTONOMOUS_REACTION`: Robot reacts to events (e.g., low battery)

### 5. Mission Management

**MissionService** - Execute and manage robot missions

```protobuf
service MissionService {
  rpc ControlMission(ControlMissionRequest) returns (ControlMissionResponse);
  rpc GetPredefinedMissions(GetPredefinedMissionsRequest) returns (GetPredefinedMissionsResponse);
  rpc GetMission(GetMissionRequest) returns (GetMissionResponse);
  rpc CreateMission(CreateMissionRequest) returns (CreateMissionResponse);
  rpc DeleteMission(DeleteMissionRequest) returns (DeleteMissionResponse);
  rpc UpdateMission(UpdateMissionRequest) returns (UpdateMissionResponse);
}
```

**Mission Control Commands:**
- Start missions (predefined or ad-hoc)
- Pause running missions
- Resume paused missions

**Mission Status Codes:**
- `CMS_OK`: Operation successful
- `CMS_ERROR_REQUEST_INVALID`: Malformed request
- `CMS_ERROR_MISSION_UNKNOWN`: Mission not found
- `CMS_ERROR_PROTECTIVE_STOP_ENABLED`: Safety stop active
- `CMS_ERROR_CONTROL_LEASE_UNOWNED`: No control authority

## Data Types and Sensors

### 1. Image and Media Types

**Standard Image:**
```protobuf
message Image {
  int32 width = 1;
  int32 height = 2;
  string encoding = 3;  // Format: bgr8, jpeg, etc.
  int32 step = 4;
  bytes data = 5;
}
```

**Thermal Image:**
```protobuf
message ThermalImage {
  Image image = 1;  // Raw thermal data
  double gain = 2;  // Temperature conversion: temp = gain * raw + offset
  double offset = 3;
}
```

**Acoustic Image:**
```protobuf
message AcousticImage {
  Image image = 1;
  FloatRange frequency_range = 2;
}
```

**Audio Data:**
```protobuf
message AudioData {
  int32 sampling_rate = 1;  // Hz
  int32 channels = 2;
  int32 depth = 3;  // Bits per sample
  bytes data = 4;
  float duration = 5;  // Seconds
}
```

### 2. Robot State Information

**Battery State:**
```protobuf
message BatteryState {
  MeasurementDynamics state_of_charge = 1;  // 0-1 range
  MeasurementDynamics voltage = 2;  // Volts
  BatteryStatus status = 3;
}
```

**Battery Status Values:**
- `BS_CHARGING`: Currently charging
- `BS_DISCHARGING`: Currently discharging  
- `BS_NOT_CONNECTED`: No battery connected
- `BS_ERROR`: Battery error state
- `BS_PERMANENT_FAILURE`: Battery needs replacement

**Main Body Environmental State:**
```protobuf
message MainBodyState {
  MeasurementDynamics relative_humidity = 1;      // 0-1 range
  MeasurementDynamics differential_pressure = 2;  // mbar
  MeasurementDynamics temperature = 3;            // Celsius
}
```

### 3. Spatial and Navigation

**Pose Representation:**
```protobuf
message Pose {
  Vector3 position = 1;    // x, y, z coordinates
  Quaternion orientation = 2;  // Rotation quaternion
}
```

**Navigation Goals:**
```protobuf
message NavigationGoal {
  string uid = 1;        // Unique identifier
  string label = 2;      // Human-readable name
  Pose pose = 3;         // Target pose
  Tolerance tolerance = 4;  // Position/rotation tolerances
}
```

## Inspection Capabilities

### Measurement Types

**Inspection Measurement Types:**
- `IMT_THERMAL`: Thermal camera images
- `IMT_VISUAL`: Zoom camera images  
- `IMT_AUDITIVE`: Microphone recordings
- `IMT_VIDEO`: Video recordings
- `IMT_CONCENTRATION`: Gas concentration measurements
- `IMT_ACOUSTIC_IMAGE`: Acoustic camera images
- `IMT_CUSTOM`: Custom payload measurements

### Interpretation Types

**Analysis Capabilities:**
- `IIT_THERMAL_HOTSPOT_DETECTION`: Thermal anomaly detection
- `IIT_VISUAL_READOUT`: Gauge/display reading
- `IIT_VISUAL_OBJECT_DETECTION`: Object recognition
- `IIT_AUDITIVE_FREQUENCY_ANALYSIS`: Audio frequency analysis
- `IIT_LEAK_DETECTION`: Acoustic leak detection
- `IIT_PARTIAL_DISCHARGE_DETECTION`: Electrical fault detection
- `IIT_CONCENTRATION`: Gas concentration analysis

### Substance Concentration Levels

**Concentration Assessment:**
- `SCL_NORMAL`: Within normal range
- `SCL_LOW_WARNING/LOW_ALARM`: Below thresholds
- `SCL_HIGH_WARNING/HIGH_ALARM`: Above thresholds
- `SCL_NOT_ENOUGH_MEASUREMENTS`: Insufficient data

## Live Video Streaming

### LiveView Integration

The API includes LiveKit-based video streaming capabilities:

**Key Features:**
- Real-time video streaming from robot cameras
- WebRTC-based low-latency transmission
- Multi-camera support with selective streaming
- Authentication via server tokens

**Usage Pattern:**
1. Authenticate with server to get access token
2. Request LiveView room token
3. Connect to LiveKit room
4. Subscribe to desired camera feeds
5. Send periodic heartbeats to maintain streams

## Error Handling

### Service Call Status

**ANYmal Service Status:**
- `ASCS_OK`: Request successful
- `ASCS_ERROR_ANYMAL_UNKNOWN`: Robot not known
- `ASCS_ERROR_ANYMAL_OFFLINE`: Robot offline
- `ASCS_ERROR_PERMISSION`: Insufficient permissions
- `ASCS_ERROR_UNKNOWN`: Unknown error

**Data Server Status:**
- `DSSCS_OK`: Request successful
- `DSSCS_ERROR`: Request failed

### State Estimator Status

**Estimator States:**
- `STATE_ESTIMATOR_STATE_OK`: Normal operation
- `STATE_ESTIMATOR_STATE_UNINITIALIZED`: Not ready
- `STATE_ESTIMATOR_STATE_ERROR_ESTIMATOR`: Estimator fault
- `STATE_ESTIMATOR_STATE_ERROR_SENSOR`: Sensor fault

## SDK Usage Examples

### Python SDK Connection Example

```python
from anymal_sdk_example import ANYmalExampleHandler, parse_cli_arguments

# Initialize connection
args = parse_cli_arguments()
anymal_name = "your_robot_name"
handler = ANYmalExampleHandler("client-name", anymal_name, args)

# Create communication interface
handler.create_communication_interface()
handler.register_connection_callbacks()

# Use the API...
handler.close_communication_interface()
```

### Control Authority Example

```python
# Take control (requires appropriate client type)
take_control_request = TakeControlRequestSdk()
take_control_request.anymal_name = anymal_name
take_control_request.client_type = ControlAuthorityClientType.CLCT_REMOTE

# Send periodic heartbeats
# Release control when done
```

### Mission Execution Example

```python
# Set to autonomous mode
set_mode_request = SetUserInteractionModeRequest()
set_mode_request.anymal_name = anymal_name
set_mode_request.user_interaction_mode = UserInteractionMode.UIM_AUTONOMOUS

# Start a mission
start_request = StartMissionRequest()
start_request.anymal_name = anymal_name
start_request.mission_id = "predefined_mission_id"

control_request = ControlMissionRequest()
control_request.anymal_name = anymal_name
control_request.start.CopyFrom(start_request)
```

## Authentication and Security

### Server Authentication

The API uses token-based authentication:

1. **Login Endpoint:** `/authentication-service/auth/login`
2. **Credentials:** Email and password
3. **Token:** Bearer token for subsequent requests
4. **SSL:** Configurable certificate verification

### Access Control

- Control authority system prevents conflicts
- Priority-based access (on-site > remote > automated)
- Heartbeat mechanism ensures active control
- Automatic timeout for inactive clients

## Best Practices

### Connection Management
- Always check connection status before operations
- Handle connection loss gracefully with reconnection logic
- Use appropriate client types for priority management

### Safety Considerations
- Always verify robot state before issuing commands
- Monitor protective stop and power cut status
- Implement proper error handling for safety-critical operations
- Test emergency stop procedures

### Mission Planning
- Validate navigation goals are reachable
- Ensure robot can return to docking station
- Monitor battery levels during long missions
- Plan for environmental constraints

### Resource Management
- Release control authority when not needed
- Close communication interfaces properly
- Handle streaming resources efficiently
- Monitor system resource usage

## Integration Guidelines

### gRPC Configuration
- Use appropriate timeouts for operations
- Implement retry logic for transient failures
- Configure proper SSL/TLS settings
- Handle streaming connections appropriately

### Multi-Language Support
- C++ for performance-critical applications
- Python for rapid prototyping and scripting
- Protocol Buffers for cross-platform compatibility

### Deployment Considerations
- Network latency affects real-time operations
- Bandwidth requirements for video streaming
- Security implications of remote access
- Monitoring and logging requirements

This documentation provides a comprehensive overview of the ANYmal API capabilities, enabling developers to effectively integrate with and control ANYmal robots across various applications and use cases.