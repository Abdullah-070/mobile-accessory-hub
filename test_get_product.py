"""Test exactly what the application is doing"""
import sys
sys.path.insert(0, 'frontend')

from repositories.product_repository import ProductRepository

# Test getting a product by ID
product_code = 'PRD001'
print(f"Attempting to get product: {product_code}")
print(f"Type: {type(product_code)}")
print("-" * 70)

try:
    product = ProductRepository.get_by_id(product_code)
    if product:
        print("SUCCESS!")
        print(f"Product Code: {product.product_code}")
        print(f"Product Name: {product.product_name}")
        print(f"Subcat ID: {product.subcat_id}")
        print(f"Brand: {product.brand}")
    else:
        print("Product not found")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
