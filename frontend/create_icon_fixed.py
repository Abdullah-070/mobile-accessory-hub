"""
Convert PNG image to ICO format for application icon - Fixed version
"""
from PIL import Image
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Source image path
source_image = os.path.join(script_dir, "logo-mobile-products-mobile-products_1189726-5309 (1).png")

# Output ICO path  
output_ico = os.path.join(script_dir, "assets", "app_icon.ico")

# Also save to frontend root for backup
output_ico_root = os.path.join(script_dir, "app_icon.ico")

print(f"Loading image from: {source_image}")

# Open the image
img = Image.open(source_image)
print(f"Original size: {img.size}, Mode: {img.mode}")

# Convert to RGBA for transparency support
if img.mode != 'RGBA':
    img = img.convert('RGBA')
    print("Converted to RGBA mode")

# Create icon sizes - Windows uses these specific sizes
icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Create a list of resized images
icon_images = []
for size in icon_sizes:
    resized = img.copy()
    resized.thumbnail(size, Image.Resampling.LANCZOS)
    # Create a new image with exact size and paste the resized one centered
    new_img = Image.new('RGBA', size, (0, 0, 0, 0))
    # Calculate position to center
    x = (size[0] - resized.size[0]) // 2
    y = (size[1] - resized.size[1]) // 2
    new_img.paste(resized, (x, y))
    icon_images.append(new_img)
    print(f"Created {size[0]}x{size[1]} icon")

# Ensure assets directory exists
os.makedirs(os.path.join(script_dir, "assets"), exist_ok=True)

# Save as ICO - use the largest image as base and include all sizes
icon_images[0].save(
    output_ico,
    format='ICO',
    sizes=[(img.size[0], img.size[1]) for img in icon_images],
    append_images=icon_images[1:]
)

# Also copy to root
icon_images[0].save(
    output_ico_root,
    format='ICO', 
    sizes=[(img.size[0], img.size[1]) for img in icon_images],
    append_images=icon_images[1:]
)

print(f"\n✓ Icon created successfully!")
print(f"  Saved to: {output_ico}")
print(f"  Backup at: {output_ico_root}")
print(f"  Sizes: {[f'{s[0]}x{s[1]}' for s in icon_sizes]}")
