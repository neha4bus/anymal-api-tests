#!/usr/bin/env python3
"""
ANYmal Thermal JSON to Raw Image Converter
Converts JSON thermal measurement files with mono16 data to usable thermal images
"""

import json
import base64
import numpy as np
import cv2 as cv
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThermalJSONConverter:
    """Converter for ANYmal thermal measurement JSON files"""
    
    def __init__(self):
        # Default thermal camera parameters for ANYmal (from SDK examples)
        self.default_width = 336
        self.default_height = 256
        self.default_gain = 0.04
        self.default_offset = -273.15  # Kelvin to Celsius conversion
        
    def load_thermal_json(self, json_file_path: str) -> Dict[str, Any]:
        """Load thermal measurement JSON file"""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded thermal JSON: {json_file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON file: {e}")
            raise
    
    def decode_mono16_data(self, encoded_data: str, width: int = None, height: int = None) -> np.ndarray:
        """
        Decode base64 encoded mono16 thermal data
        
        Args:
            encoded_data: Base64 encoded thermal data string
            width: Image width (defaults to ANYmal thermal camera width)
            height: Image height (defaults to ANYmal thermal camera height)
            
        Returns:
            numpy array with raw uint16 thermal values
        """
        if width is None:
            width = self.default_width
        if height is None:
            height = self.default_height
            
        try:
            # Decode base64 data
            binary_data = base64.b64decode(encoded_data)
            logger.info(f"Decoded {len(binary_data)} bytes of thermal data")
            
            # Convert to uint16 array (mono16 format)
            raw_buffer = np.frombuffer(binary_data, dtype=np.uint16)
            
            # Calculate expected size
            expected_size = width * height
            actual_size = len(raw_buffer)
            
            logger.info(f"Expected {expected_size} pixels, got {actual_size} values")
            
            # Handle size mismatch
            if actual_size < expected_size:
                logger.warning(f"Data size mismatch. Padding with zeros.")
                padded_buffer = np.zeros(expected_size, dtype=np.uint16)
                padded_buffer[:actual_size] = raw_buffer
                raw_buffer = padded_buffer
            elif actual_size > expected_size:
                logger.warning(f"Data size larger than expected. Truncating.")
                raw_buffer = raw_buffer[:expected_size]
            
            # Reshape to image dimensions
            raw_image = raw_buffer.reshape((height, width))
            
            logger.info(f"Raw thermal image shape: {raw_image.shape}")
            logger.info(f"Raw value range: {raw_image.min()} - {raw_image.max()}")
            
            return raw_image
            
        except Exception as e:
            logger.error(f"Failed to decode mono16 data: {e}")
            raise
    
    def convert_to_temperature(self, raw_image: np.ndarray, gain: float = None, offset: float = None) -> np.ndarray:
        """
        Convert raw uint16 values to temperature using ANYmal calibration formula
        
        Args:
            raw_image: Raw uint16 thermal image
            gain: Calibration gain (defaults to ANYmal standard)
            offset: Calibration offset (defaults to ANYmal standard)
            
        Returns:
            Temperature image in Celsius
        """
        if gain is None:
            gain = self.default_gain
        if offset is None:
            offset = self.default_offset
            
        # Apply ANYmal temperature conversion formula: temp = gain * raw + offset
        temperature_image = raw_image.astype(np.float32) * gain + offset
        
        logger.info(f"Temperature conversion: gain={gain}, offset={offset}")
        logger.info(f"Temperature range: {temperature_image.min():.2f}°C - {temperature_image.max():.2f}°C")
        
        return temperature_image
    
    def create_thermal_visualization(self, temperature_image: np.ndarray) -> np.ndarray:
        """
        Create colorized thermal visualization using ANYmal approach
        
        Args:
            temperature_image: Temperature array in Celsius
            
        Returns:
            BGR color image for display/saving
        """
        # Normalize temperature data to 0-255 range
        normalized = cv.normalize(
            temperature_image,
            None,
            alpha=0,
            beta=255,
            norm_type=cv.NORM_MINMAX,
            dtype=cv.CV_8U
        )
        
        # Apply JET colormap (standard for thermal imaging)
        colored_image = cv.applyColorMap(normalized, cv.COLORMAP_JET)
        
        # Add temperature annotations (ANYmal style)
        min_temp = temperature_image.min()
        max_temp = temperature_image.max()
        height = temperature_image.shape[0]
        
        # Add min temperature text
        cv.putText(
            colored_image,
            f"Min: {min_temp:.2f}°C",
            (10, height - 50),
            cv.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv.LINE_AA
        )
        
        # Add max temperature text
        cv.putText(
            colored_image,
            f"Max: {max_temp:.2f}°C",
            (10, height - 25),
            cv.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv.LINE_AA
        )
        
        logger.info("Created thermal visualization with temperature annotations")
        return colored_image
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """Extract metadata from ANYmal thermal measurement filename"""
        # Parse filename: 0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement.json
        parts = Path(filename).stem.split('_')
        
        metadata = {
            'measurement_id': parts[0] if len(parts) > 0 else 'unknown',
            'unit': parts[1] + '_' + parts[2] if len(parts) > 2 else 'unknown',
            'sensor_type': parts[3] if len(parts) > 3 else 'THERMAL',
            'sensor_id': parts[4] if len(parts) > 4 else 'unknown',
            'measurement_type': parts[5] if len(parts) > 5 else 'measurement'
        }
        
        return metadata
    
    def process_thermal_json(self, json_file_path: str, output_dir: str = "./thermal_output") -> Dict[str, str]:
        """
        Complete processing pipeline for thermal JSON files
        
        Args:
            json_file_path: Path to thermal measurement JSON file
            output_dir: Directory to save processed files
            
        Returns:
            Dictionary with paths to generated files
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Extract base filename for outputs
        base_filename = Path(json_file_path).stem
        
        logger.info(f"Processing thermal JSON: {json_file_path}")
        
        # Load JSON data
        json_data = self.load_thermal_json(json_file_path)
        
        # Extract metadata from filename
        metadata = self.extract_metadata_from_filename(json_file_path)
        
        # Get thermal data from JSON
        if 'data' not in json_data:
            raise ValueError("No 'data' field found in JSON file")
        
        encoded_data = json_data['data']
        
        # Try to get dimensions from JSON, fallback to defaults
        width = json_data.get('width', self.default_width)
        height = json_data.get('height', self.default_height)
        gain = json_data.get('gain', self.default_gain)
        offset = json_data.get('offset', self.default_offset)
        
        # Decode mono16 data
        raw_image = self.decode_mono16_data(encoded_data, width, height)
        
        # Convert to temperature
        temperature_image = self.convert_to_temperature(raw_image, gain, offset)
        
        # Create visualization
        thermal_display = self.create_thermal_visualization(temperature_image)
        
        # Save files
        output_files = {}
        
        # 1. Save raw uint16 data
        raw_file = os.path.join(output_dir, f"{base_filename}_raw_uint16.npy")
        np.save(raw_file, raw_image)
        output_files['raw_data'] = raw_file
        
        # 2. Save temperature data
        temp_file = os.path.join(output_dir, f"{base_filename}_temperatures.npy")
        np.save(temp_file, temperature_image)
        output_files['temperature_data'] = temp_file
        
        # 3. Save thermal visualization
        display_file = os.path.join(output_dir, f"{base_filename}_thermal_display.jpg")
        cv.imwrite(display_file, thermal_display)
        output_files['display_image'] = display_file
        
        # 4. Save grayscale thermal image
        grayscale_file = os.path.join(output_dir, f"{base_filename}_thermal_grayscale.png")
        normalized_temp = cv.normalize(temperature_image, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)
        cv.imwrite(grayscale_file, normalized_temp)
        output_files['grayscale_image'] = grayscale_file
        
        # 5. Save metadata
        metadata_file = os.path.join(output_dir, f"{base_filename}_metadata.json")
        full_metadata = {
            **metadata,
            'processing_info': {
                'width': int(width),
                'height': int(height),
                'gain': float(gain),
                'offset': float(offset),
                'min_temperature': float(temperature_image.min()),
                'max_temperature': float(temperature_image.max()),
                'raw_min': int(raw_image.min()),
                'raw_max': int(raw_image.max()),
                'conversion_formula': f'temperature = {gain} * raw_value + {offset}'
            },
            'original_json': json_data
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(full_metadata, f, indent=2)
        output_files['metadata'] = metadata_file
        
        # 6. Save CSV temperature data
        csv_file = os.path.join(output_dir, f"{base_filename}_temperatures.csv")
        np.savetxt(csv_file, temperature_image, delimiter=',', fmt='%.2f')
        output_files['temperature_csv'] = csv_file
        
        logger.info(f"Processing complete! Generated {len(output_files)} files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type}: {file_path}")
        
        return output_files
    
    def analyze_thermal_data(self, temperature_image: np.ndarray, threshold_temp: float = 50.0) -> Dict[str, Any]:
        """Analyze thermal data for hotspots and statistics"""
        
        analysis = {
            'statistics': {
                'mean_temp': float(np.mean(temperature_image)),
                'std_temp': float(np.std(temperature_image)),
                'min_temp': float(np.min(temperature_image)),
                'max_temp': float(np.max(temperature_image)),
                'median_temp': float(np.median(temperature_image))
            },
            'hotspots': {
                'threshold': threshold_temp,
                'count': int(np.sum(temperature_image > threshold_temp)),
                'percentage': float(np.sum(temperature_image > threshold_temp) / temperature_image.size * 100),
                'locations': np.where(temperature_image > threshold_temp)
            }
        }
        
        return analysis


def main():
    """Example usage of the thermal JSON converter"""
    
    # Initialize converter
    converter = ThermalJSONConverter()
    
    # Process the thermal measurement file
    json_file = "inspection_data/0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement.json"
    
    if not os.path.exists(json_file):
        logger.error(f"File not found: {json_file}")
        return
    
    try:
        # Process the thermal JSON
        output_files = converter.process_thermal_json(json_file, "./thermal_converted")
        
        # Load temperature data for analysis
        temp_data = np.load(output_files['temperature_data'])
        
        # Analyze thermal data
        analysis = converter.analyze_thermal_data(temp_data, threshold_temp=30.0)
        
        print("\n" + "="*60)
        print("🔥 THERMAL ANALYSIS RESULTS")
        print("="*60)
        
        stats = analysis['statistics']
        print(f"📊 Temperature Statistics:")
        print(f"   Mean: {stats['mean_temp']:.2f}°C")
        print(f"   Min:  {stats['min_temp']:.2f}°C")
        print(f"   Max:  {stats['max_temp']:.2f}°C")
        print(f"   Std:  {stats['std_temp']:.2f}°C")
        
        hotspots = analysis['hotspots']
        print(f"\n🔥 Hotspot Analysis (>{hotspots['threshold']}°C):")
        print(f"   Count: {hotspots['count']} pixels")
        print(f"   Coverage: {hotspots['percentage']:.2f}% of image")
        
        print(f"\n📁 Generated Files:")
        for file_type, file_path in output_files.items():
            print(f"   {file_type}: {file_path}")
        
        print(f"\n✅ Conversion complete! Check './thermal_converted' directory")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()