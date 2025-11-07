# Purpose
This tool converts dream entries exported from the discontinued Luci dream journal app into a format compatible with the open-source note-taking app Joplin.

It takes JSON exported from Luci and converts each dream into an individual Markdown file with YAML front matter, preserving:
- Dream text
- Creation date
- Titles (or auto-generated titles when missing)
- Selected tags (e.g., Favourite → dream-favourite, Favourite II → dream-favourite-2)

Although originally developed for Luci dream logs, the script may also be adapted for other JSON-based dream trackers or journaling apps.

# Checking your Luci export
You may want to ensure the resulting export doesn't have blank timestamps:

`cat luci_export.json | jq '.[].timestamp' | grep -E '^0$' | wc -l`

In my case, the entire latter half of my entry exports were corrupted in this way:
```
cat luci_export.json | jq '.[].timestamp' | tail -3000 | grep -E '^0$' | wc -l
    2979
```

Unfortunately, Luci fails when exporting many in this regard, as well as dropping the tags so that it's an empty list. It probably drops all metadata after a few thousand entries, but at least the contents are intact.

# Usage
1. Place the export in the same folder as the script with name `luci_export.json`
2. `python3 converter.py`
3. Import into Joplin from the resulting directory as instructed by the script (best to try with just one file first)

# Limitation
The program didn't cary over all the tags, so I had to make sure I verified it manually.

# Verify
You may want to verify with various counts, or manually address mismatches. You can open the export and show the contents of every dream tagged with Favourite with this:
```
jq -r '.[]
       | select(.tags != null and (.tags[] | test("(?i)^Favourite")))
       | "--- DREAM START ---\nTitle: \(.title // "No Title")\nCreated: \(.timestamp)\n\(.text)\n--- DREAM END ---"' luci_export.json | less
```
