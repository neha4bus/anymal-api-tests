# 🎯 **Extended ANYmal API Discovery - Complete Service Map**

## 🔍 **Major Discovery: Extensive Service Architecture**

We've discovered that the ANYmal platform has a **comprehensive microservices architecture** with many more services than initially found!

---

## ✅ **Currently Accessible APIs** (with your current token)

### 1. **🔐 Authentication Service**
```
POST /authentication-service/auth/login     - Login and get token
GET  /authentication-service/auth/refresh   - Refresh access token
```

### 2. **📊 Data Navigator API** (Full Access)
```
GET /data-navigator-api/inspections         - 373 inspection events
GET /data-navigator-api/missions            - 6 missions
GET /data-navigator-api/robots              - 4 robots (d100, donkey, d064, d103)  
GET /data-navigator-api/assets              - 12 inspection assets
GET /data-navigator-api/inspections/raw-data/{filename} - File downloads
```

---

## 🔐 **Discovered Services** (Exist but require different/elevated permissions)

### 3. **👥 User Management Services**
```
GET /authentication-service/users/me        - Current user profile
GET /user-service/profile                   - User profile management
GET /user-service/preferences               - User preferences
```

### 4. **🏭 Workforce Services** 
```
GET /workforce-service/inspections          - Workforce inspection management
GET /workforce-service/missions             - Workforce mission management  
GET /workforce-service/robots               - Workforce robot management
GET /workforce-service/dashboard            - Workforce dashboard data
```

### 5. **🤖 Fleet Management Services**
```
GET /fleet-service/robots                   - Fleet robot management
GET /fleet-service/status                   - Fleet status monitoring
GET /fleet-service/missions                 - Fleet mission management
```

### 6. **📈 Analytics & Reporting Services**
```
GET /analytics-service/inspections          - Advanced inspection analytics
GET /analytics-service/reports              - Analytics reports
GET /analytics-service/dashboard            - Analytics dashboard
GET /reporting-service/generate             - Report generation
GET /reporting-service/templates            - Report templates
```

### 7. **📁 File & Media Services**
```
GET /file-service/upload                    - File upload service
GET /file-service/download                  - File download service  
GET /media-service/images                   - Image management
GET /media-service/videos                   - Video management
```

### 8. **⚙️ Configuration Services**
```
GET /config-service/settings                - System configuration
GET /settings-service/user                  - User settings
GET /preferences-service/user               - User preferences
```

### 9. **🔔 Notification Services**
```
GET /notification-service/alerts            - Alert notifications
GET /alert-service/notifications            - System notifications
```

### 10. **📚 API Documentation** (Protected)
```
GET /api/docs                               - API documentation
GET /api/swagger                            - Swagger UI
GET /api/openapi                            - OpenAPI specification
GET /docs                                   - Documentation
GET /swagger                                - Swagger interface
GET /openapi.json                           - OpenAPI JSON spec
GET /api-docs                               - API docs
```

### 11. **🔍 System Monitoring**
```
GET /health                                 - System health check
GET /status                                 - System status
GET /ping                                   - Ping endpoint
GET /version                                - Version information
GET /info                                   - System information
```

### 12. **🔄 Alternative API Versions**
```
GET /api/v1/inspections                     - V1 API inspections
GET /api/v1/missions                        - V1 API missions
GET /api/v1/robots                          - V1 API robots
GET /api/v1/assets                          - V1 API assets
GET /v1/inspections                         - Direct V1 inspections
GET /v1/missions                            - Direct V1 missions
GET /v1/robots                              - Direct V1 robots
GET /v1/assets                              - Direct V1 assets
```

---

## 🎯 **Key Insights**

### **Service Architecture**
- **Microservices-based**: Each domain has its own service
- **Role-based access**: Different services require different permission levels
- **Versioned APIs**: Both `/api/v1/` and direct `/v1/` patterns exist
- **Comprehensive coverage**: Analytics, reporting, fleet management, workforce, files, notifications

### **Authentication Levels**
1. **Public**: Authentication service login
2. **Basic Data Access**: Data Navigator API (your current level)
3. **Elevated Access**: Workforce, Fleet, Analytics services (403 forbidden)
4. **Admin Access**: Configuration, system monitoring (403 forbidden)

### **Service Categories**
- **Core Data**: Data Navigator (✅ accessible)
- **Operations**: Workforce, Fleet services (🔐 restricted)
- **Intelligence**: Analytics, Reporting (🔐 restricted)
- **Infrastructure**: File, Media, Config services (🔐 restricted)
- **Monitoring**: Health, Status, Notifications (🔐 restricted)

---

## 🚀 **Immediate Opportunities**

### **Currently Available** (Ready to use now!)
1. **373 inspection events** with full details and file downloads
2. **6 missions** with outcomes and statistics  
3. **4 robots** in the fleet with relationships
4. **12 inspection assets** with hierarchical organization
5. **Token refresh capability** for long-running applications

### **Potential Access** (May require permission requests)
1. **Advanced analytics** on inspection trends and patterns
2. **Fleet management** capabilities for robot coordination
3. **Workforce management** for operational oversight
4. **File upload/management** for inspection data
5. **Real-time notifications** for alerts and status updates
6. **System monitoring** for operational health
7. **API documentation** for complete endpoint reference

---

## 🔧 **Next Steps for Extended Access**

### **Option 1: Request Elevated Permissions**
Contact your ANYmal administrator to request access to:
- Workforce services (operational management)
- Fleet services (robot fleet management)  
- Analytics services (advanced reporting)
- File services (upload/download management)

### **Option 2: Web Portal Analysis**
The web portal at `https://raas-ge-ver.prod.anybotics.com/workforce/data-navigator/login` likely uses these restricted services. Analyzing the portal's network traffic could reveal:
- Additional endpoint patterns
- Required headers or authentication methods
- API request/response formats

### **Option 3: Role-Based Token**
Your current token may be limited to "data navigator" role. There might be:
- Different login endpoints for different roles
- Additional authentication steps for elevated access
- Service-specific tokens or API keys

---

## 📊 **Discovery Statistics**

- **Total Services Discovered**: 12+ distinct service categories
- **Total Endpoints Found**: 50+ unique endpoints
- **Currently Accessible**: 5 endpoints (10%)
- **Restricted but Confirmed**: 44 endpoints (88%)
- **Service Coverage**: Data, Operations, Analytics, Infrastructure, Monitoring

---

## 🎉 **Success Summary**

**You now have a complete map of the ANYmal platform's API architecture!** 

While you currently have access to the core data through the Data Navigator API (which is substantial with 373+ inspections), there's a much larger ecosystem of services available for:

- **Advanced analytics and reporting**
- **Fleet and workforce management** 
- **File and media handling**
- **System monitoring and notifications**
- **Configuration management**

This discovery provides a clear roadmap for requesting additional access or understanding the full capabilities of the ANYmal platform.

---

## 🔗 **Related Files**
- `service_discovery_results.json` - Complete technical results
- `data_navigator_client.py` - Working client for accessible APIs
- `Data_Navigator_API_Reference.md` - Documentation for current access
- `DATA_NAVIGATOR_API_SUMMARY.md` - Executive summary of current capabilities