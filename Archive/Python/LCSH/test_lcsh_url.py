#!/usr/bin/env python3
"""
Quick test to find correct LCSH bulk download URL
"""

import requests

test_urls = [
    "https://id.loc.gov/download/vocabularysubjects.skosrdf.nt.zip",
    "https://id.loc.gov/download/vocabularysubjects.nt.gz",
    "https://id.loc.gov/download/vocabularysubjects.skosrdf.nt.gz",
    "https://id.loc.gov/static/data/vocabularysubjects.skosrdf.nt.gz",
    "https://id.loc.gov/download/subjects.all.skos.nt.gz",
    "https://id.loc.gov/authorities/subjects.skosrdf.nt.gz",
]

print("Testing LCSH download URLs...\n")

for url in test_urls:
    print(f"Trying: {url}")
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            size = int(response.headers.get('content-length', 0)) / 1024 / 1024
            print(f"  [SUCCESS] {response.status_code} - Size: {size:.1f} MB")
            print(f"  [FOUND] Use this URL!")
            break
        else:
            print(f"  [FAILED] {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\nDone!")


