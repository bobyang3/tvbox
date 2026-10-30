# Update Filter Year Instructions

This document describes how to add new year entries (e.g. 2028, 2029) to all year filter blocks across `.js`, `.json`, and `.py` files in the `tvbox` repository.

## Repository
`C:\Users\Robert Yang\Documents\_project_\GitHub\bobyang3\tvbox`

## Scope
- File extensions: `.js`, `.json`, `.py`
- Target: Year filter blocks where `"key":"year"` and year entries exist in `"value"` arrays
- Years to add: Specify the new year(s) (e.g. `2028`, `2029`)

## Entry Format Rules

### 1. No spaces in year entries
All year entries must be non-spaced:
- Double-quote style: `{"n":"2028","v":"..."}` ✅
- Single-quote style: `{'n':'2028','v':'...'}` ✅
- Spaced: `{"n": "2028", "v": "..."}` ❌ (must be fixed)
- Spaced: `{'n': '2028', 'v': '...'}` ❌ (must be fixed)

### 2. Value format varies by file
Each file uses its own value format. Match the existing format:
- `/year/2028` (most common in `js/` files)
- `2028` (numeric, common in `json/` files)
- `[2028,2029)` (date range, common in `py/` files like B站番剧)
- `[2028-01-01 00:00:00,2029-01-01 00:00:00)` (release_date range)

### 3. Ordering rule: "全部" / "時間全選" FIRST
In every value array containing "全部" or "時間全選":
- `{"n":"全部","v":""}` or `{"n":"時間全選","v":""}` must come FIRST
- Then years in descending order: `2029`, `2028`, `2027`, ...
- Then all other entries (older years, age ranges, etc.)

Correct example:
```
"value":[{"n":"全部","v":""},{"n":"2029","v":"..."},{"n":"2028","v":"..."},{"n":"2027","v":"..."},...]
```

## Workflow

### Step 1: Identify files to modify
```powershell
git -C <repo> ls-files -m | Where-Object { $_ -match '\.(js|json|py)$' }
```
This gives all modified tracked files. Only modify files in this list (plus any others you want to add years to).

### Step 2: Add new year entries
For each year filter value array, insert the new year(s) after "全部"/"時間全選" and before existing years.

Example insertion for 2028:
```
BEFORE: "value":[{"n":"全部","v":""},{"n":"2027","v":"..."},{"n":"2026","v":"..."},...]
AFTER:  "value":[{"n":"全部","v":""},{"n":"2028","v":"..."},{"n":"2027","v":"..."},{"n":"2026","v":"..."},...]
```

### Step 3: Normalize spacing
Remove all spaces inside year entries:
- `{"n": "2028", "v": "..."}` → `{"n":"2028","v":"..."}`
- `{'n': '2028', 'v': '...'}` → `{'n':'2028','v':'...'}`

### Step 4: Fix line endings (Windows)
If a file's HEAD version is LF-only but the working copy has CRLF, convert CRLF → LF:
```powershell
(Get-Content <file> -Raw).Replace("`r`n","`n") | Set-Content <file> -Encoding UTF8 -NoNewline
```

### Step 5: Validate
Run all checks:
1. No spaced year entries for new years
2. No CRLF regressions in modified files (HEAD is LF-only → working copy must be LF-only)
3. "全部"/"時間全選" comes before all years in every value array
4. New years (2028, 2029...) present in all files that have `"key":"time"` filters

## Common Pitfalls

| Issue | Description | Fix |
|-------|-------------|-----|
| Missing tracked files | `git ls-files -m` lists files that don't exist on disk (e.g. `js/archived/01看球[球].js`) | Skip files where `Test-Path` returns false |
| Special filenames | Some filenames contain special characters (brackets, emoji) that fail on Windows `WriteAllText` | Wrap file writes in try/catch; skip and report |
| CRLF introduction | Python's `open(path,'w')` on Windows can introduce CRLF | Use `open(path,'wb')` with UTF-8 encoded bytes, or convert back to LF after writing |
| Spaced entries from `add_years.py` | Original year-adding script may insert spaced entries | Run normalization regex after adding years |
| Multi-line entries | Some files have year entries spread across multiple lines | Use `[\s\S]*?` in regex to match across lines |

## Regex Patterns

### Match any year entry (double-quote)
```
\{\s*"n"\s*:\s*"2028"\s*,\s*"v"\s*:\s*"([^"]*)"\s*\}
```

### Match any year entry (single-quote)
```
\{\s*'n'\s*:\s*'2028'\s*,\s*'v'\s*:\s*'([^']*)'\s*\}
```

### Match spaced year entry (has space after `{`)
```
\{\s+"n"\s*:\s*"2028"
```

### Match value array containing years
```
"value"\s*:\s*\[([\s\S]*?)\]\s*[,}]
```

## Validation Script Outline

```powershell
# 1. Check no spaced entries for new years
# 2. Check no CRLF regressions
# 3. Check "全部"/"時間全選" before years in every value array
# 4. Check new years present in files with "key":"time"
```

## Files Modified in Previous Run (2027 added)

Approximately 1,121 modified tracked files across:
- `js/` - JavaScript filter configs (most common, value format `/year/YYYY`)
- `json/` - JSON filter configs (value format `YYYY`)
- `py/` - Python spider configs (value format `[YYYY,YYYY+1)` or date ranges)
- `lib/` - Library filter configs
- `json/archived/` - Archived JSON configs

## Example PowerShell One-Liner to Add a Year

```powershell
# Insert 2028 after "全部" in double-quote style files
$content = [regex]::Replace($content,
    '(\{"n":"全部","v":""\}[\s\S]*?\{"n":"2027"',
    '{"n":"全部","v":""},{"n":"2028","v":"<VALUE>"},{"n":"2027"')
```

Replace `<VALUE>` with the correct value format for each file.
