#test_gsc.py
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_gsc_connection():
    """Test GSC API connection"""
    try:
        print("\n=== Google Search Console API Connection Test ===")
        print(f"Project root: {project_root}")
        
        # 1. Credentials check
        creds_path = project_root / 'config' / 'gcp4-441506-56861cb0311a.json'
        print(f"\n1. Checking credentials at: {creds_path.absolute()}")
        
        if not creds_path.exists():
            print(f"❌ Error: Credentials file not found")
            print(f"Expected at: {creds_path.absolute()}")
            return False
        print("✓ Credentials file found")

        # 2. Create credentials
        print("\n2. Creating credentials...")
        credentials = service_account.Credentials.from_service_account_file(
            str(creds_path),
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        print("✓ Credentials created")

        # 3. Build GSC API client
        print("\n3. Building GSC API client...")
        service = build(
            'searchconsole',
            'v1',
            credentials=credentials,
            cache_discovery=False
        )
        print("✓ API client built")

        # 4. Test API connection
        print("\n4. Testing API connection...")
        sites = service.sites().list().execute()
        
        print("\n=== Available Sites ===")
        if 'siteEntry' in sites:
            for site in sites['siteEntry']:
                print(f"• {site['siteUrl']}")
                print(f"  Permission Level: {site['permissionLevel']}")
                print()
        else:
            print("No sites found or no access to any sites")

        print("\n✓ GSC API connection test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gsc_connection()
    sys.exit(0 if success else 1)