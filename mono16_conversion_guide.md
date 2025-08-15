# ANYmal API: mono16 to Raw File Conversion Guide

## Overview

The ANYmal API uses `mono16` encoding for thermal images, which represents 16-bit single-channel (monochrome) raw thermal data. This guide explains how to convert mono16 data to actual temperature values and usable image files.

## 🔥 Thermal Image Data Structure

### Protocol Buffer Definition
```protobuf
message ThermalImage {
  Image image = 1;      // Raw thermal data in mono16 format
  double gain = 2;      // Temperature conversion gain factor
  double offset = 3;    // Temperature conversion offset
}

message Image {
  int32 width = 1;      // Image width in pixels
  int32 height = 2;     // Image height in pixels  
  string encoding = 3;  // "mono16" for thermal images
  int32 step = 4;       // Bytes per row (width * 2 for 16-bit)
  bytes data = 5;       // Raw binary image data
}
```

## 🔧 Conversion Process

### Step 1: Extract Raw mono16 Data

The `mono16` encoding means:
- **16-bit unsigned integers** (uint16)
- **Single channel** (monochrome/grayscale)
- **Raw sensor values** (not temperatures yet)

```python
import numpy as np

def extract_mono16_data(image):
    """Extract raw uint16 values from mono16 encoded image"""
    if image.encoding == "mono16":
        # Convert bytes to uint16 array
        np_buffer = np.frombuffer(image.data, dtype="uint16")
        
        # Reshape to image dimensions (height, width, 1 channel)
        raw_image = np.ndarray(
            shape=(image.height, image.width, 1), 
            dtype="uint16", 
            buffer=np_buffer
        )
        return raw_image
    else:
        raise ValueError(f"Expected mono16 encoding, got {image.encoding}")
```

### Step 2: Convert Raw Values to Temperature

The key formula from the API documentation:
```
temperature = gain * raw_value + offset
```

```python
def convert_to_temperature(thermal_image):
    """Convert mono16 raw values to actual temperatures"""
    # Extract raw mono16 data
    raw_image = extract_mono16_data(thermal_image.image)
    
    # Apply linear conversion formula
    temperature_image = raw_image * thermal_image.gain + thermal_image.offset
    
    return temperature_image
```

### Step 3: Process for Display/Export

```python
import cv2 as cv

def convert_thermal_to_displayable(thermal_image):
    """Convert thermal image to displayable format with color mapping"""
    
    # Get temperature values
    temp_image = convert_to_temperature(thermal_image)
    
    # Normalize to 0-255 range for display
    normalized = cv.normalize(
        temp_image,
        None,
        alpha=0,
        beta=255,
        norm_type=cv.NORM_MINMAX,
        dtype=cv.CV_8U
    )
    
    # Apply color map (e.g., JET colormap for thermal visualization)
    colored_image = cv.applyColorMap(normalized, cv.COLORMAP_JET)
    
    return colored_image, temp_image
```

## 📊 Complete Example Implementation

Based on the ANYmal SDK code:

```python
import numpy as np
import cv2 as cv
from typing import Tuple
import anymal_api_proto as api

class ThermalImageProcessor:
    """Complete thermal image processing from mono16 to usable formats"""
    
    @staticmethod
    def process_mono16_thermal(thermal_image: api.ThermalImage) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Complete processing pipeline for mono16 thermal images
        
        Args:
            thermal_image: ANYmal ThermalImage with mono16 encoding
            
        Returns:
            tuple: (display_image, temperature_array, metadata)
        """
        image = thermal_image.image
        
        # Validate encoding
        if image.encoding != "mono16":
            raise ValueError(f"Expected mono16 encoding, got {image.encoding}")
        
        # Step 1: Extract raw uint16 data
        raw_buffer = np.frombuffer(image.data, dtype="uint16")
        raw_image = raw_buffer.reshape((image.height, image.width))
        
        # Step 2: Convert to temperature using calibration
        temperature_image = raw_image * thermal_image.gain + thermal_image.offset
        
        # Step 3: Create displayable image with color mapping
        normalized = cv.normalize(
            temperature_image,
            None,
            alpha=0,
            beta=255,
            norm_type=cv.NORM_MINMAX,
            dtype=cv.CV_8U
        )
        
        # Apply thermal color map
        display_image = cv.applyColorMap(normalized, cv.COLORMAP_JET)
        
        # Add temperature annotations
        min_temp = temperature_image.min()
        max_temp = temperature_image.max()
        
        cv.putText(display_image, f"Min: {min_temp:.2f}°C", 
                  (10, image.height - 50), cv.FONT_HERSHEY_SIMPLEX, 
                  0.5, (255, 255, 255), 1)
        cv.putText(display_image, f"Max: {max_temp:.2f}°C", 
                  (10, image.height - 25), cv.FONT_HERSHEY_SIMPLEX, 
                  0.5, (255, 255, 255), 1)
        
        # Metadata
        metadata = {
            'width': image.width,
            'height': image.height,
            'encoding': image.encoding,
            'min_temperature': float(min_temp),
            'max_temperature': float(max_temp),
            'gain': thermal_image.gain,
            'offset': thermal_image.offset,
            'raw_min': int(raw_image.min()),
            'raw_max': int(raw_image.max())
        }
        
        return display_image, temperature_image, metadata
    
    @staticmethod
    def save_thermal_data(thermal_image: api.ThermalImage, base_filename: str):
        """Save thermal data in multiple formats"""
        display_img, temp_array, metadata = ThermalImageProcessor.process_mono16_thermal(thermal_image)
        
        # Save display image (colorized)
        cv.imwrite(f"{base_filename}_display.jpg", display_img)
        
        # Save raw temperature data (numpy array)
        np.save(f"{base_filename}_temperatures.npy", temp_array)
        
        # Save raw uint16 data
        raw_buffer = np.frombuffer(thermal_image.image.data, dtype="uint16")
        raw_image = raw_buffer.reshape((thermal_image.image.height, thermal_image.image.width))
        np.save(f"{base_filename}_raw_uint16.npy", raw_image)
        
        # Save metadata
        import json
        with open(f"{base_filename}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'display_image': f"{base_filename}_display.jpg",
            'temperature_data': f"{base_filename}_temperatures.npy", 
            'raw_data': f"{base_filename}_raw_uint16.npy",
            'metadata': f"{base_filename}_metadata.json"
        }

# Usage example
def process_downloaded_thermal_file(thermal_image_data):
    """Process a downloaded thermal image file"""
    processor = ThermalImageProcessor()
    
    # Process the thermal image
    display_img, temp_array, metadata = processor.process_mono16_thermal(thermal_image_data)
    
    # Save in multiple formats
    files = processor.save_thermal_data(thermal_image_data, "thermal_inspection_001")
    
    print(f"Processed thermal image:")
    print(f"  Temperature range: {metadata['min_temperature']:.2f}°C to {metadata['max_temperature']:.2f}°C")
    print(f"  Raw value range: {metadata['raw_min']} to {metadata['raw_max']}")
    print(f"  Conversion: temp = {metadata['gain']} * raw + {metadata['offset']}")
    print(f"  Files saved: {list(files.values())}")
    
    return files
```

