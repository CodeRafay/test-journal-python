#!/usr/bin/env python3
"""
Production Deployment Verification Script
Tests all critical functionality of the deployed Journal App
"""

import requests
import json
import sys
from typing import Optional

class DeploymentVerifier:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.admin_logged_in = False
        self.test_entry_id = None
        
    def test_health_check(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/api/")
            return response.status_code == 200 and "Journal API" in response.text
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_admin_login(self) -> bool:
        """Test admin authentication"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/login",
                json={"password": "12345678"}
            )
            if response.status_code == 200:
                data = response.json()
                self.admin_logged_in = data.get("role") == "admin"
                return self.admin_logged_in
            return False
        except Exception as e:
            print(f"❌ Admin login failed: {e}")
            return False
    
    def test_viewer_login(self) -> bool:
        """Test viewer authentication"""
        try:
            # Logout first
            self.session.post(f"{self.base_url}/api/logout")
            
            response = self.session.post(
                f"{self.base_url}/api/login", 
                json={"password": "87654321"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("role") == "viewer"
            return False
        except Exception as e:
            print(f"❌ Viewer login failed: {e}")
            return False
    
    def test_create_entry(self) -> bool:
        """Test entry creation (admin only)"""
        if not self.admin_logged_in:
            self.test_admin_login()
            
        try:
            entry_data = {
                "title": "Deployment Test Entry",
                "content": "This entry verifies the deployment is working correctly.",
                "category": "Testing", 
                "tags": ["deployment", "verification"],
                "isShared": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/entries",
                json=entry_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_entry_id = data.get("id")
                return True
            return False
        except Exception as e:
            print(f"❌ Create entry failed: {e}")
            return False
    
    def test_get_entries(self) -> bool:
        """Test retrieving entries"""
        try:
            response = self.session.get(f"{self.base_url}/api/entries")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Get entries failed: {e}")
            return False
    
    def test_search_entries(self) -> bool:
        """Test search functionality"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/entries",
                params={"search": "deployment"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Search entries failed: {e}")
            return False
    
    def test_get_categories(self) -> bool:
        """Test category retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/categories")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Get categories failed: {e}")
            return False
    
    def test_update_entry(self) -> bool:
        """Test entry updating"""
        if not self.test_entry_id:
            return False
            
        try:
            update_data = {
                "title": "Updated Deployment Test Entry"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/entries/{self.test_entry_id}",
                json=update_data
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Update entry failed: {e}")
            return False
    
    def test_delete_entry(self) -> bool:
        """Test entry deletion"""
        if not self.test_entry_id:
            return False
            
        try:
            response = self.session.delete(
                f"{self.base_url}/api/entries/{self.test_entry_id}"
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Delete entry failed: {e}")
            return False
    
    def run_full_verification(self) -> bool:
        """Run complete deployment verification"""
        print(f"🔍 Verifying deployment at: {self.base_url}")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Login", self.test_admin_login),
            ("Viewer Login", self.test_viewer_login),  
            ("Create Entry", self.test_create_entry),
            ("Get Entries", self.test_get_entries),
            ("Search Entries", self.test_search_entries),
            ("Get Categories", self.test_get_categories),
            ("Update Entry", self.test_update_entry),
            ("Delete Entry", self.test_delete_entry),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test_name}: {e}")
        
        print("=" * 50)
        print(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Deployment is successful.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the deployment.")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python verify-deployment.py <backend-url>")
        print("Example: python verify-deployment.py https://your-app.vercel.app")
        sys.exit(1)
    
    base_url = sys.argv[1]
    verifier = DeploymentVerifier(base_url)
    
    success = verifier.run_full_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()