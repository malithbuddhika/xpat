"""Debug script to test HTML parser and verify date extraction."""

from app.services.html_parser import parse_verification_html
from app.services.xpat_client import XpatClient
from app.services.session_manager import SessionManager

# Test the specific employee
work_permit = "WP00636730"
passport = "EK6583697"

session_manager = SessionManager.get_instance()
session = session_manager.get_session()
session_manager.refresh()

data = {
    "workPermitNumber": work_permit,
    "firstName": passport,
}

print(f"Testing verification for {work_permit} / {passport}")
print("-" * 60)

try:
    response = session.post(
        "https://xpat.egov.mv/EmploymentApproval/EmploymentApproval/WorkPermitVerify",
        data=data,
        timeout=10,
    )
    response.raise_for_status()
    
    print(f"Response status: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    print("\n--- Full HTML Response ---")
    print(response.text)
    print("\n--- Parsed Results ---")
    
    parsed = parse_verification_html(response.text)
    for key, value in parsed.items():
        print(f"{key}: {value}")
        
except Exception as e:
    print(f"Error: {e}")
