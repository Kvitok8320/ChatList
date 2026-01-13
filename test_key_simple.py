import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OPENROUTER_API_KEY')

with open('key_test_result.txt', 'w', encoding='utf-8') as f:
    if not key:
        f.write('ERROR: OPENROUTER_API_KEY not found in .env file\n')
    else:
        key = key.strip()
        f.write(f'Key found: YES\n')
        f.write(f'Key format: {"CORRECT" if key.startswith("sk-or-v1-") else "INCORRECT"}\n')
        f.write(f'Key length: {len(key)}\n')
        f.write(f'Key preview: {key[:20]}...{key[-10:]}\n\n')
        
        f.write('Testing API connection...\n')
        try:
            r = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://github.com/chatlist',
                    'X-Title': 'ChatList'
                },
                json={
                    'model': 'openai/gpt-3.5-turbo',
                    'messages': [{'role': 'user', 'content': 'Say OK'}]
                },
                timeout=30
            )
            f.write(f'Status code: {r.status_code}\n')
            if r.status_code == 200:
                f.write('SUCCESS! Key works!\n')
                f.write(f'Response: {r.json()["choices"][0]["message"]["content"]}\n')
            else:
                f.write(f'ERROR: {r.text[:300]}\n')
        except Exception as e:
            f.write(f'ERROR: {str(e)}\n')

print('Result saved to key_test_result.txt')



