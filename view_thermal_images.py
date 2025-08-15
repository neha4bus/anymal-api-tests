#!/usr/bin/env python3
"""
Thermal Image Viewer
Opens and displays the converted thermal/infrared images
"""

import cv2
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def view_thermal_images():
    """Display the thermal images with analysis"""
    
    # File paths
    thermal_dir = "thermal_converted"
    base_name = "0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement"
    
    display_image_path = f"{thermal_dir}/{base_name}_thermal_display.jpg"
    grayscale_image_path = f"{thermal_dir}/{base_name}_thermal_grayscale.png"
    temp_data_path = f"{thermal_dir}/{base_name}_temperatures.npy"
    
    # Check if files exist
    if not all(os.path.exists(path) for path in [display_image_path, grayscale_image_path, temp_data_path]):
        print("❌ Thermal image files not found. Please run the converter first.")
        return
    
    # Load images and temperature data
    display_image = cv2.imread(display_image_path)
    grayscale_image = cv2.imread(grayscale_image_path, cv2.IMREAD_GRAYSCALE)
    temp_data = np.load(temp_data_path)
    
    # Convert BGR to RGB for matplotlib
    display_image_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('ANYmal Thermal/Infrared Image Analysis', fontsize=16, fontweight='bold')
    
    # 1. Colorized thermal image (top-left)
    axes[0, 0].imshow(display_image_rgb)
    axes[0, 0].set_title('Thermal Display (JET Colormap)', fontweight='bold')
    axes[0, 0].set_xlabel('Pixel X')
    axes[0, 0].set_ylabel('Pixel Y')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Grayscale thermal image (top-right)
    im2 = axes[0, 1].imshow(grayscale_image, cmap='gray')
    axes[0, 1].set_title('Thermal Grayscale', fontweight='bold')
    axes[0, 1].set_xlabel('Pixel X')
    axes[0, 1].set_ylabel('Pixel Y')
    plt.colorbar(im2, ax=axes[0, 1], label='Intensity')
    
    # 3. Temperature heatmap (bottom-left)
    im3 = axes[1, 0].imshow(temp_data, cmap='hot', interpolation='nearest')
    axes[1, 0].set_title('Temperature Heatmap (°C)', fontweight='bold')
    axes[1, 0].set_xlabel('Pixel X')
    axes[1, 0].set_ylabel('Pixel Y')
    cbar3 = plt.colorbar(im3, ax=axes[1, 0], label='Temperature (°C)')
    
    # Add temperature contours
    contours = axes[1, 0].contour(temp_data, levels=10, colors='white', alpha=0.5, linewidths=0.5)
    axes[1, 0].clabel(contours, inline=True, fontsize=8, fmt='%.1f°C')
    
    # 4. Temperature histogram (bottom-right)
    axes[1, 1].hist(temp_data.flatten(), bins=50, color='red', alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Temperature Distribution', fontweight='bold')
    axes[1, 1].set_xlabel('Temperature (°C)')
    axes[1, 1].set_ylabel('Pixel Count')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add statistics to histogram
    mean_temp = np.mean(temp_data)
    min_temp = np.min(temp_data)
    max_temp = np.max(temp_data)
    
    axes[1, 1].axvline(mean_temp, color='blue', linestyle='--', linewidth=2, label=f'Mean: {mean_temp:.2f}°C')
    axes[1, 1].axvline(min_temp, color='green', linestyle='--', linewidth=2, label=f'Min: {min_temp:.2f}°C')
    axes[1, 1].axvline(max_temp, color='red', linestyle='--', linewidth=2, label=f'Max: {max_temp:.2f}°C')
    axes[1, 1].legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the analysis plot
    analysis_path = f"{thermal_dir}/thermal_analysis_plot.png"
    plt.savefig(analysis_path, dpi=300, bbox_inches='tight')
    print(f"📊 Thermal analysis plot saved: {analysis_path}")
    
    # Show the plot
    plt.show()
    
    # Print analysis summary
    print("\n" + "="*60)
    print("🔥 THERMAL IMAGE ANALYSIS SUMMARY")
    print("="*60)
    print(f"📏 Image Dimensions: {temp_data.shape[1]} × {temp_data.shape[0]} pixels")
    print(f"🌡️  Temperature Range: {min_temp:.2f}°C to {max_temp:.2f}°C")
    print(f"📊 Mean Temperature: {mean_temp:.2f}°C")
    print(f"📈 Standard Deviation: {np.std(temp_data):.2f}°C")
    
    # Hotspot analysis
    threshold_temp = 30.0
    hotspots = temp_data > threshold_temp
    hotspot_count = np.sum(hotspots)
    hotspot_percentage = (hotspot_count / temp_data.size) * 100
    
    print(f"🔥 Hotspots (>{threshold_temp}°C): {hotspot_count} pixels ({hotspot_percentage:.2f}%)")
    
    if hotspot_count > 0:
        hotspot_locations = np.where(hotspots)
        max_hotspot_temp = np.max(temp_data[hotspots])
        print(f"🌡️  Hottest Point: {max_hotspot_temp:.2f}°C")
        print(f"📍 Hotspot Locations: {len(hotspot_locations[0])} areas detected")
    
    print(f"\n📁 Generated Files:")
    print(f"   🖼️  Colorized: {display_image_path}")
    print(f"   ⚫ Grayscale: {grayscale_image_path}")
    print(f"   📊 Analysis: {analysis_path}")


def open_images_with_system_viewer():
    """Open thermal images with system default image viewer"""
    
    thermal_dir = "thermal_converted"
    base_name = "0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement"
    
    display_image_path = f"{thermal_dir}/{base_name}_thermal_display.jpg"
    grayscale_image_path = f"{thermal_dir}/{base_name}_thermal_grayscale.png"
    
    print("🖼️  Opening thermal images with system viewer...")
    
    try:
        # Try to open with system default viewer
        import subprocess
        import sys
        
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.run(['open', display_image_path])
            subprocess.run(['open', grayscale_image_path])
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.run(['xdg-open', display_image_path])
            subprocess.run(['xdg-open', grayscale_image_path])
        elif sys.platform.startswith('win'):  # Windows
            subprocess.run(['start', display_image_path], shell=True)
            subprocess.run(['start', grayscale_image_path], shell=True)
        
        print(f"✅ Opened thermal images:")
        print(f"   🔥 Colorized: {display_image_path}")
        print(f"   ⚫ Grayscale: {grayscale_image_path}")
        
    except Exception as e:
        print(f"❌ Could not open images automatically: {e}")
        print(f"📁 Please manually open these files:")
        print(f"   {os.path.abspath(display_image_path)}")
        print(f"   {os.path.abspath(grayscale_image_path)}")


def create_thermal_summary():
    """Create a text-based thermal image summary"""
    
    thermal_dir = "thermal_converted"
    base_name = "0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement"
    temp_data_path = f"{thermal_dir}/{base_name}_temperatures.npy"
    
    if not os.path.exists(temp_data_path):
        print("❌ Temperature data not found")
        return
    
    temp_data = np.load(temp_data_path)
    
    print("\n" + "🔥" * 20 + " THERMAL IMAGE SUMMARY " + "🔥" * 20)
    print(f"📏 Dimensions: {temp_data.shape[1]} × {temp_data.shape[0]} pixels")
    print(f"🌡️  Temperature Range: {np.min(temp_data):.2f}°C to {np.max(temp_data):.2f}°C")
    print(f"📊 Statistics:")
    print(f"   Mean: {np.mean(temp_data):.2f}°C")
    print(f"   Median: {np.median(temp_data):.2f}°C")
    print(f"   Std Dev: {np.std(temp_data):.2f}°C")
    
    # Create ASCII thermal map (simplified)
    print(f"\n🗺️  ASCII Thermal Map (simplified 20×10):")
    
    # Downsample for ASCII display
    h, w = temp_data.shape
    step_h, step_w = h // 10, w // 20
    
    for i in range(0, h, step_h):
        row = ""
        for j in range(0, w, step_w):
            if i + step_h <= h and j + step_w <= w:
                avg_temp = np.mean(temp_data[i:i+step_h, j:j+step_w])
                if avg_temp > 30:
                    row += "🔥"
                elif avg_temp > 27:
                    row += "🟠"
                elif avg_temp > 24:
                    row += "🟡"
                elif avg_temp > 22:
                    row += "🟢"
                else:
                    row += "🔵"
            else:
                row += "⚫"
        print(f"   {row}")
    
    print(f"\n🔥 Legend: 🔥>30°C 🟠27-30°C 🟡24-27°C 🟢22-24°C 🔵<22°C")


if __name__ == "__main__":
    print("🔥 ANYmal Thermal Image Viewer")
    print("=" * 50)
    
    # Check if matplotlib is available for advanced viewing
    try:
        import matplotlib.pyplot as plt
        print("📊 Creating detailed thermal analysis...")
        view_thermal_images()
    except ImportError:
        print("⚠️  Matplotlib not available. Using basic viewer...")
        create_thermal_summary()
        open_images_with_system_viewer()
    
    # Always show text summary
    create_thermal_summary()