#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Journal Application
Tests authentication, CRUD operations, access control, and data validation
"""

import requests
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://secret-diary-1.preview.emergentagent.com/api"
ADMIN_PASSWORD = "12345678"
VIEWER_PASSWORD = "87654321"
INVALID_PASSWORD = "wrongpassword"

class JournalAPITester:
    def __init__(self):
        self.admin_session = requests.Session()
        self.viewer_session = requests.Session()
        self.unauthenticated_session = requests.Session()
        self.test_results = []
        self.created_entries = []  # Track created entries for cleanup
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        self.test_results.append(result)
        print(result)
        
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", 
                            data.get("message") == "Journal API is running",
                            f"Response: {data}")
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    def test_admin_login(self):
        """Test admin login with correct password"""
        try:
            payload = {"password": ADMIN_PASSWORD}
            response = self.admin_session.post(f"{BASE_URL}/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                success = (data.get("role") == "admin" and 
                          "Successfully logged in as admin" in data.get("message", ""))
                self.log_test("Admin Login", success, f"Response: {data}")
                
                # Check if session cookie is set
                cookies = self.admin_session.cookies
                has_session_cookie = any(cookie.name == "session" for cookie in cookies)
                self.log_test("Admin Session Cookie Set", has_session_cookie, 
                            f"Cookies: {dict(cookies)}")
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
    
    def test_viewer_login(self):
        """Test viewer login with correct password"""
        try:
            payload = {"password": VIEWER_PASSWORD}
            response = self.viewer_session.post(f"{BASE_URL}/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                success = (data.get("role") == "viewer" and 
                          "Successfully logged in as viewer" in data.get("message", ""))
                self.log_test("Viewer Login", success, f"Response: {data}")
                
                # Check if session cookie is set
                cookies = self.viewer_session.cookies
                has_session_cookie = any(cookie.name == "session" for cookie in cookies)
                self.log_test("Viewer Session Cookie Set", has_session_cookie, 
                            f"Cookies: {dict(cookies)}")
            else:
                self.log_test("Viewer Login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Viewer Login", False, f"Error: {str(e)}")
    
    def test_invalid_login(self):
        """Test login with invalid password"""
        try:
            payload = {"password": INVALID_PASSWORD}
            response = requests.post(f"{BASE_URL}/login", json=payload)
            
            success = response.status_code == 401
            self.log_test("Invalid Login Rejection", success, 
                        f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Error: {str(e)}")
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        endpoints_to_test = [
            ("/entries", "GET"),
            ("/entries", "POST"),
            ("/categories", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.unauthenticated_session.get(f"{BASE_URL}{endpoint}")
                elif method == "POST":
                    response = self.unauthenticated_session.post(f"{BASE_URL}{endpoint}", 
                                                               json={"title": "test"})
                
                success = response.status_code == 401
                self.log_test(f"Unauthenticated {method} {endpoint} Rejected", success,
                            f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Unauthenticated {method} {endpoint} Rejected", False, f"Error: {str(e)}")
    
    def test_create_entry_admin(self):
        """Test creating journal entries as admin"""
        test_entries = [
            {
                "title": "My First Journal Entry",
                "content": "This is a test entry for the journal application. It contains some meaningful content to test the system.",
                "category": "Personal",
                "tags": ["test", "journal", "first"],
                "isShared": False
            },
            {
                "title": "Shared Public Entry",
                "content": "This entry is shared with viewers. It demonstrates the sharing functionality.",
                "category": "Public",
                "tags": ["shared", "public"],
                "isShared": True
            },
            {
                "title": "Work Notes",
                "content": "Important work-related notes and observations from today's meetings.",
                "category": "Work",
                "tags": ["work", "meetings", "notes"],
                "isShared": False
            }
        ]
        
        for i, entry_data in enumerate(test_entries):
            try:
                response = self.admin_session.post(f"{BASE_URL}/entries", json=entry_data)
                
                if response.status_code == 200:
                    data = response.json()
                    success = (data.get("title") == entry_data["title"] and
                              data.get("content") == entry_data["content"] and
                              data.get("category") == entry_data["category"] and
                              ("_id" in data or "id" in data))
                    
                    entry_id = data.get("_id") or data.get("id")
                    if success and entry_id:
                        self.created_entries.append(entry_id)
                    
                    self.log_test(f"Create Entry {i+1} (Admin)", success, 
                                f"Entry ID: {entry_id or 'N/A'}")
                else:
                    self.log_test(f"Create Entry {i+1} (Admin)", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test(f"Create Entry {i+1} (Admin)", False, f"Error: {str(e)}")
    
    def test_create_entry_viewer_denied(self):
        """Test that viewers cannot create entries"""
        try:
            entry_data = {
                "title": "Viewer Attempt",
                "content": "This should fail",
                "category": "Test",
                "tags": [],
                "isShared": False
            }
            
            response = self.viewer_session.post(f"{BASE_URL}/entries", json=entry_data)
            success = response.status_code == 403
            self.log_test("Create Entry Denied (Viewer)", success,
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Entry Denied (Viewer)", False, f"Error: {str(e)}")
    
    def test_get_entries_admin(self):
        """Test getting entries as admin"""
        try:
            # Test basic get entries
            response = self.admin_session.get(f"{BASE_URL}/entries")
            
            if response.status_code == 200:
                data = response.json()
                success = "grouped" in data and isinstance(data["grouped"], dict)
                self.log_test("Get Entries Grouped (Admin)", success,
                            f"Categories found: {list(data.get('grouped', {}).keys())}")
                
                # Test ungrouped entries
                response = self.admin_session.get(f"{BASE_URL}/entries?grouped=false")
                if response.status_code == 200:
                    data = response.json()
                    success = "entries" in data and isinstance(data["entries"], list)
                    self.log_test("Get Entries List (Admin)", success,
                                f"Found {len(data.get('entries', []))} entries")
                else:
                    self.log_test("Get Entries List (Admin)", False, f"Status: {response.status_code}")
            else:
                self.log_test("Get Entries Grouped (Admin)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Entries (Admin)", False, f"Error: {str(e)}")
    
    def test_get_entries_viewer(self):
        """Test getting entries as viewer (should only see shared entries)"""
        try:
            response = self.viewer_session.get(f"{BASE_URL}/entries?grouped=false")
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                
                # Check that all returned entries are shared
                all_shared = all(entry.get("isShared", False) for entry in entries)
                self.log_test("Get Entries (Viewer - Only Shared)", all_shared,
                            f"Found {len(entries)} entries, all shared: {all_shared}")
            else:
                self.log_test("Get Entries (Viewer)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Entries (Viewer)", False, f"Error: {str(e)}")
    
    def test_search_entries(self):
        """Test search functionality"""
        search_terms = ["journal", "work", "test"]
        
        for term in search_terms:
            try:
                response = self.admin_session.get(f"{BASE_URL}/entries?search={term}&grouped=false")
                
                if response.status_code == 200:
                    data = response.json()
                    entries = data.get("entries", [])
                    
                    # Check if search term appears in results
                    found_matches = any(
                        term.lower() in entry.get("title", "").lower() or
                        term.lower() in entry.get("content", "").lower() or
                        any(term.lower() in tag.lower() for tag in entry.get("tags", []))
                        for entry in entries
                    )
                    
                    self.log_test(f"Search Entries '{term}'", 
                                len(entries) == 0 or found_matches,
                                f"Found {len(entries)} entries")
                else:
                    self.log_test(f"Search Entries '{term}'", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Search Entries '{term}'", False, f"Error: {str(e)}")
    
    def test_category_filter(self):
        """Test category filtering"""
        try:
            response = self.admin_session.get(f"{BASE_URL}/entries?category=Personal&grouped=false")
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                
                # Check that all entries belong to the specified category
                correct_category = all(entry.get("category") == "Personal" for entry in entries)
                self.log_test("Category Filter", 
                            len(entries) == 0 or correct_category,
                            f"Found {len(entries)} entries in 'Personal' category")
            else:
                self.log_test("Category Filter", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Category Filter", False, f"Error: {str(e)}")
    
    def test_get_categories(self):
        """Test getting categories"""
        try:
            # Test as admin
            response = self.admin_session.get(f"{BASE_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                success = "categories" in data and isinstance(data["categories"], list)
                self.log_test("Get Categories (Admin)", success,
                            f"Categories: {data.get('categories', [])}")
            else:
                self.log_test("Get Categories (Admin)", False, f"Status: {response.status_code}")
            
            # Test as viewer
            response = self.viewer_session.get(f"{BASE_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                success = "categories" in data and isinstance(data["categories"], list)
                self.log_test("Get Categories (Viewer)", success,
                            f"Categories: {data.get('categories', [])}")
            else:
                self.log_test("Get Categories (Viewer)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
    
    def test_update_entry(self):
        """Test updating entries (admin only)"""
        if not self.created_entries:
            self.log_test("Update Entry (No entries to update)", False, "No entries created")
            return
        
        entry_id = self.created_entries[0]
        
        try:
            # Test admin update
            update_data = {
                "title": "Updated Title",
                "content": "This content has been updated",
                "category": "Updated",
                "isShared": True
            }
            
            response = self.admin_session.put(f"{BASE_URL}/entries/{entry_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                success = (data.get("title") == update_data["title"] and
                          data.get("content") == update_data["content"])
                self.log_test("Update Entry (Admin)", success, f"Updated entry {entry_id}")
            else:
                self.log_test("Update Entry (Admin)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
            
            # Test viewer update (should fail)
            response = self.viewer_session.put(f"{BASE_URL}/entries/{entry_id}", json=update_data)
            success = response.status_code == 403
            self.log_test("Update Entry Denied (Viewer)", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Update Entry", False, f"Error: {str(e)}")
    
    def test_delete_entry(self):
        """Test deleting entries (admin only)"""
        if len(self.created_entries) < 2:
            self.log_test("Delete Entry (No entries to delete)", False, "Not enough entries created")
            return
        
        entry_id = self.created_entries[1]  # Use second entry for deletion test
        
        try:
            # Test viewer delete (should fail)
            response = self.viewer_session.delete(f"{BASE_URL}/entries/{entry_id}")
            success = response.status_code == 403
            self.log_test("Delete Entry Denied (Viewer)", success, f"Status: {response.status_code}")
            
            # Test admin delete
            response = self.admin_session.delete(f"{BASE_URL}/entries/{entry_id}")
            
            if response.status_code == 200:
                data = response.json()
                success = "deleted successfully" in data.get("message", "").lower()
                self.log_test("Delete Entry (Admin)", success, f"Deleted entry {entry_id}")
                
                # Remove from tracking list
                if entry_id in self.created_entries:
                    self.created_entries.remove(entry_id)
            else:
                self.log_test("Delete Entry (Admin)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
            
        except Exception as e:
            self.log_test("Delete Entry", False, f"Error: {str(e)}")
    
    def test_data_validation(self):
        """Test data validation for entry creation"""
        invalid_entries = [
            {},  # Empty data
            {"title": ""},  # Empty title
            {"title": "Valid Title"},  # Missing content
            {"title": "Valid Title", "content": "Valid Content"},  # Missing category
        ]
        
        for i, invalid_entry in enumerate(invalid_entries):
            try:
                response = self.admin_session.post(f"{BASE_URL}/entries", json=invalid_entry)
                success = response.status_code in [400, 422]  # Bad request or validation error
                self.log_test(f"Data Validation {i+1}", success, 
                            f"Status: {response.status_code} for invalid data: {invalid_entry}")
            except Exception as e:
                self.log_test(f"Data Validation {i+1}", False, f"Error: {str(e)}")
    
    def test_logout(self):
        """Test logout functionality"""
        try:
            # Test admin logout
            response = self.admin_session.post(f"{BASE_URL}/logout")
            
            if response.status_code == 200:
                data = response.json()
                success = "logged out" in data.get("message", "").lower()
                self.log_test("Logout (Admin)", success, f"Response: {data}")
                
                # Verify session is cleared by trying to access protected endpoint
                response = self.admin_session.get(f"{BASE_URL}/entries")
                session_cleared = response.status_code == 401
                self.log_test("Session Cleared After Logout", session_cleared, 
                            f"Status: {response.status_code}")
            else:
                self.log_test("Logout (Admin)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Logout", False, f"Error: {str(e)}")
    
    def cleanup_test_entries(self):
        """Clean up any remaining test entries"""
        # Re-login as admin for cleanup
        payload = {"password": ADMIN_PASSWORD}
        self.admin_session.post(f"{BASE_URL}/login", json=payload)
        
        for entry_id in self.created_entries:
            try:
                response = self.admin_session.delete(f"{BASE_URL}/entries/{entry_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up test entry: {entry_id}")
                else:
                    print(f"⚠️ Could not clean up entry {entry_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning up entry {entry_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Journal API Backend Tests")
        print(f"📍 Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Basic connectivity
        self.test_health_check()
        
        # Authentication tests
        print("\n🔐 Authentication Tests")
        self.test_admin_login()
        self.test_viewer_login()
        self.test_invalid_login()
        self.test_unauthenticated_access()
        
        # CRUD operations
        print("\n📝 CRUD Operations Tests")
        self.test_create_entry_admin()
        self.test_create_entry_viewer_denied()
        self.test_get_entries_admin()
        self.test_get_entries_viewer()
        
        # Search and filtering
        print("\n🔍 Search and Filtering Tests")
        self.test_search_entries()
        self.test_category_filter()
        self.test_get_categories()
        
        # Update and delete
        print("\n✏️ Update and Delete Tests")
        self.test_update_entry()
        self.test_delete_entry()
        
        # Data validation
        print("\n✅ Data Validation Tests")
        self.test_data_validation()
        
        # Session management
        print("\n🚪 Session Management Tests")
        self.test_logout()
        
        # Cleanup
        print("\n🧹 Cleanup")
        self.cleanup_test_entries()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
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
    tester = JournalAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n💥 Some tests failed!")
        exit(1)