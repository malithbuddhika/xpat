"""HTML parsing utilities for XPAT verification results."""

from __future__ import annotations

import re
from typing import Dict, Optional

from bs4 import BeautifulSoup


def parse_verification_html(html: str) -> Dict[str, Optional[str]]:
    """Parse XPAT verification HTML and return structured data.
    
    Handles the new HTML structure from XPAT API response with kt-widget layout.
    """

    soup = BeautifulSoup(html, "html.parser")
    data: Dict[str, Optional[str]] = {
        "worker_name": None,
        "passport_number": None,
        "company": None,
        "status": None,
        "issued_date": None,
        "permit_valid_till": None,
        "work_site": None,
        "photo_url": None,
    }

    # Extract worker name from <a class="kt-widget__username">
    username_elem = soup.select_one("a.kt-widget__username")
    if username_elem:
        data["worker_name"] = username_elem.get_text(strip=True)
    
    # Extract status from <span class="btn btn-label-info">
    status_elem = soup.select_one("span.btn.btn-label-info")
    if status_elem:
        data["status"] = status_elem.get_text(strip=True)
    
    # Extract company from <a title="current employer">
    company_elem = soup.select_one('a[title="current employer"]')
    if company_elem:
        # Get text without the icon
        text = company_elem.get_text(strip=True)
        data["company"] = text
    
    # Extract passport from <a title="passport number">
    passport_elem = soup.select_one('a[title="passport number"]')
    if passport_elem:
        text = passport_elem.get_text(strip=True)
        data["passport_number"] = text
    
    # Extract issued date: look for text after <b>Issued On: </b>
    for b_tag in soup.find_all("b"):
        if "Issued On" in b_tag.get_text():
            # Get the parent div and extract date text
            parent = b_tag.parent
            if parent:
                text = parent.get_text(strip=True)
                # Extract just the date part (after "Issued On:")
                match = re.search(r"Issued On:\s*(.+?)(?:\s*Work Permit|\s*$)", text)
                if match:
                    data["issued_date"] = match.group(1).strip()
            break
    
    # Extract permit valid till: look for text after <b>Work Permit Valid till: </b>
    for b_tag in soup.find_all("b"):
        if "Work Permit Valid till" in b_tag.get_text():
            # Look in the next span or nearby text
            span = b_tag.find_next("span")
            if span:
                data["permit_valid_till"] = span.get_text(strip=True)
            else:
                # Fallback to next text
                next_text = b_tag.find_next(string=True)
                if next_text:
                    data["permit_valid_till"] = next_text.strip().lstrip(": ").strip()
            break
    
    # Extract work site: look for text after <b>Work Site: </b>
    for b_tag in soup.find_all("b"):
        if "Work Site" in b_tag.get_text():
            # Look in the next span or nearby text
            span = b_tag.find_next("span")
            if span:
                data["work_site"] = span.get_text(strip=True)
            else:
                # Fallback to next text
                next_text = b_tag.find_next(string=True)
                if next_text:
                    data["work_site"] = next_text.strip().lstrip(": ").strip()
            break
    
    # Extract photo URL from <img> tag
    img = soup.find("img", {"alt": "profile"})
    if img and img.get("src"):
        src = img["src"].strip()
        # Convert relative URL to absolute if needed
        if src.startswith("/"):
            src = "https://xpat.egov.mv" + src
        data["photo_url"] = src

    return data
