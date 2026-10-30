# Add Location Flags to JS Files

## Overview
This guide explains how to add country/region flag emojis to the "area" (地区) fields in JavaScript crawler files. The script updates display names while preserving all data values.

## Quick Start

Run the PowerShell script from the repository root:

```powershell
.\AI\update_area_flags.ps1
```

Or navigate to the AI folder first:

```powershell
cd AI
.\update_area_flags.ps1
```

This will process all three directories:
- `js_decoded/` - Decoded JavaScript crawler files
- `js/` - Original JavaScript crawler files (base64-encoded or plain text)
- `json/` - JSON configuration files

## What It Does

### 1. Adds Country/Region Flags
Adds flag emojis to country/region names in the `"n"` (name) field for better visual identification.

### 2. Special Transformations (IMPORTANT)
- **内地** → **🇨🇳中国** (renames "内地" to "中国")
- **大陆** → **🇨🇳中国** (renames "大陆" to "中国")
- **中国香港** → **🇭🇰香港** (removes "中国" prefix, keeps only "香港")
- **中国台湾** → **🇹🇼台湾** (removes "中国" prefix, keeps only "台湾")
- **Cleanup:** Removes any remaining "中国" prefix from Hong Kong/Taiwan flags

### 3. Preserves All Values
**CRITICAL RULE:** Only modifies `"n"` (name) fields. **NEVER** changes `"v"` (value) or `"value"` fields.

**IMPORTANT:** When you see `"大陆"` in the `"v"` field, the script will convert it to `"中国"` in the `"n"` field while keeping the original value structure intact.

## Supported Countries/Regions

| Original | Updated | Flag |
|----------|---------|------|
| 中国大陆 | 🇨🇳中国大陆 | 🇨🇳 |
| 中国 | 🇨🇳中国 | 🇨🇳 |
| 大陆 | 🇨🇳中国 | 🇨🇳 |
| 内地 | 🇨🇳中国 | 🇨🇳 |
| 香港 | 🇭🇰香港 | 🇭🇰 |
| 中国香港 | 🇭🇰香港 ⚠️ | 🇭🇰 |
| 台湾 | 🇹🇼台湾 | 🇹🇼 |
| 中国台湾 | 🇹🇼台湾 ⚠️ | 🇹🇼 |
| 日本 | 🇯🇵日本 | 🇯🇵 |
| 韩国 | 🇰🇷韩国 | 🇰🇷 |
| 美国 | 🇺🇸美国 | 🇺🇸 |
| 英国 | 🇬🇧英国 | 🇬🇧 |
| 法国 | 🇫🇷法国 | 🇫🇷 |
| 德国 | 🇩🇪德国 | 🇩🇪 |
| 意大利 | 🇮🇹意大利 | 🇮🇹 |
| 西班牙 | 🇪🇸西班牙 | 🇪🇸 |
| 加拿大 | 🇨🇦加拿大 | 🇨🇦 |
| 澳大利亚 | 🇦🇺澳大利亚 | 🇦🇺 |
| 俄罗斯 | 🇷🇺俄罗斯 | 🇷🇺 |
| 印度 | 🇮🇳印度 | 🇮🇳 |
| 泰国 | 🇹🇭泰国 | 🇹🇭 |
| 新加坡 | 🇸🇬新加坡 | 🇸🇬 |
| 马来西亚 | 🇲🇾马来西亚 | 🇲🇾 |
| 港台 | 🇭🇰🇹🇼港台 | 🇭🇰🇹🇼 |
| 港澳台 | 🇭🇰🇲🇴🇹🇼港澳台 | 🇭🇰🇲🇴🇹🇼 |
| 欧美 | 🇪🇺🇺🇸欧美 | 🇪🇺🇺🇸 |
| 日韩 | 🇯🇵🇰🇷日韩 | 🇯🇵🇰🇷 |
| 国产 | 🇨🇳国产 | 🇨🇳 |

## Examples

### Before
```javascript
filter: {
    "dianying": [
        {
            "key": "area",
            "name": "地区",
            "value": [
                {"n": "全部", "v": ""},
                {"n": "日本", "v": "日本"},
                {"n": "中国香港", "v": "中国香港"},       // ⚠️ Has "中国" prefix
                {"n": "香港", "v": "中国香港"},           // Mixed naming
                {"n": "中国台湾", "v": "中国台湾"},       // ⚠️ Has "中国" prefix
                {"n": "台湾", "v": "中国台湾"},           // Mixed naming
                {"n": "内地", "v": "内地"},
                {"n": "大陆", "v": "大陆"},
                {"n": "中国", "v": "中国大陆"}            // ⚠️ Inconsistent
            ]
        }
    ]
}
```

### After
```javascript
filter: {
    "dianying": [
        {
            "key": "area",
            "name": "地区",
            "value": [
                {"n": "全部", "v": ""},
                {"n": "🇯🇵日本", "v": "日本"},            // ✓ Added flag
                {"n": "🇭🇰香港", "v": "中国香港"},        // ✓ Removed "中国" prefix, v preserved
                {"n": "🇭🇰香港", "v": "中国香港"},        // ✓ Normalized & added flag
                {"n": "🇹🇼台湾", "v": "中国台湾"},        // ✓ Removed "中国" prefix, v preserved
                {"n": "🇹🇼台湾", "v": "中国台湾"},        // ✓ Normalized & added flag
                {"n": "🇨🇳中国", "v": "内地"},            // ✓ Renamed 内地 to 中国
                {"n": "🇨🇳中国", "v": "大陆"},            // ✓ Renamed 大陆 to 中国
                {"n": "🇨🇳中国大陆", "v": "中国大陆"}     // ✓ Added flag
            ]
        }
    ]
}
```

