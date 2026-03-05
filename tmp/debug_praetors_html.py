"""Debug: save sample of Wikipedia praetors HTML to inspect structure."""
import requests
import re

r = requests.get(
    "https://en.wikipedia.org/w/api.php",
    params={"action": "parse", "page": "List_of_Roman_praetors", "format": "json", "prop": "text"},
    headers={"User-Agent": "Chrystallum/1.0"},
    timeout=30,
)
html = r.json()["parse"]["text"]["*"]

# Find 2nd century section - look for 174, 190, 139
for needle in ["174", "190", "139", "200"]:
    idx = html.find(needle)
    if idx >= 0:
        snippet = html[max(0, idx-100):idx+150]
        print(f"--- Found {needle} at {idx} ---")
        print(repr(snippet[:400]))
        print()

# Count year-like numbers
years = re.findall(r">(\d{3})\s*[<\[]", html)
print("Year-like matches:", sorted(set(years))[:50])
