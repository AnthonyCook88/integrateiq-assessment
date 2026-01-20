"""
Integrate IQ Assessment - HubSpot Contact Integration
Fetches contact data from AWS API and syncs to HubSpot
"""

import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AWS_API_URL = os.getenv("AWS_API_URL")
AWS_BEARER_TOKEN = os.getenv("AWS_BEARER_TOKEN")
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"


class HubSpotClient:
    """Client for interacting with HubSpot API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """
        Search for a contact by email address
        Returns the contact object if found, None otherwise
        """
        url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/search"
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email
                        }
                    ]
                }
            ],
            "properties": ["email", "firstname", "lastname", "phone", "company"]
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                return data["results"][0]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error searching for contact with email {email}: {e}")
            return None
    
    def create_or_update_contact(self, contact_data: Dict) -> bool:
        """
        Create a new contact or update an existing one based on email
        Returns True if successful, False otherwise
        """
        email = contact_data.get("email")
        if not email:
            print("Contact data missing email address, skipping...")
            return False
        
        # Check if contact already exists
        existing_contact = self.get_contact_by_email(email)
        
        if existing_contact:
            # Update existing contact
            contact_id = existing_contact["id"]
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"
            method = "PATCH"
            print(f"Updating existing contact: {email} (ID: {contact_id})")
        else:
            # Create new contact
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"
            method = "POST"
            print(f"Creating new contact: {email}")
        
        # Prepare properties for HubSpot
        properties = {}
        
        # Map AWS API fields to HubSpot properties
        if "firstname" in contact_data or "firstName" in contact_data:
            properties["firstname"] = contact_data.get("firstname") or contact_data.get("firstName", "")
        if "lastname" in contact_data or "lastName" in contact_data:
            properties["lastname"] = contact_data.get("lastname") or contact_data.get("lastName", "")
        if "email" in contact_data:
            properties["email"] = contact_data["email"]
        if "phone" in contact_data:
            properties["phone"] = contact_data["phone"]
        if "company" in contact_data:
            properties["company"] = contact_data["company"]
        
        payload = {"properties": properties}
        
        try:
            if method == "POST":
                response = requests.post(url, json=payload, headers=self.headers)
            else:
                response = requests.patch(url, json=payload, headers=self.headers)
            
            response.raise_for_status()
            print(f"✓ Successfully {'created' if method == 'POST' else 'updated'} contact: {email}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error {'creating' if method == 'POST' else 'updating'} contact {email}: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return False


def fetch_aws_contacts() -> List[Dict]:
    """
    Fetch contact data from AWS API
    Returns a list of contact dictionaries
    """
    headers = {
        "Authorization": f"Bearer {AWS_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Fetching contacts from AWS API: {AWS_API_URL}")
        response = requests.get(AWS_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            contacts = data
        elif isinstance(data, dict):
            # Try common keys that might contain the contacts array
            contacts = data.get("contacts") or data.get("data") or data.get("items") or []
            if not isinstance(contacts, list):
                contacts = [data]  # If it's a single contact object
        else:
            contacts = []
        
        print(f"✓ Successfully fetched {len(contacts)} contacts from AWS API")
        return contacts
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching contacts from AWS API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return []


def sync_contacts_to_hubspot():
    """
    Main function to sync contacts from AWS API to HubSpot
    """
    # Validate required environment variables
    if not HUBSPOT_API_KEY:
        print("✗ Error: HUBSPOT_API_KEY environment variable is not set")
        print("  Please set it in your .env file or environment variables")
        return
    
    if not AWS_API_URL:
        print("✗ Error: AWS_API_URL environment variable is not set")
        print("  Please set it in your .env file or environment variables")
        return
    
    if not AWS_BEARER_TOKEN:
        print("✗ Error: AWS_BEARER_TOKEN environment variable is not set")
        print("  Please set it in your .env file or environment variables")
        return
    
    # Fetch contacts from AWS
    contacts = fetch_aws_contacts()
    if not contacts:
        print("No contacts to sync")
        return
    
    # Initialize HubSpot client
    hubspot = HubSpotClient(HUBSPOT_API_KEY)
    
    # Process each contact
    success_count = 0
    error_count = 0
    
    print(f"\nSyncing {len(contacts)} contacts to HubSpot...")
    print("-" * 60)
    
    for contact in contacts:
        if hubspot.create_or_update_contact(contact):
            success_count += 1
        else:
            error_count += 1
    
    print("-" * 60)
    print(f"\nSync complete!")
    print(f"  Successfully processed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(contacts)}")


if __name__ == "__main__":
    sync_contacts_to_hubspot()