## 🔍 Key Technical Details

### Data Format Specifications

1. **mono16 Encoding**:
   - 16-bit unsigned integers (0-65535 range)
   - Single channel (grayscale)
   - Little-endian byte order
   - Raw sensor ADC values

2. **Temperature Conversion**:
   - **Formula**: `temperature_celsius = gain * raw_value + offset`
   - **Gain**: Scaling factor (typically ~0.04)
   - **Offset**: Zero-point offset (typically ~-273.15 for Kelvin to Celsius)

3. **Image Dimensions**:
   - **Width**: Pixels per row
   - **Height**: Number of rows
   - **Step**: Bytes per row (width × 2 for 16-bit data)

### Example Values from ANYmal SDK

```python
# From thermal_image_example
thermal_image.image.width = 336      # pixels
thermal_image.image.height = 256     # pixels  
thermal_image.image.step = 672       # bytes (336 * 2)
thermal_image.image.encoding = "mono16"
thermal_image.gain = 0.04            # scaling factor
thermal_image.offset = -273.15       # Kelvin to Celsius conversion
```

## 🎯 Practical Applications

### 1. Hotspot Detection
```python
def find_hotspots(temperature_image, threshold_temp=50.0):
    """Find areas above temperature threshold"""
    hotspots = temperature_image > threshold_temp
    return np.where(hotspots)
```

### 2. Temperature Statistics
```python
def analyze_temperature_distribution(temperature_image):
    """Analyze temperature distribution in image"""
    return {
        'mean': np.mean(temperature_image),
        'std': np.std(temperature_image),
        'min': np.min(temperature_image),
        'max': np.max(temperature_image),
        'median': np.median(temperature_image)
    }
```

### 3. Export to Standard Formats
```python
def export_thermal_formats(thermal_image, filename_base):
    """Export thermal data to various standard formats"""
    display_img, temp_array, metadata = ThermalImageProcessor.process_mono16_thermal(thermal_image)
    
    # TIFF with temperature data (preserves precision)
    cv.imwrite(f"{filename_base}.tiff", (temp_array * 100).astype(np.uint16))
    
    # CSV with temperature values
    np.savetxt(f"{filename_base}.csv", temp_array, delimiter=',', fmt='%.2f')
    
    # PNG display image
    cv.imwrite(f"{filename_base}.png", display_img)
```

## 🔧 Integration with Download System

You can integrate this thermal processing with the inspection data download system:

```python
from inspection_data_download_samples import ANYmalDataDownloader
import anymal_api_proto as api

def download_and_process_thermal_data(server_url, email, password, thermal_filename):
    """Download and process thermal inspection data"""
    
    # Download the file
    downloader = ANYmalDataDownloader(server_url)
    if downloader.authenticate(email, password):
        file_path = downloader.download_inspection_file(thermal_filename)
        
        if file_path:
            # Load the thermal image data (assuming protobuf format)
            with open(file_path, 'rb') as f:
                thermal_data = api.ThermalImage()
                thermal_data.ParseFromString(f.read())
            
            # Process the thermal data
            processor = ThermalImageProcessor()
            files = processor.save_thermal_data(thermal_data, "processed_thermal")
            
            return files
    
    return None
```

This comprehensive conversion process transforms the raw mono16 thermal sensor data into usable temperature measurements and visualization formats for analysis and reporting.