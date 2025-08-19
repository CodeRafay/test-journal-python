#!/usr/bin/env python3
"""
Debug script for entry visibility toggle issue
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://dashboard-load-fix.preview.emergentagent.com/api"
ADMIN_PASSWORD = "12345678"

class EntryVisibilityDebugger:
    def __init__(self):
        self.admin_session = requests.Session()
        self.login_admin()
        
    def login_admin(self):
        """Login as admin"""
        payload = {"password": ADMIN_PASSWORD}
        response = self.admin_session.post(f"{BASE_URL}/login", json=payload)
        if response.status_code == 200:
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            
    def list_all_entries(self):
        """List all entries in the database"""
        print("\n🔍 Checking current entries in database:")
        print("=" * 50)
        
        response = self.admin_session.get(f"{BASE_URL}/entries?grouped=false")
        if response.status_code == 200:
            data = response.json()
            entries = data.get("entries", [])
            
            print(f"Found {len(entries)} entries:")
            for i, entry in enumerate(entries, 1):
                entry_id = entry.get("id") or entry.get("_id")
                title = entry.get("title", "No title")
                is_shared = entry.get("isShared", False)
                category = entry.get("category", "No category")
                
                print(f"{i}. ID: {entry_id}")
                print(f"   Title: {title}")
                print(f"   Category: {category}")
                print(f"   Shared: {is_shared}")
                print(f"   Created: {entry.get('dateCreated', 'Unknown')}")
                print()
                
            return entries
        else:
            print(f"❌ Failed to get entries: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    
    def test_entry_update_with_real_id(self, entry_id: str):
        """Test updating an entry with a real ID"""
        print(f"\n🧪 Testing entry update with ID: {entry_id}")
        print("=" * 50)
        
        # First, get the current entry to see its state
        response = self.admin_session.get(f"{BASE_URL}/entries?grouped=false")
        if response.status_code == 200:
            entries = response.json().get("entries", [])
            target_entry = None
            for entry in entries:
                if (entry.get("id") == entry_id or entry.get("_id") == entry_id):
                    target_entry = entry
                    break
            
            if target_entry:
                current_shared = target_entry.get("isShared", False)
                print(f"Current entry state:")
                print(f"  Title: {target_entry.get('title')}")
                print(f"  Shared: {current_shared}")
                
                # Try to toggle the visibility
                new_shared_state = not current_shared
                update_data = {"isShared": new_shared_state}
                
                print(f"\n🔄 Attempting to toggle visibility to: {new_shared_state}")
                
                response = self.admin_session.put(f"{BASE_URL}/entries/{entry_id}", json=update_data)
                
                print(f"Update response status: {response.status_code}")
                if response.status_code == 200:
                    updated_entry = response.json()
                    print("✅ Update successful!")
                    print(f"New shared state: {updated_entry.get('isShared')}")
                    return True
                else:
                    print("❌ Update failed!")
                    print(f"Response: {response.text}")
                    return False
            else:
                print(f"❌ Entry with ID {entry_id} not found")
                return False
        else:
            print(f"❌ Failed to get entries for verification: {response.status_code}")
            return False
    
    def test_with_invalid_id(self):
        """Test with an invalid ID to reproduce the 404 error"""
        print(f"\n🧪 Testing with invalid ID to reproduce 404 error")
        print("=" * 50)
        
        invalid_ids = [
            "undefined",
            "null", 
            "",
            "invalid-uuid",
            "123456789"
        ]
        
        for invalid_id in invalid_ids:
            print(f"\nTesting with ID: '{invalid_id}'")
            update_data = {"isShared": True}
            
            response = self.admin_session.put(f"{BASE_URL}/entries/{invalid_id}", json=update_data)
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
    
    def test_entry_id_formats(self):
        """Check the format of entry IDs"""
        print(f"\n🔍 Analyzing entry ID formats")
        print("=" * 50)
        
        response = self.admin_session.get(f"{BASE_URL}/entries?grouped=false")
        if response.status_code == 200:
            entries = response.json().get("entries", [])
            
            for entry in entries:
                entry_id = entry.get("id") or entry.get("_id")
                print(f"Entry ID: {entry_id}")
                print(f"  Type: {type(entry_id)}")
                print(f"  Length: {len(str(entry_id))}")
                print(f"  Format: {'UUID-like' if '-' in str(entry_id) else 'Other'}")
                print()
    
    def create_test_entry_and_toggle(self):
        """Create a test entry and try to toggle its visibility"""
        print(f"\n🧪 Creating test entry and testing visibility toggle")
        print("=" * 50)
        
        # Create a test entry
        entry_data = {
            "title": "Visibility Toggle Test Entry",
            "content": "This entry is created to test the visibility toggle functionality.",
            "category": "Test",
            "tags": ["test", "visibility"],
            "isShared": False
        }
        
        response = self.admin_session.post(f"{BASE_URL}/entries", json=entry_data)
        if response.status_code == 200:
            created_entry = response.json()
            entry_id = created_entry.get("id") or created_entry.get("_id")
            print(f"✅ Test entry created with ID: {entry_id}")
            
            # Now try to toggle its visibility
            success = self.test_entry_update_with_real_id(entry_id)
            
            # Clean up the test entry
            delete_response = self.admin_session.delete(f"{BASE_URL}/entries/{entry_id}")
            if delete_response.status_code == 200:
                print(f"✅ Test entry cleaned up")
            else:
                print(f"⚠️ Failed to clean up test entry: {delete_response.status_code}")
                
            return success
        else:
            print(f"❌ Failed to create test entry: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def run_debug_session(self):
        """Run the complete debugging session"""
        print("🔍 ENTRY VISIBILITY TOGGLE DEBUG SESSION")
        print("=" * 60)
        
        # 1. List all current entries
        entries = self.list_all_entries()
        
        # 2. Check entry ID formats
        self.test_entry_id_formats()
        
        # 3. Test with invalid IDs (to reproduce the issue)
        self.test_with_invalid_id()
        
        # 4. Test with real entry IDs if any exist
        if entries:
            print(f"\n🧪 Testing with existing entries")
            print("=" * 50)
            for entry in entries[:2]:  # Test with first 2 entries
                entry_id = entry.get("id") or entry.get("_id")
                if entry_id:
                    self.test_entry_update_with_real_id(entry_id)
        
        # 5. Create a new entry and test toggle
        self.create_test_entry_and_toggle()
        
        print("\n" + "=" * 60)
        print("🏁 DEBUG SESSION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    debugger = EntryVisibilityDebugger()
    debugger.run_debug_session()