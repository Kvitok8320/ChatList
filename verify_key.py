import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("ERROR: OPENROUTER_API_KEY not found")
    exit(1)

api_key = api_key.strip()
print(f"Key found: {api_key[:20]}... (length: {len(api_key)})")

if not api_key.startswith("sk-or-v1-"):
    print("WARNING: Key format may be incorrect")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/chatlist",
    "X-Title": "ChatList"
}

data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say 'OK' if you can read this"}]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        print(f"SUCCESS! Response: {message}")
    else:
        print(f"ERROR {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

