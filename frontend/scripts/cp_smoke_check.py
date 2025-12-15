"""
=============================================================================
Copilot Smoke Check Script
=============================================================================
Purpose: Validate category and subcategory repository methods work correctly.
This script tests the newly integrated dialog functionality without UI.

Test Coverage:
- CategoryRepository.get_next_id()
- CategoryRepository.create_category()
- CategoryRepository.get_all_categories()
- SubcategoryRepository.get_next_id()
- SubcategoryRepository.create_subcategory()
- SubcategoryRepository.get_subcategories_for_category()

Usage:
    cd frontend
    python scripts/cp_smoke_check.py

Note: This script creates test data in the database. Run with caution.
=============================================================================
"""

import sys
import os

# Add frontend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_test(test_name, passed, details=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")


def test_category_next_id():
    """Test category ID generation."""
    print_header("TEST: Category ID Generation")
    
    try:
        next_id = CategoryRepository.get_next_id()
        passed = next_id.startswith("CAT") and len(next_id) == 6
        print_test("get_next_id() format", passed, f"Generated: {next_id}")
        return passed
    except Exception as e:
        print_test("get_next_id()", False, f"Error: {str(e)}")
        return False


def test_category_create():
    """Test category creation."""
    print_header("TEST: Category Creation")
    
    try:
        success, message, cat_id = CategoryRepository.create_category(
            "CP_Test_Category", 
            "Test category created by smoke check"
        )
        print_test("create_category()", success, f"{message} | ID: {cat_id}")
        return success, cat_id
    except Exception as e:
        print_test("create_category()", False, f"Error: {str(e)}")
        return False, None


def test_category_get_all():
    """Test category retrieval."""
    print_header("TEST: Category Retrieval")
    
    try:
        categories = CategoryRepository.get_all_categories()
        passed = len(categories) > 0
        print_test("get_all_categories()", passed, f"Found {len(categories)} categories")
        
        # Check for our test category
        test_cat = next((c for c in categories if c.cat_name == "CP_Test_Category"), None)
        if test_cat:
            print(f"       Test category found: {test_cat.cat_id} - {test_cat.cat_name}")
            return True, test_cat.cat_id
        else:
            print("       Warning: Test category not found in results")
            return passed, None
    except Exception as e:
        print_test("get_all_categories()", False, f"Error: {str(e)}")
        return False, None


def test_subcategory_next_id():
    """Test subcategory ID generation."""
    print_header("TEST: Subcategory ID Generation")
    
    try:
        next_id = SubcategoryRepository.get_next_id()
        passed = next_id.startswith("SUB") and len(next_id) == 6
        print_test("get_next_id() format", passed, f"Generated: {next_id}")
        return passed
    except Exception as e:
        print_test("get_next_id()", False, f"Error: {str(e)}")
        return False


def test_subcategory_create(cat_id):
    """Test subcategory creation."""
    print_header("TEST: Subcategory Creation")
    
    if not cat_id:
        print_test("create_subcategory()", False, "No valid category ID provided")
        return False, None
    
    try:
        success, message, subcat_id = SubcategoryRepository.create_subcategory(
            cat_id,
            "CP_Test_Subcategory",
            "Test subcategory created by smoke check"
        )
        print_test("create_subcategory()", success, f"{message} | ID: {subcat_id}")
        return success, subcat_id
    except Exception as e:
        print_test("create_subcategory()", False, f"Error: {str(e)}")
        return False, None


def test_subcategory_get_by_category(cat_id):
    """Test subcategory retrieval by category."""
    print_header("TEST: Subcategory Retrieval")
    
    if not cat_id:
        print_test("get_subcategories_for_category()", False, "No valid category ID provided")
        return False
    
    try:
        subcategories = SubcategoryRepository.get_subcategories_for_category(cat_id)
        passed = len(subcategories) > 0
        print_test("get_subcategories_for_category()", passed, f"Found {len(subcategories)} subcategories")
        
        # Check for our test subcategory
        test_subcat = next((s for s in subcategories if s.subcat_name == "CP_Test_Subcategory"), None)
        if test_subcat:
            print(f"       Test subcategory found: {test_subcat.subcat_id} - {test_subcat.subcat_name}")
        else:
            print("       Warning: Test subcategory not found in results")
        
        return passed
    except Exception as e:
        print_test("get_subcategories_for_category()", False, f"Error: {str(e)}")
        return False


def cleanup_test_data(cat_id, subcat_id):
    """Clean up test data created during smoke checks."""
    print_header("CLEANUP: Removing Test Data")
    
    # Delete subcategory first (foreign key constraint)
    if subcat_id:
        try:
            success, message = SubcategoryRepository.delete(subcat_id)
            print_test(f"Delete subcategory {subcat_id}", success, message)
        except Exception as e:
            print_test(f"Delete subcategory {subcat_id}", False, f"Error: {str(e)}")
    
    # Delete category
    if cat_id:
        try:
            success, message = CategoryRepository.delete(cat_id)
            print_test(f"Delete category {cat_id}", success, message)
        except Exception as e:
            print_test(f"Delete category {cat_id}", False, f"Error: {str(e)}")


def run_smoke_checks():
    """Run all smoke checks."""
    print_header("COPILOT SMOKE CHECK - Category & Subcategory Dialogs")
    print("Testing repository methods used by new dialog views")
    print("Test data will be created and cleaned up automatically")
    
    results = []
    cat_id = None
    subcat_id = None
    
    # Test Category Operations
    results.append(("Category ID Generation", test_category_next_id()))
    
    cat_created, cat_id = test_category_create()
    results.append(("Category Creation", cat_created))
    
    cat_retrieved, cat_id_retrieved = test_category_get_all()
    results.append(("Category Retrieval", cat_retrieved))
    if cat_id is None and cat_id_retrieved:
        cat_id = cat_id_retrieved
    
    # Test Subcategory Operations
    results.append(("Subcategory ID Generation", test_subcategory_next_id()))
    
    subcat_created, subcat_id = test_subcategory_create(cat_id)
    results.append(("Subcategory Creation", subcat_created))
    
    results.append(("Subcategory Retrieval", test_subcategory_get_by_category(cat_id)))
    
    # Cleanup
    cleanup_test_data(cat_id, subcat_id)
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Dialogs are ready for use!")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_smoke_checks()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
