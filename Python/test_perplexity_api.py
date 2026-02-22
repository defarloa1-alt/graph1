import os
import requests

API_URL = "https://api.perplexity.ai/chat/completions"
API_KEY = os.getenv("PERPLEXITY_API_KEY")

if not API_KEY:
    print("PERPLEXITY_API_KEY not set in environment.")
    exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar-pro",
    "messages": [
        {"role": "user", "content": "Hello, Perplexity! Test connection."}
    ],
    "max_tokens": 100
}

response = requests.post(API_URL, headers=headers, json=data)
print("Status:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Raw response:", response.text)