**Key Points:**
- ⚠️ `"n"` values never contain `"中国香港"` or `"中国台湾"` anymore - only `"香港"` or `"台湾"`
- ✓ All `"v"` values are **preserved exactly** as they were
- ✓ `"大陆"` in v field is kept but display name shows `"中国"`

## Key Rules

1. **Only modify `"n"` fields** - Never change `"v"` or `"value"` fields
2. **Preserve all data values** - The backend relies on exact `"v"` values
3. **No "中国" prefix in Hong Kong/Taiwan names** - `"n"` must be `"🇭🇰香港"` or `"🇹🇼台湾"`, never `"🇭🇰中国香港"` or `"🇹🇼中国台湾"`
4. **Rename variations consistently**:
   - `"内地"` → `"🇨🇳中国"` in `"n"` field
   - `"大陆"` → `"🇨🇳中国"` in `"n"` field
   - `"中国香港"` → `"🇭🇰香港"` in `"n"` field (removes "中国" prefix)
   - `"中国台湾"` → `"🇹🇼台湾"` in `"n"` field (removes "中国" prefix)
5. **Works on both directories** - Processes both `js/` and `js_decoded/` directories
6. **Safe to re-run** - Script is idempotent; can be run multiple times
7. **UTF-8 encoding** - Maintains proper UTF-8 encoding for Chinese characters and emojis

## Directories Processed

- `js/` - Original JS files (may be base64-encoded) - ~465 files
- `js_decoded/` - Decoded JS files - ~111 files
- `json/` - JSON configuration files - multiple files

## Output

The script will show:
- ✓ **Updated successfully** - File was modified with flag additions/renames
- **No changes needed** - File already has correct flags or was previously updated
- **Skipped** - File doesn't contain area/地区 fields
- **Error** - File path issue (usually special characters in filename)

Example output:
```
=== Starting Area Flag Update ===

Processing js_decoded directory...
Found 111 files
Processing: js_decoded\348电影网.js
  Updated successfully
Processing: js_decoded\4k剧院.js
  Updated successfully
...

Processing js directory...
Found 465 files
Processing: js\NY影院.js
  No changes needed
...

Processing json directory...
Found ~100 files
Processing: json\黑洞影视.json
  Updated successfully
...

=== Completed ===
Total files updated: 69

Summary of changes applied:
  - Added country/region flags to area names
  - Renamed '内地' to '🇨🇳中国'
  - Renamed '大陆' to '🇨🇳中国'
  - Renamed '中国香港' to '🇭🇰香港' (removed 中国 prefix)
  - Renamed '中国台湾' to '🇹🇼台湾' (removed 中国 prefix)
  - Cleaned up any remaining '中国香港' or '中国台湾' in 'n' fields
  - All 'v' and 'value' fields preserved unchanged
```

## Adding New Countries/Regions

To add support for new countries/regions, edit the `$flagMappings` hashtable in `update_area_flags.ps1`:

```powershell
$flagMappings = @{
    "国家名" = "🏴国家名"
    # Add more mappings here
}
```

## Troubleshooting

### Files with Special Characters
Files with brackets `[]` in their names may show errors due to PowerShell path limitations. This is normal and doesn't affect other files.

### Re-running the Script
Safe to run multiple times. Already updated files will show "No changes needed".

### Verification
Check a sample file to verify changes:
```powershell
Get-Content "js_decoded\4k剧院.js" | Select-String -Pattern "🇯🇵|🇰🇷|🇭🇰|🇹🇼|🇨🇳"
```

## AI Prompt for Future Updates

When asking AI to update location flags, use:

```
Please run the update_area_flags.ps1 script to add country/region flags to JS files.

CRITICAL Requirements:
1. Add flag emojis to country/region names in "n" fields
2. Transform "内地" → "🇨🇳中国" in "n" field
3. Transform "大陆" → "🇨🇳中国" in "n" field
4. Transform "中国香港" → "🇭🇰香港" (REMOVE "中国" prefix from "n" field)
5. Transform "中国台湾" → "🇹🇼台湾" (REMOVE "中国" prefix from "n" field)
6. NEVER modify "v" or "value" fields - keep all values exactly as they were
7. NO "中国香港" or "中国台湾" should appear in "n" fields
8. Process both js/ and js_decoded/ directories

Reference: add_location_flag.md for details
```

## Related Files

- `update_area_flags.ps1` - The PowerShell script
- `javascript-crawler-migration.md` - JS crawler migration guide
- `python-crawler-migration.md` - Python crawler migration guide

## Notes

- Script was last updated: 2026-10-30
- Processes: `js_decoded/` (111 files), `js/` (465 files), `json/` (~100+ files)
- Total files typically updated: ~60-80 files per run
- Processing time: ~2-3 minutes for all directories
- No backup needed (changes are tracked by Git)
- Safe to re-run multiple times (idempotent)
