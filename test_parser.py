#!/usr/bin/env python3
"""Test the updated parser with actual response."""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.html_parser import parse_verification_html

# Read the debug response
with open("debug_response.html", "r") as f:
    html = f.read()

print("Testing HTML parser with actual API response...\n")

parsed = parse_verification_html(html)

print("Parsed data:")
print("-" * 60)
for key, value in parsed.items():
    if value:
        print(f"  {key:20} → {value}")
    else:
        print(f"  {key:20} → (not found)")

print("-" * 60)
print(f"\n✅ Successfully extracted {sum(1 for v in parsed.values() if v)} out of 8 fields")
