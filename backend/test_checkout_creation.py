import requests

token = '60d67733c0532b56cc4cb74353dc5e10dd08b7e5'
url = 'http://127.0.0.1:8000/api/billing/upgrade/'
headers = {'Authorization': f'Token {token}'}

print("--- Testing STARTER ---")
data = {'target_plan': 'STARTER', 'billing_cycle': 'month'}
try:
    res = requests.post(url, json=data, headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Testing PRO ---")
data = {'target_plan': 'PRO', 'billing_cycle': 'month'}
try:
    res = requests.post(url, json=data, headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
