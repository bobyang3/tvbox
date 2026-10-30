# AI - Instruction Files and Automation Scripts

This folder contains documentation and automation scripts for AI-assisted development tasks.

## 📚 Documentation Files

### Migration Guides
- **[javascript-crawler-migration.md](javascript-crawler-migration.md)** - Guide for migrating JavaScript crawlers from old API to new QuickJS API
- **[python-crawler-migration.md](python-crawler-migration.md)** - Guide for migrating Python crawlers to new API

### Task Instructions
- **[add_location_flag.md](add_location_flag.md)** - Instructions for adding country/region flags to location fields in crawler files
- **[js_file_cleanup.md](js_file_cleanup.md)** - Guide for cleaning up JavaScript files
- **[update_filter_year.md](update_filter_year.md)** - Instructions for updating filter year fields

## 🔧 Automation Scripts

### update_area_flags.ps1
PowerShell script to add country/region flags to location (area/地区) fields in crawler files.

**Usage:**
```powershell
# Run from repository root
.\AI\update_area_flags.ps1

# Or from within AI folder
cd AI
.\update_area_flags.ps1
```

**Features:**
- Processes `js/`, `js_decoded/`, and `json/` directories
- Adds flag emojis to country/region names
- Transforms location names consistently:
  - "内地" → "🇨🇳中国"
  - "大陆" → "🇨🇳中国"
  - "中国香港" → "🇭🇰香港"
  - "中国台湾" → "🇹🇼台湾"
- Preserves all backend values unchanged
- Safe to re-run multiple times

**Documentation:** See [add_location_flag.md](add_location_flag.md)

## 🚀 How to Use These Files

### For AI Assistants
When asking an AI assistant to perform tasks, reference these files:

**Example 1 - Add Location Flags:**
```
Please run the update_area_flags.ps1 script from the AI folder following the 
instructions in add_location_flag.md
```

**Example 2 - Migrate JavaScript Crawlers:**
```
Please review javascript-crawler-migration.md and help migrate a JavaScript 
crawler from the old API to the new QuickJS API format
```

### For Direct Use
1. Read the appropriate `.md` file for instructions
2. Run any required scripts
3. Verify the changes
4. Commit using Git

## 📋 File Structure

```
AI/
├── README.md                          (this file)
├── update_area_flags.ps1              (automation script)
├── add_location_flag.md               (task instructions)
├── javascript-crawler-migration.md    (migration guide)
├── python-crawler-migration.md        (migration guide)
├── js_file_cleanup.md                 (task instructions)
└── update_filter_year.md              (task instructions)
```

## 🎯 Quick Reference

| Task | File | Command |
|------|------|---------|
| Add location flags | `add_location_flag.md` | `.\AI\update_area_flags.ps1` |
| Migrate JS crawler | `javascript-crawler-migration.md` | Manual process |
| Migrate Python crawler | `python-crawler-migration.md` | Manual process |
| Cleanup JS files | `js_file_cleanup.md` | Manual process |
| Update filter years | `update_filter_year.md` | Manual process |

## 📝 Notes

- All scripts and instructions are version controlled in Git
- Documentation is kept up-to-date with recent changes
- Scripts are idempotent (safe to run multiple times)
- All scripts preserve backend values and only update display names
- Specific instructions for AI assistants are included in each markdown file

## 🔗 Related Resources

- Repository root contains crawler files in:
  - `js/` - JavaScript crawlers (base64-encoded or plain text)
  - `js_decoded/` - Decoded JavaScript crawlers
  - `json/` - JSON configuration files
  - `py/` - Python crawlers

---

**Last Updated:** 2026-10-30
**Maintained by:** AI Assistant with user direction
