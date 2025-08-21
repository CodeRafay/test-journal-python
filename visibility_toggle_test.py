#!/usr/bin/env python3
"""
Focused test for journal entry visibility toggle functionality
Tests the PUT /api/entries/{id} endpoint specifically for isShared status changes
"""

import requests
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://vercel-backend-flow.preview.emergentagent.com/api"
ADMIN_PASSWORD = "12345678"

class VisibilityToggleTester:
    def __init__(self):
        self.admin_session = requests.Session()
        self.test_results = []
        self.test_entry_id = None
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        self.test_results.append(result)
        print(result)
        
    def setup_admin_session(self):
        """Login as admin to get authenticated session"""
        try:
            payload = {"password": ADMIN_PASSWORD}
            response = self.admin_session.post(f"{BASE_URL}/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("role") == "admin"
                self.log_test("Admin Login Setup", success, f"Role: {data.get('role')}")
                return success
            else:
                self.log_test("Admin Login Setup", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Login Setup", False, f"Error: {str(e)}")
            return False
    
    def create_test_entry(self):
        """Create a test entry for visibility toggle testing"""
        try:
            entry_data = {
                "title": "Visibility Toggle Test Entry",
                "content": "This entry is created specifically to test the visibility toggle functionality. It will be toggled between shared and private states.",
                "category": "Testing",
                "tags": ["test", "visibility", "toggle"],
                "isShared": False  # Start as private
            }
            
            response = self.admin_session.post(f"{BASE_URL}/entries", json=entry_data)
            
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get("id")
                if entry_id:
                    self.test_entry_id = entry_id
                    self.log_test("Create Test Entry", True, f"Entry ID: {entry_id}, Initial isShared: {data.get('isShared')}")
                    return True
                else:
                    self.log_test("Create Test Entry", False, "No entry ID returned")
                    return False
            else:
                self.log_test("Create Test Entry", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test Entry", False, f"Error: {str(e)}")
            return False
    
    def test_toggle_private_to_shared(self):
        """Test toggling entry from private to shared"""
        if not self.test_entry_id:
            self.log_test("Toggle Private to Shared", False, "No test entry available")
            return False
            
        try:
            # Update entry to shared
            update_data = {"isShared": True}
            response = self.admin_session.put(f"{BASE_URL}/entries/{self.test_entry_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("isShared") == True
                self.log_test("Toggle Private to Shared", success, 
                            f"Entry {self.test_entry_id} isShared: {data.get('isShared')}")
                return success
            else:
                self.log_test("Toggle Private to Shared", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Toggle Private to Shared", False, f"Error: {str(e)}")
            return False
    
    def test_toggle_shared_to_private(self):
        """Test toggling entry from shared back to private"""
        if not self.test_entry_id:
            self.log_test("Toggle Shared to Private", False, "No test entry available")
            return False
            
        try:
            # Update entry back to private
            update_data = {"isShared": False}
            response = self.admin_session.put(f"{BASE_URL}/entries/{self.test_entry_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("isShared") == False
                self.log_test("Toggle Shared to Private", success, 
                            f"Entry {self.test_entry_id} isShared: {data.get('isShared')}")
                return success
            else:
                self.log_test("Toggle Shared to Private", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Toggle Shared to Private", False, f"Error: {str(e)}")
            return False
    
    def test_invalid_entry_id_undefined(self):
        """Test visibility toggle with 'undefined' entry ID (should return 404)"""
        try:
            update_data = {"isShared": True}
            response = self.admin_session.put(f"{BASE_URL}/entries/undefined", json=update_data)
            
            success = response.status_code == 404
            self.log_test("Invalid Entry ID 'undefined'", success, 
                        f"Status: {response.status_code}, Expected: 404")
            return success
        except Exception as e:
            self.log_test("Invalid Entry ID 'undefined'", False, f"Error: {str(e)}")
            return False
    
    def test_invalid_entry_id_nonexistent(self):
        """Test visibility toggle with non-existent UUID (should return 404)"""
        try:
            fake_uuid = str(uuid.uuid4())
            update_data = {"isShared": True}
            response = self.admin_session.put(f"{BASE_URL}/entries/{fake_uuid}", json=update_data)
            
            success = response.status_code == 404
            self.log_test("Invalid Entry ID (Non-existent UUID)", success, 
                        f"Status: {response.status_code}, Expected: 404, UUID: {fake_uuid}")
            return success
        except Exception as e:
            self.log_test("Invalid Entry ID (Non-existent UUID)", False, f"Error: {str(e)}")
            return False
    
    def test_invalid_entry_id_malformed(self):
        """Test visibility toggle with malformed entry ID (should return 404 or 400)"""
        try:
            malformed_id = "not-a-valid-uuid"
            update_data = {"isShared": True}
            response = self.admin_session.put(f"{BASE_URL}/entries/{malformed_id}", json=update_data)
            
            success = response.status_code in [400, 404]  # Either is acceptable
            self.log_test("Invalid Entry ID (Malformed)", success, 
                        f"Status: {response.status_code}, Expected: 400 or 404, ID: {malformed_id}")
            return success
        except Exception as e:
            self.log_test("Invalid Entry ID (Malformed)", False, f"Error: {str(e)}")
            return False
    
    def test_partial_update_with_other_fields(self):
        """Test that visibility toggle works alongside other field updates"""
        if not self.test_entry_id:
            self.log_test("Partial Update with Visibility", False, "No test entry available")
            return False
            
        try:
            # Update multiple fields including isShared
            update_data = {
                "title": "Updated Title for Visibility Test",
                "isShared": True,
                "tags": ["updated", "visibility", "test"]
            }
            response = self.admin_session.put(f"{BASE_URL}/entries/{self.test_entry_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                success = (data.get("isShared") == True and 
                          data.get("title") == update_data["title"] and
                          "updated" in data.get("tags", []))
                self.log_test("Partial Update with Visibility", success, 
                            f"isShared: {data.get('isShared')}, title: {data.get('title')}")
                return success
            else:
                self.log_test("Partial Update with Visibility", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Partial Update with Visibility", False, f"Error: {str(e)}")
            return False
    
    def verify_entry_state(self, expected_shared: bool):
        """Verify the current state of the test entry"""
        if not self.test_entry_id:
            return False
            
        try:
            # Get entries to verify current state
            response = self.admin_session.get(f"{BASE_URL}/entries?grouped=false")
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                
                # Find our test entry
                test_entry = next((entry for entry in entries if entry.get("id") == self.test_entry_id), None)
                
                if test_entry:
                    actual_shared = test_entry.get("isShared")
                    success = actual_shared == expected_shared
                    self.log_test(f"Verify Entry State (Expected: {expected_shared})", success, 
                                f"Actual isShared: {actual_shared}")
                    return success
                else:
                    self.log_test("Verify Entry State", False, "Test entry not found in entries list")
                    return False
            else:
                self.log_test("Verify Entry State", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verify Entry State", False, f"Error: {str(e)}")
            return False
    
    def cleanup_test_entry(self):
        """Clean up the test entry"""
        if self.test_entry_id:
            try:
                response = self.admin_session.delete(f"{BASE_URL}/entries/{self.test_entry_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up test entry: {self.test_entry_id}")
                else:
                    print(f"⚠️ Could not clean up entry {self.test_entry_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning up entry {self.test_entry_id}: {str(e)}")
    
    def run_visibility_toggle_tests(self):
        """Run all visibility toggle tests"""
        print("🔄 Starting Journal Entry Visibility Toggle Tests")
        print(f"📍 Testing against: {BASE_URL}")
        print("=" * 70)
        
        # Setup
        if not self.setup_admin_session():
            print("❌ Failed to setup admin session. Aborting tests.")
            return False
        
        if not self.create_test_entry():
            print("❌ Failed to create test entry. Aborting tests.")
            return False
        
        # Core visibility toggle tests
        print("\n🔄 Visibility Toggle Tests")
        self.verify_entry_state(False)  # Should start as private
        self.test_toggle_private_to_shared()
        self.verify_entry_state(True)   # Should now be shared
        self.test_toggle_shared_to_private()
        self.verify_entry_state(False)  # Should be private again
        
        # Invalid ID tests
        print("\n❌ Invalid Entry ID Tests")
        self.test_invalid_entry_id_undefined()
        self.test_invalid_entry_id_nonexistent()
        self.test_invalid_entry_id_malformed()
        
        # Advanced tests
        print("\n🔧 Advanced Toggle Tests")
        self.test_partial_update_with_other_fields()
        
        # Cleanup
        print("\n🧹 Cleanup")
        self.cleanup_test_entry()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 VISIBILITY TOGGLE TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result)
        failed_tests = sum(1 for result in self.test_results if "❌ FAIL" in result)
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = VisibilityToggleTester()
    success = tester.run_visibility_toggle_tests()
    
    if success:
        print("\n🎉 All visibility toggle tests passed!")
        exit(0)
    else:
        print("\n💥 Some visibility toggle tests failed!")
        exit(1)