import urllib.request
import base64

def encode(text):
    # JSON-like wrapper usually required by newer mermaid.ink
    state = f'{{"code":"{text}","mermaid":"{{"theme":"default"}}","autoSync":true,"updateDiagram":true}}'
    b64 = base64.urlsafe_b64encode(state.encode('utf-8')).decode('utf-8')
    # strip padding
    b64 = b64.rstrip('=')
    return f"https://mermaid.ink/img/{b64}?type=jpeg"

url = encode("graph TD\nA-->B")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as r:
        print("Mermaid.ink status:", r.status)
except Exception as e:
    print("Mermaid.ink error:", e)
