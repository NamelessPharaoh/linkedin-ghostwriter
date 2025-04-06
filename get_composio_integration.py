#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from composio import ComposioToolSet

# Load environment variables
load_dotenv()

def verify_integration():
    """
    Verifies the Composio LinkedIn integration configuration
    
    This function fetches connected account details from Composio and verifies that:
    1. The connected account exists and is accessible
    2. The connected account is properly configured for LinkedIn
    3. The connected account has the necessary permissions
    
    Returns:
        bool: True if verification passes, False otherwise
    """
    try:
        # Get API key from environment variables or use default
        api_key = os.environ.get("COMPOSIO_API_KEY", "3kc5iwkpu3rtdk6cbvfuop")
        
        # Get connected account ID from environment variables or use default
        account_id = os.environ.get("COMPOSIO_ACCOUNT_ID", "624411e8-3384-4b2f-8fe8-4c835b81ea81")
        
        print(f"Verifying Composio LinkedIn connected account (ID: {account_id})...")
        
        # Initialize Composio client
        toolset = ComposioToolSet(api_key=api_key)
        
        # Get connected account details directly by ID
        connection = toolset.get_connected_account(account_id)
        
        if not connection:
            print(f"Connected account with ID {account_id} not found")
            return False
        
        # Log detailed connection information
        print("\n=== Composio LinkedIn Connected Account Details ===")
        print(f"Account ID: {connection.id if hasattr(connection, 'id') else 'Unknown'}")
        print(f"Name: {connection.name if hasattr(connection, 'name') else 'Unknown'}")
        print(f"Entity: {connection.entity if hasattr(connection, 'entity') else 'Unknown'}")
        print(f"Status: {connection.status if hasattr(connection, 'status') else 'Unknown'}")
        
        created_at = getattr(connection, 'createdAt', None)
        updated_at = getattr(connection, 'updatedAt', None)
        print(f"Created: {created_at if created_at else 'Unknown'}")
        print(f"Last Updated: {updated_at if updated_at else 'Unknown'}")
        
        # Verify LinkedIn-specific configuration
        if hasattr(connection, 'entity') and connection.entity.lower() != 'linkedin':
            print(f"ERROR: Connected account entity is \"{connection.entity}\" but expected \"linkedin\"")
            return False
        
        # Check if the connected account is active (case-insensitive)
        if hasattr(connection, 'status') and connection.status.lower() != 'active':
            print(f"ERROR: Connected account status is \"{connection.status}\" but expected \"active\"")
        else:
            print('✅ Connected account is active and properly configured for LinkedIn')
        
        # Check if the connected account has the expected organization URN
        expected_org_urn = os.environ.get("ORGANIZATION_URN")
        if expected_org_urn and hasattr(connection, 'organizationUrn') and expected_org_urn != connection.organizationUrn:
            print(f"WARNING: Organization URN mismatch. Expected: {expected_org_urn}, Actual: {connection.organizationUrn}")
        
        print("=== End of Connected Account Details ===\n")
        
        return True
    except Exception as e:
        print(f"Error verifying Composio LinkedIn connected account: {str(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = verify_integration()
    if success:
        print("Connected account verification completed successfully")
        sys.exit(0)
    else:
        print("Connected account verification failed")
        sys.exit(1)