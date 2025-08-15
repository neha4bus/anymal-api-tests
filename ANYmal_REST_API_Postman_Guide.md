# ANYmal REST API - Postman Collection Guide

## Overview

While ANYmal primarily uses gRPC for its main API, there are several REST endpoints available for specific functionalities like authentication, live video streaming, and data navigation. This guide provides the REST APIs you can test with Postman.

## Base URL Configuration

Replace `{server_url}` with your ANYmal server URL (without the `api-` prefix):
```
https://your-server-domain.com
```

## Authentication

### 1. Login / Get Access Token

**Endpoint:** `POST /authentication-service/auth/login`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "email": "your-email@domain.com",
  "password": "your-password"
}
```

**Response (201 Created):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "...",
  "expiresIn": 3600
}
```

**Postman Test Script:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.accessToken);
    console.log("Access token saved to environment");
}
```

## Live Video Streaming APIs

### 2. Get LiveView Token

**Endpoint:** `GET /anymal-api/liveview/token`

**Headers:**
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters:**
```
participant: liveview_client_name
```

**Response:**
```json
{
  "token": {
    "url": "wss://livekit-server-url",
    "token": "livekit_jwt_token"
  }
}
```

### 3. Get Available Video Sources

**Endpoint:** `GET /anymal-api/liveview/sources`

**Headers:**
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters:**
```
anymal: robot_name
```

**Response:**
```json
{
  "sources": [
    {
      "frameId": "front_camera",
      "description": "Front Camera Feed",
      "type": "video"
    },
    {
      "frameId": "thermal_camera", 
      "description": "Thermal Camera Feed",
      "type": "thermal"
    },
    {
      "frameId": "rear_camera",
      "description": "Rear Camera Feed", 
      "type": "video"
    }
  ]
}
```

### 4. Enable/Configure Video Tracks

**Endpoint:** `POST /anymal-api/liveview/tracks`

**Headers:**
```json
{
  "Authorization": "Bearer {{access_token}}",
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

**Query Parameters:**
```
anymal: robot_name
```

**Request Body:**
```json
{
  "tracks": [
    {
      "frameId": "front_camera"
    },
    {
      "frameId": "thermal_camera"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Tracks configured successfully"
}
```

## Data Navigation APIs

### 5. Download Inspection Raw Data

**Endpoint:** `GET /data-navigator-api/inspections/raw-data/{filename}`

**Headers:**
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Path Parameters:**
```
filename: inspection_data_filename.jpg
```

**Response:** Binary data (image/video file)

**Response Codes:**
- `200 OK`: File downloaded successfully
- `404 Not Found`: File not uploaded yet or doesn't exist
- `401 Unauthorized`: Invalid or expired token

## Postman Collection Setup

### Environment Variables

Create a Postman environment with these variables:

```json
{
  "server_url": "your-server-domain.com",
  "access_token": "",
  "anymal_name": "your_robot_name",
  "participant_name": "postman_client"
}
```

### Collection Structure

```
ANYmal REST API Collection/
├── Authentication/
│   └── Login
├── LiveView/
│   ├── Get LiveView Token
│   ├── Get Video Sources  
│   └── Configure Video Tracks
└── Data Navigation/
    └── Download Inspection Data
```

### Pre-request Scripts

For authenticated endpoints, add this pre-request script:

```javascript
// Check if access token exists and is not expired
const token = pm.environment.get("access_token");
if (!token) {
    console.log("No access token found. Please login first.");
}
```

### Common Response Tests

Add these test scripts to validate responses:

```javascript
// Test for successful authentication
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has access token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('accessToken');
});

// Test for successful API calls
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 5000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

## Sample Postman Requests

### 1. Complete Authentication Flow

```bash
# Step 1: Login
POST https://{{server_url}}/authentication-service/auth/login
Content-Type: application/json

{
  "email": "operator@company.com",
  "password": "secure_password"
}

# Step 2: Use token for subsequent requests
GET https://{{server_url}}/anymal-api/liveview/sources?anymal={{anymal_name}}
Authorization: Bearer {{access_token}}
```

### 2. LiveView Setup Flow

```bash
# Step 1: Get available sources
GET https://{{server_url}}/anymal-api/liveview/sources?anymal=robot_01
Authorization: Bearer {{access_token}}

# Step 2: Get LiveView room token
GET https://{{server_url}}/anymal-api/liveview/token?participant=postman_client
Authorization: Bearer {{access_token}}

# Step 3: Configure desired video tracks
POST https://{{server_url}}/anymal-api/liveview/tracks?anymal=robot_01
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "tracks": [
    {"frameId": "front_camera"},
    {"frameId": "thermal_camera"}
  ]
}
```

## Error Handling

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created (login successful)
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": "Authentication failed"
  }
}
```

## Security Considerations

### SSL/TLS Configuration

- Use HTTPS for all requests
- Verify SSL certificates in production
- For testing, you can disable SSL verification in Postman settings

### Token Management

- Access tokens typically expire after 1 hour
- Store tokens securely in environment variables
- Implement token refresh logic for long-running sessions
- Never log or expose tokens in plain text

### Rate Limiting

- Be mindful of API rate limits
- Implement appropriate delays between requests
- Monitor response headers for rate limit information

## Limitations

### REST vs gRPC

**Available via REST:**
- Authentication and token management
- LiveView video streaming setup
- Basic data download operations

**Only available via gRPC:**
- Robot control commands
- Mission management
- Real-time sensor data
- Control authority management
- Safety system controls

### Real-time Operations

For real-time robot control and monitoring, you'll need to use the gRPC API with appropriate client libraries. The REST endpoints are primarily for:

1. **Authentication** - Getting access tokens
2. **LiveView Setup** - Configuring video streams  
3. **Data Access** - Downloading inspection results

## Next Steps

After testing these REST endpoints in Postman:

1. **For Robot Control**: Implement gRPC clients using the Protocol Buffer definitions
2. **For Live Video**: Use WebRTC/LiveKit clients to consume video streams
3. **For Integration**: Combine REST authentication with gRPC operations

This REST API subset provides the foundation for authentication and media streaming, while the full robot control capabilities require the gRPC interface.