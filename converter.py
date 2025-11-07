#!/usr/bin/env python3

### Please note this program is 100% vibe coded

"""
v3 — ensure ALL dreams are exported (list-based JSON)
Includes created timestamps and favourite tags
"""

import json, os, sys, re
from datetime import datetime, timezone

INPUT_FILE = "luci_export.json"
OUTPUT_FOLDER = "Joplin_Dreams"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

CONTENT_KEYS = ["text", "content", "note", "body", "dream", "description"]
DATE_KEYS = ["timestamp", "date", "created", "created_at", "created_time"]
TAG_KEYS = ["tags", "labels", "tag", "categories"]

ROMAN_MAP = {
    'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,
    'XI':11,'XII':12,'XIII':13,'XIV':14,'XV':15
}

def extract_content(obj):
    for k in CONTENT_KEYS:
        if k in obj and obj[k]:
            return str(obj[k])
    # fallback to title if present
    if "title" in obj and obj["title"]:
        return str(obj["title"])
    return ""

def extract_created(obj):
    for k in DATE_KEYS:
        if k in obj and obj[k]:
            return str(obj[k])
    return ""

def normalize_timestamp(s):
    if not s:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    s = str(s).strip()
    if re.fullmatch(r"\d{10,13}", s):
        ts = int(s) / (1000 if len(s)==13 else 1)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def make_title(content, idx):
    for ln in content.splitlines():
        if ln.strip():
            return ln.strip()[:120].replace('"', "'")
    return f"Dream {idx}"

def make_filename(title, idx):
    name = re.sub(r'[\\/:*?"<>|]', "", title).strip()
    return (name or f"Dream_{idx}") + ".md"

def gather_tags(obj):
    tags = []
    for key in TAG_KEYS:
        if key in obj and obj[key]:
            val = obj[key]
            if isinstance(val, list):
                for it in val:
                    if isinstance(it, str):
                        tags.append(it.strip())
            elif isinstance(val, str):
                for part in re.split(r'\s*,\s*', val):
                    if part.strip():
                        tags.append(part.strip())
    return tags

def roman_or_integer_to_int(token):
    token = token.upper()
    if token.isdigit():
        return int(token)
    if token in ROMAN_MAP:
        return ROMAN_MAP[token]
    roman_vals = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
    total, prev = 0,0
    for ch in token[::-1]:
        val = roman_vals.get(ch,0)
        total = total - val if val<prev else total + val
        prev = val
    return total if total>0 else None

def extract_favourite_tags(obj):
    raw_tags = gather_tags(obj)
    out = []
    for t in raw_tags:
        if "favourite" not in t.lower():
            continue
        s = t.strip()
        m = re.search(r"favourite\s*[-_ ]*\s*([ivxlcdm]+|\d+)$", s, flags=re.IGNORECASE)
        if m:
            num = roman_or_integer_to_int(m.group(1))
            if num:
                out.append(f"dream-favourite-{num}")
                continue
        out.append("dream-favourite")
    seen=set();final=[]
    for x in out:
        if x not in seen:
            seen.add(x);final.append(x)
    return final

# Load JSON
try:
    notes = json.load(open(INPUT_FILE, encoding="utf-8"))
    if not isinstance(notes, list):
        print("Expected top-level list in JSON.", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print("ERROR loading JSON:", e, file=sys.stderr)
    sys.exit(1)

count = 0
for i,note in enumerate(notes, start=1):
    content = extract_content(note).replace("\\r\\n","\n").replace("\r\n","\n").replace("\r","\n").strip()
    title = make_title(content, i)
    filename = make_filename(title, i)
    created = normalize_timestamp(extract_created(note))
    tags = extract_favourite_tags(note)
    yaml_lines = ["---", f'title: "{title}"', f"created: {created}", f"updated: {created}"]
    if tags:
        yaml_lines.append("tags:")
        for tt in tags:
            yaml_lines.append(f"  - {tt}")
    yaml_lines.append("---")
    yaml_lines.append("")
    yaml_lines.append(content)
    yaml_lines.append("")
    out_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(out_path,"w",encoding="utf-8") as fo:
        fo.write("\n".join(yaml_lines))
    count +=1

print(f"✅ Done. {count} notes written to {OUTPUT_FOLDER}/")
print("Import with: File → Import → MD - Markdown + Front Matter (Directory)")
