#!/usr/bin/env python3
"""Debug script to see actual API response."""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.session_manager import SessionManager
from app.utils.config import XPAT_VERIFY_URL

def debug_api():
    """Test the XPAT API and print the response."""
    session_mgr = SessionManager.get_instance()
    session = session_mgr.get_session()
    
    # Refresh session
    print("🔄 Refreshing session...")
    session_mgr.refresh()
    
    # Make test request
    data = {
        "workPermitNumber": "WP00636730",
        "firstName": "EK6583697",
    }
    
    print(f"📡 Posting to {XPAT_VERIFY_URL}")
    print(f"📋 Data: {data}")
    
    try:
        response = session.post(XPAT_VERIFY_URL, data=data, timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📏 Response length: {len(response.text)} bytes")
        print("\n" + "="*80)
        print("RESPONSE HTML (first 2000 chars):")
        print("="*80)
        print(response.text[:2000])
        print("\n" + "="*80)
        print("Full response saved to debug_response.html")
        
        # Save full response for inspection
        with open("debug_response.html", "w") as f:
            f.write(response.text)
            
    except Exception as exc:
        print(f"❌ Error: {exc}")

if __name__ == "__main__":
    debug_api()
