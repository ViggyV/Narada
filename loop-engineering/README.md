# Loop Engineering — blog site

A self-contained static blog: nine-part field manual on loop engineering with Claude Code.

## Read it
- Open `index.html` directly, or serve locally:
  ```
  python3 -m http.server 8000
  # → http://localhost:8000
  ```
- Works on GitHub Pages as-is (all links are relative).

## Edit it
Source markdown lives in `content/`. After editing, rebuild:
```
pip install markdown   # once
python3 build.py
```
`build.py` re-renders every post and the index; post titles, summaries, and stage
tags live in the `POSTS` list at the top of the script.
