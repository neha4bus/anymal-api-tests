# ANYmal API Tests

This repository contains test scripts and examples for working with the ANYmal robotics API, including thermal image processing and inspection data download capabilities.

## 🚀 Features

- **ANYmal API Integration**: Complete Python SDK for ANYmal robot control and data access
- **Thermal Image Processing**: Convert mono16 thermal data to usable temperature images
- **Inspection Data Download**: Download and process inspection measurement files
- **Multiple Output Formats**: Raw data, CSV, images, and analysis reports
- **Security Best Practices**: Environment variable configuration for credentials

## 📁 Repository Structure

```
anymal-api-tests/
├── api_examples/                    # ANYmal API examples and SDK
│   ├── anymal_api_cpp/             # C++ API bindings
│   ├── anymal_api_python/          # Python API bindings
│   ├── anymal_api_proto/           # Protocol Buffer definitions
│   └── anymal_sdk_python_example/  # Python SDK examples
├── infrastructure/                  # Development infrastructure
├── inspection_examples/            # Inspection-related examples
├── mission_task_examples/          # Mission and task examples
├── environment_data/               # Environment configuration data
├── inspection_data_download_samples.py  # Main download script
├── thermal_json_converter.py       # Thermal image converter
├── view_thermal_images.py         # Thermal image viewer
├── simple_download_example.py     # Simple usage examples
├── config_example.py              # Configuration management
└── ANYmal_API_Documentation.md    # Complete API documentation
```

## 🔧 Setup

### Prerequisites

- Python 3.7+
- Required packages: `requests`, `numpy`, `opencv-python`, `matplotlib`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/neha4bus/anymal-api-tests.git
cd anymal-api-tests
```

2. Install dependencies:
```bash
pip install requests numpy opencv-python matplotlib
```

3. Configure credentials (choose one method):

**Method 1: Environment Variables**
```bash
export ANYMAL_SERVER_URL="your-server.com"
export ANYMAL_EMAIL="your-email@domain.com"
export ANYMAL_PASSWORD="your-password"
```

**Method 2: Configuration File**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## 🚀 Quick Start

### Download Inspection Data

```bash
# Interactive mode
python3 simple_download_example.py interactive

# Single file download
python3 simple_download_example.py single server.com email@domain.com password file.jpg

# Batch download
python3 simple_download_example.py batch server.com email@domain.com password file1.jpg file2.png
```

### Process Thermal Images

```bash
# Convert thermal JSON to images
python3 thermal_json_converter.py

# View thermal images
python3 view_thermal_images.py
```

### Full API Example

```bash
# Set environment variables first
python3 inspection_data_download_samples.py
```

## 📊 Thermal Image Processing

The thermal converter processes mono16 encoded thermal data:

- **Input**: JSON files with base64-encoded mono16 thermal data
- **Output**: Temperature arrays, colorized images, analysis reports
- **Conversion**: Uses ANYmal calibration formula: `temperature = gain * raw_value + offset`
- **Visualization**: JET colormap with temperature annotations

### Example Output

```
🔥 THERMAL ANALYSIS RESULTS
Temperature Range: 21.37°C - 35.73°C
Mean Temperature: 24.75°C
Hotspots (>30°C): 340 pixels (0.40% of image)
```

## 🔐 Security

- **Never commit credentials**: Use environment variables or local config files
- **Gitignore configured**: Sensitive files are automatically excluded
- **Example files only**: All committed files use placeholder credentials

## 📚 Documentation

- **[Complete API Documentation](ANYmal_API_Documentation.md)**: Full ANYmal API reference
- **[REST API Guide](ANYmal_REST_API_Postman_Guide.md)**: Postman collection for REST endpoints
- **[Usage Guide](USAGE_GUIDE.md)**: Detailed usage instructions
- **[Thermal Conversion Guide](mono16_conversion_guide.md)**: Technical details on thermal processing

## 🛠️ API Capabilities

### Core Services
- **Connection Management**: Monitor robot connectivity
- **Control Authority**: Manage robot control permissions
- **Safety Controls**: Emergency stop and power cut
- **Mission Management**: Execute and control robot missions
- **Inspection Data**: Download and process measurement files

### Data Types
- **Thermal Images**: mono16 to temperature conversion
- **Visual Images**: Standard camera feeds
- **Audio Data**: Microphone recordings
- **Sensor Data**: Battery, environmental, joint states

## 🔧 Development

### Adding New Features

1. Create feature branch
2. Add tests and documentation
3. Ensure no sensitive data in commits
4. Submit pull request

### Testing

```bash
# Test authentication (uses environment variables)
python3 inspection_data_download_samples.py

# Test thermal processing
python3 thermal_json_converter.py

# Test image viewing
python3 view_thermal_images.py
```

## 📝 License

This project contains examples and tests for the ANYmal API. Please refer to ANYbotics licensing terms for the underlying API.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure no sensitive data is committed
5. Submit a pull request

## ⚠️ Important Notes

- **Credentials**: Never commit real server URLs, emails, or passwords
- **Data Files**: Large inspection files are gitignored
- **Testing**: Use test credentials for development
- **Production**: Use environment variables for production deployments

## 📞 Support

For ANYmal API support, contact ANYbotics directly. For issues with these test scripts, please open a GitHub issue.