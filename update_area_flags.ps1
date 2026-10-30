# Script to add country/region flags to area/地区 fields in JS files
# Only modifies "n" values, never changes "v" values

$ErrorActionPreference = "Stop"

# Define the mappings
$flagMappings = @{
    # Countries with flags
    # IMPORTANT: Order matters! Process longer strings first to avoid partial matches
    "中国大陆" = "🇨🇳中国大陆"
    "中国香港" = "🇭🇰香港"  # Remove "中国" prefix
    "中国台湾" = "🇹🇼台湾"  # Remove "中国" prefix
    "中国" = "🇨🇳中国"
    "大陆" = "🇨🇳中国"  # Rename 大陆 to 中国
    "内地" = "🇨🇳中国"  # Rename 内地 to 中国
    "香港" = "🇭🇰香港"
    "台湾" = "🇹🇼台湾"
    "日本" = "🇯🇵日本"
    "韩国" = "🇰🇷韩国"
    "美国" = "🇺🇸美国"
    "英国" = "🇬🇧英国"
    "法国" = "🇫🇷法国"
    "德国" = "🇩🇪德国"
    "意大利" = "🇮🇹意大利"
    "西班牙" = "🇪🇸西班牙"
    "加拿大" = "🇨🇦加拿大"
    "澳大利亚" = "🇦🇺澳大利亚"
    "俄罗斯" = "🇷🇺俄罗斯"
    "印度" = "🇮🇳印度"
    "泰国" = "🇹🇭泰国"
    "新加坡" = "🇸🇬新加坡"
    "马来西亚" = "🇲🇾马来西亚"
    "港台" = "🇭🇰🇹🇼港台"
    "港澳台" = "🇭🇰🇲🇴🇹🇼港澳台"
    "欧美" = "🇪🇺🇺🇸欧美"
    "日韩" = "🇯🇵🇰🇷日韩"
    "国产" = "🇨🇳国产"
}

function Update-AreaFlags {
    param(
        [string]$Content
    )
    
    $updated = $Content
    
    # Process mappings in order (longer strings first to avoid partial matches)
    $orderedKeys = $flagMappings.Keys | Sort-Object -Property Length -Descending
    
    foreach ($key in $orderedKeys) {
        $newValue = $flagMappings[$key]
        
        # Pattern 1: {"n":"<key>","v":"..."}
        # This handles cases where n equals the key exactly
        $pattern1 = '(\{"n"\s*:\s*")('+[regex]::Escape($key)+')("\s*,\s*"v"\s*:\s*"[^"]*")'
        $replacement1 = '${1}' + $newValue + '${3}'
        $updated = $updated -replace $pattern1, $replacement1
        
        # Pattern 2: {"n":"<key>","value":"..."}
        $pattern2 = '(\{"n"\s*:\s*")('+[regex]::Escape($key)+')("\s*,\s*"value"\s*:\s*"[^"]*")'
        $replacement2 = '${1}' + $newValue + '${3}'
        $updated = $updated -replace $pattern2, $replacement2
    }
    
    # Clean up any remaining "中国香港" or "中国台湾" in "n" fields that may have flags
    # Pattern: {"n":"🇭🇰中国香港" or {"n":"🇹🇼中国台湾"
    $updated = $updated -replace '(\{"n"\s*:\s*"🇭🇰)中国(香港")', '${1}${2}'
    $updated = $updated -replace '(\{"n"\s*:\s*"🇹🇼)中国(台湾")', '${1}${2}'
    
    return $updated
}

function Process-JSFile {
    param(
        [string]$FilePath
    )
    
    Write-Host "Processing: $FilePath"
    
    try {
        # Read file content
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        
        # Check if file contains area/地区 patterns
        if ($content -notmatch '(area|地区)') {
            Write-Host "  Skipped (no area/地区 found)" -ForegroundColor Gray
            return $false
        }
        
        # Update the content
        $updatedContent = Update-AreaFlags -Content $content
        
        # Check if anything changed
        if ($content -eq $updatedContent) {
            Write-Host "  No changes needed" -ForegroundColor Gray
            return $false
        }
        
        # Write back to file
        [System.IO.File]::WriteAllText($FilePath, $updatedContent, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  Updated successfully" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "=== Starting Area Flag Update ===" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$jsDecodedDir = Join-Path $scriptDir "js_decoded"
$jsDir = Join-Path $scriptDir "js"
$jsonDir = Join-Path $scriptDir "json"

$totalUpdated = 0

# Process js_decoded directory
if (Test-Path $jsDecodedDir) {
    Write-Host "Processing js_decoded directory..." -ForegroundColor Yellow
    $files = Get-ChildItem -Path $jsDecodedDir -Filter "*.js" -File
    Write-Host "Found $($files.Count) files"
    Write-Host ""
    
    foreach ($file in $files) {
        if (Process-JSFile -FilePath $file.FullName) {
            $totalUpdated++
        }
    }
}

Write-Host ""
Write-Host "Processing js directory..." -ForegroundColor Yellow
if (Test-Path $jsDir) {
    $files = Get-ChildItem -Path $jsDir -Filter "*.js" -File
    Write-Host "Found $($files.Count) files"
    Write-Host ""
    
    foreach ($file in $files) {
        if (Process-JSFile -FilePath $file.FullName) {
            $totalUpdated++
        }
    }
}

Write-Host ""
Write-Host "Processing json directory..." -ForegroundColor Yellow
if (Test-Path $jsonDir) {
    $files = Get-ChildItem -Path $jsonDir -Filter "*.json" -File
    Write-Host "Found $($files.Count) files"
    Write-Host ""
    
    foreach ($file in $files) {
        if (Process-JSFile -FilePath $file.FullName) {
            $totalUpdated++
        }
    }
}

Write-Host ""
Write-Host "=== Completed ===" -ForegroundColor Cyan
Write-Host "Total files updated: $totalUpdated" -ForegroundColor Green
Write-Host ""
Write-Host "Summary of changes applied:"
Write-Host "  - Added country/region flags to area names"
Write-Host "  - Renamed '内地' to '🇨🇳中国'"
Write-Host "  - Renamed '大陆' to '🇨🇳中国'"
Write-Host "  - Renamed '中国香港' to '🇭🇰香港' (removed 中国 prefix)"
Write-Host "  - Renamed '中国台湾' to '🇹🇼台湾' (removed 中国 prefix)"
Write-Host "  - Cleaned up any remaining '中国香港' or '中国台湾' in 'n' fields"
Write-Host "  - All 'v' and 'value' fields preserved unchanged"
