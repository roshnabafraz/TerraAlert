import urllib.request
import json
import glob
import os

count = 0
for mmd_file in glob.glob("c:/Users/roshn/OneDrive/Desktop/Docs/TerraAlert-updatedFiles/Diagrams/*.mmd"):
    with open(mmd_file, "r", encoding="utf-8") as f:
         content = f.read()
    
    url = "https://kroki.io/"
    payload = json.dumps({
      "diagram_source": content,
      "diagram_type": "mermaid",
      "output_format": "jpeg"
    }).encode('utf-8')
    
    out_file = mmd_file.replace(".mmd", ".jpg")
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(out_file, 'wb') as out:
            out.write(response.read())
        print(f"Saved {os.path.basename(out_file)}")
        count += 1
    except Exception as e:
        print(f"Failed {os.path.basename(out_file)}: {e}")

print(f"Total converted: {count}")
