import bpy
import json
import sys
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
output = "animation-inventory.json"
if "--output" in args:
    output = args[args.index("--output") + 1]

items = []
for action in bpy.data.actions:
    start, end = action.frame_range
    items.append({
        "name": action.name,
        "frame_start": float(start),
        "frame_end": float(end),
        "frame_count": int(round(end - start + 1)),
        "fcurve_count": len(action.fcurves) if hasattr(action, "fcurves") else None,
    })

items.sort(key=lambda x: x["name"].lower())
Path(output).write_text(json.dumps(items, indent=2), encoding="utf-8")
print(f"Found {len(items)} animation actions")
for item in items:
    print(f'{item["name"]}: frames {item["frame_start"]}-{item["frame_end"]}')
