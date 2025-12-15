"""
Convert PNG image to ICO format for application icon
"""
from PIL import Image
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Source image path
source_image = os.path.join(script_dir, "logo-mobile-products-mobile-products_1189726-5309 (1).png")

# Output ICO path
output_ico = os.path.join(script_dir, "app_icon.ico")

# Open the image
img = Image.open(source_image)

# Convert to RGBA if needed
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Create multiple sizes for the ICO file (Windows uses different sizes)
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Resize images for each size
icons = []
for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icons.append(resized)

# Save as ICO with multiple sizes
img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
img_256.save(output_ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

print(f"Icon created successfully at: {output_ico}")
print("Icon sizes included: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256")
