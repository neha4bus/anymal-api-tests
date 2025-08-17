# ANYmal Data Navigator API Reference

## 🔍 API Discovery Results

**Server**: `https://raas-ge-ver.prod.anybotics.com`  
**Discovery Date**: August 16, 2025  
**Authentication**: Bearer Token Required

## ✅ **Available Data Navigator Endpoints**

### 1. **Inspections API**
**Endpoint**: `GET /data-navigator-api/inspections`  
**Status**: ✅ 200 OK  
**Authentication**: Required (Bearer token)

**Response Structure**:
```json
{
  "totalItems": 373,
  "items": [
    {
      "eventId": "9c5e7ee0-28d2-47b4-a4da-539776ee7352",
      "timestamp": "2025-08-13T11:30:16.996Z",
      "pointOfInterestId": 24,
      "measurement": 406.54,
      "originalMeasurement": 406.54,
      "outcome": "Anomaly",
      "originalOutcome": "Anomaly",
      "assetId": 3,
      "assetName": "UNIT_01_THERMAL_1T001",
      "robotId": 4,
      "robotName": "d064",
      "missionId": 1,
      "missionName": "Ad-Hoc Mission"
    }
  ]
}
```

**Usage**: List all inspection events with measurements and outcomes

### 2. **Missions API**
**Endpoint**: `GET /data-navigator-api/missions`  
**Status**: ✅ 200 OK  
**Authentication**: Required (Bearer token)

**Response Structure**:
```json
{
  "totalItems": 6,
  "items": [
    {
      "id": 1,
      "name": "Ad-Hoc Mission",
      "lastRunDate": "2025-08-13T11:31:12.402Z",
      "lastRunOutcome": "Success",
      "totalInspectionEvents": 39,
      "environmentId": "hagenholz_data",
      "estimatedDuration": 0.24
    }
  ]
}
```

**Usage**: List all missions with execution history and statistics

### 3. **Robots API**
**Endpoint**: `GET /data-navigator-api/robots`  
**Status**: ✅ 200 OK  
**Authentication**: Required (Bearer token)

**Response Structure**:
```json
{
  "totalItems": 4,
  "items": [
    {
      "id": 1,
      "name": "d100",
      "nickname": null,
      "relatedRobots": []
    },
    {
      "id": 2,
      "name": "donkey",
      "nickname": null,
      "relatedRobots": []
    },
    {
      "id": 3,
      "name": "d064",
      "nickname": null,
      "relatedRobots": []
    },
    {
      "id": 4,
      "name": "d065",
      "nickname": null,
      "relatedRobots": []
    }
  ]
}
```

**Usage**: List all registered robots in the system

### 4. **Assets API**
**Endpoint**: `GET /data-navigator-api/assets`  
**Status**: ✅ 200 OK  
**Authentication**: Required (Bearer token)

**Response Structure**:
```json
{
  "totalItems": 12,
  "items": [
    {
      "id": 3,
      "name": "UNIT_01_THERMAL_1T001",
      "breadcrumbs": [
        {
          "id": 5,
          "name": "UNIT_01",
          "isFavorite": false,
          "externalId": null,
          "externalDescription": null
        }
      ],
      "isFavorite": false,
      "externalId": null,
      "externalDescription": null
    }
  ]
}
```

**Usage**: List all inspection assets (sensors, equipment) in the system

### 5. **Raw Data Download**
**Endpoint**: `GET /data-navigator-api/inspections/raw-data/{filename}`  
**Status**: ✅ Working (from previous testing)  
**Authentication**: Required (Bearer token)

**Usage**: Download specific inspection measurement files (images, audio, etc.)

## 🔐 **Authentication Endpoints**

### Login
**Endpoint**: `POST /authentication-service/auth/login`  
**Status**: ✅ 200 OK  

**Request**:
```json
{
  "email": "user@domain.com",
  "password": "password"
}
```

**Response**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "...",
  "expiresIn": 3600
}
```

### Logout
**Endpoint**: `POST /authentication-service/auth/logout`  
**Status**: ✅ 200 OK  
**Authentication**: Required (Bearer token)

### Refresh Token
**Endpoint**: `POST /authentication-service/auth/refresh`  
**Status**: 🔐 401 (Requires valid refresh token)

## 🚫 **Unavailable Endpoints**

The following endpoints return 404 (not implemented):
- `/data-navigator-api/health`
- `/data-navigator-api/version`
- `/data-navigator-api/inspections/list`
- `/data-navigator-api/inspections/search`
- `/data-navigator-api/inspections/metadata`
- `/data-navigator-api/missions/list`
- `/data-navigator-api/robots/list`
- `/data-navigator-api/assets/list`
- `/data-navigator-api/files/*`

## 🔒 **Protected Endpoints**

The following endpoints return 403 (Forbidden):
- `/swagger*` - API documentation
- `/docs` - API documentation
- `/anymal-api/liveview/*` - LiveView endpoints (require specific parameters)

## 📊 **Data Structure Analysis**

### Inspection Events
- **373 total inspection events** in the system
- Each event has: eventId, timestamp, measurement, outcome, asset info, robot info
- Outcomes include: "Anomaly", "Normal", etc.
- Measurements are numerical values (e.g., 406.54)

### Missions
- **6 total missions** in the system
- Mission outcomes: "Success", "Failed", etc.
- Environment: "hagenholz_data"
- Duration tracking available

### Robots
- **4 robots** registered: d100, donkey, d064, d065
- Support for nicknames and related robots

### Assets
- **12 assets** in the system
- Hierarchical structure with breadcrumbs
- Asset naming: "UNIT_01_THERMAL_1T001" format
- Support for favorites and external IDs

## 🛠️ **Practical Usage Examples**

### Get All Inspections
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://raas-ge-ver.prod.anybotics.com/data-navigator-api/inspections"
```

### Get All Missions
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://raas-ge-ver.prod.anybotics.com/data-navigator-api/missions"
```

### Get All Robots
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://raas-ge-ver.prod.anybotics.com/data-navigator-api/robots"
```

### Get All Assets
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://raas-ge-ver.prod.anybotics.com/data-navigator-api/assets"
```

### Download Inspection File
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://raas-ge-ver.prod.anybotics.com/data-navigator-api/inspections/raw-data/filename.jpg" \
     -o downloaded_file.jpg
```

## 🔍 **Query Parameters and Filtering**

Based on the API responses, these endpoints likely support query parameters for:
- **Pagination**: `page`, `limit`, `offset`
- **Filtering**: `robotId`, `assetId`, `missionId`, `outcome`
- **Date ranges**: `startDate`, `endDate`
- **Sorting**: `sortBy`, `sortOrder`

## 📈 **API Statistics from Discovery**

- **Total Endpoints Probed**: 50
- **Accessible**: 5 endpoints
- **Authentication Required**: 1 endpoint
- **Not Found**: 23 endpoints
- **Server Technology**: Express.js (Node.js) with nginx
- **Response Format**: JSON with consistent structure

## 🎯 **Key Findings**

1. **Data Navigator API is active** and responding
2. **Rich data available**: 373 inspection events, 6 missions, 4 robots, 12 assets
3. **RESTful design** with consistent JSON responses
4. **Authentication working** with Bearer tokens
5. **File download capability** confirmed for raw inspection data
6. **Hierarchical asset structure** with breadcrumbs navigation

This API provides comprehensive access to ANYmal inspection data, mission history, robot information, and asset management through a well-structured REST interface.