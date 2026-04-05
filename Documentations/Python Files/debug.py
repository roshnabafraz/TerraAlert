import urllib.request
import json

url = "https://kroki.io/"
payload = json.dumps({
  "diagram_source": "graph TD\nA-->B",
  "diagram_type": "mermaid",
  "output_format": "jpeg"
}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(response.status)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response Body:", e.read().decode('utf-8', errors='ignore'))
except Exception as e:
    print("Error:", e)
