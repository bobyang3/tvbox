# JS Filter 解碼與驗證作業說明（全專案）

本檔記錄如何將專案中所有 `.js` / `.json` 檔案內，以 base64+gzip 編碼寫入的 `filter` 欄位，解碼為可讀 JSON 格式，並驗證檔案無誤的完整作業流程。適用於 `js_decoded/`、`js/`、`json/` 等所有資料夾。可用於重複執行相同任務。

---

## 1. 偵測：尋找還未解碼的 filter

在整個專案根目錄中搜尋所有仍含 `H4sI`（base64+gzip 標頭）的 `filter` 欄位：

```powershell
# 搜尋整個解決方案內含 H4sI 的檔案
rg -l "H4sI" . --glob '!node_modules' --glob '!.git'

# 僅找出 filter 欄位仍為編碼字串的檔案（單引號或雙引號）
rg -n "filter:\s*['\"]?H4sI" . --glob '!node_modules' --glob '!.git'

# 找出 filter 欄位鍵名帶引號的情形（如 "filter": "H4sI..."）
rg -n '"filter"\s*:\s*"H4sI' . --glob '!node_modules' --glob '!.git'
```

預期發現的編碼樣式有三種：

| 樣式 | 範例 |
|------|------|
| `filter: 'H4sI...'` | 單引號，鍵名無引號 |
| `filter: "H4sI..."` | 雙引號，鍵名無引號 |
| `"filter": "H4sI..."` | 雙引號，鍵名也帶引號 |

> 注意：若 `H4sI` 出現在 `class_parse`、`lazy`、`$js.toString(() => {...})` 等執行期程式碼中（例如 `JSON.parse(ungzip('H4sI...'))`），**不屬於 filter 欄位**，應保留不動。

---

## 2. 解碼：將 base64+gzip 轉為 JSON

每個編碼字串都是 **base64 → gzip → JSON**。可用 PowerShell 一次解碼並取得純 JSON 文字：

```powershell
$b64 = 'H4sIAAAAAAAAA...'  # 貼上 filter 欄位內的 base64 字串（不含引號）
$bytes = [Convert]::FromBase64String($b64)
$ms = New-Object System.IO.MemoryStream
$ms.Write($bytes, 0, $bytes.Length)
$ms.Position = 0
$gzip = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
$reader = New-Object System.IO.StreamReader($gzip)
$json = $reader.ReadToEnd()
$reader.Close(); $gzip.Close(); $ms.Close()
$json
```

輸出應為可讀的 JSON 物件，例如：

```json
{"1":[{"key":"cateId","name":"類型","value":[{"n":"全部","v":"1"},{"n":"動作片","v":"6"}]}],"2":[...]}
```

---

## 3. 取代：將編碼字串換成可讀 JSON

在目標 `.js` / `.json` 檔中，將整個 `filter: 'H4sI...'`（或 `filter: "H4sI..."` / `"filter": "H4sI..."`）替換為 `filter: <解碼後的 JSON>`。

PowerShell 範例（逐檔執行）：

```powershell
$dir = 'C:\Users\Robert Yang\Documents\_project_\GitHub\bobyang3\tvbox'
$file = 'js/58动漫.js'
$path = Join-Path $dir $file
$content = Get-Content -LiteralPath $path -Raw

# 單引號 filter
if ($content -match "filter:\s*'(H4sI[^']+)'") {
    $b64 = $matches[1]
    # ...解碼成 $json...
    $newContent = $content -replace "filter:\s*'H4sI[^']+'", "filter: $json"
    Set-Content -LiteralPath $path -Value $newContent -Encoding UTF8
}
# 雙引號 filter
elseif ($content -match 'filter:\s*"(H4sI[^"]+)"') {
    $b64 = $matches[1]
    # ...解碼成 $json...
    $newContent = $content -replace 'filter:\s*"H4sI[^"]+"', "filter: $json"
    Set-Content -LiteralPath $path -Value $newContent -Encoding UTF8
}
# 帶引號鍵名 "filter"
elseif ($content -match '"filter"\s*:\s*"(H4sI[^"]+)"') {
    $b64 = $matches[1]
    # ...解碼成 $json...
    $newContent = $content -replace '"filter"\s*:\s*"H4sI[^"]+"', '"filter": ' + $json
    Set-Content -LiteralPath $path -Value $newContent -Encoding UTF8
}
```

取代後，`filter` 欄位應為一個直接寫在檔案裡的 JSON 物件，例如：

```javascript
filter: {"1":[{"key":"cateId","name":"類型","value":[{"n":"全部","v":"1"}]}],"2":[...]},
```

---

## 4. 驗證：確認 JS 檔案格式正確且無錯誤

### 4.1 確認不再有編碼 filter

```powershell
# 整個解決方案不應再有 filter 欄位含 H4sI
rg -n "filter:\s*['\"]?H4sI" . --glob '!node_modules' --glob '!.git'  # 應無輸出（除文件本體外）
rg -n '"filter"\s*:\s*"H4sI' . --glob '!node_modules' --glob '!.git'   # 應無輸出
```

### 4.2 確認 filter 為合法 JSON 物件

開啟目標 `.js`，目視確認 `filter:` 後方直接跟 `{` 開頭的 JSON，並以 `}` 與 `,` 結尾，不再有長串 base64 字元。

### 4.3 用 Node.js 語法檢查（若環境可用）

若檔案可在 Node.js 下解析（不依賴 TVBox 特有全域變數如 `muban`、`$js`），可用：

```bash
node --check js_decoded/HDmoli.js
```

> 許多 `js_decoded/` 檔案含 TVBox 特有語法（`muban.`、`$js.toString`、`var rule`），`node --check` 可能報語法錯誤，此時可僅做目視與結構檢查。

### 4.4 檢查 filter_def 與 filter 欄位對齊

開啟檔案後確認 `filter_def` 中的索引鍵（如 `1`, `2`, `41`）與 `filter` 物件中的鍵一致。範例：

```javascript
filter: {"1":[...],"2":[...],"41":[...]},
filter_def: {
    1: { 類型: "1" },
    2: { 類型: "2" },
    41: { 類型: "41" }
},
```

---

## 5. 測試：確認爬蟲可正常載入與解析

### 5.1 結構檢查清單

對每個已修改的 `.js` 檔，逐項確認：

| 檢查項目 | 如何確認 |
|---------|---------|
| `filter` 不再是 base64 | 檔案內不再出現 `H4sI` 在 `filter` 欄位 |
| `filter` 為 JSON 物件 | `filter:` 後方是 `{...}` |
| `filter_url` 欄位存在 | 且使用 `{{fl.xxx}}` 占位符與 `filter` 的 key 對應 |
| `filter_def` 欄位存在 | 索引鍵與 `filter` 物件鍵一致 |
| 檔案編碼為 UTF-8 | 無亂碼，中文顯示正確 |

### 5.2 與範例檔對照

可參考已完成解碼的檔案作為格式基準：

- `js_decoded/子子影视.js`
- `js_decoded/七年影视.js`
- `js_decoded/4k剧院.js`（本次已解碼）

這些檔案的 `filter` 欄位皆為直接寫入的 JSON 物件，可當作格式參照。

### 5.3 實際爬蟲測試（視環境而定）

若有 TVBox/App 可載入這些 `.js` 檔，應進行：

1. 載入爬蟲，確認不崩潰。
2. 進入分類頁，確認篩選選項正確顯示（類型、地區、年份、排序等）。
3. 切換不同 `filter_def` 索引（1/2/3/4…），確認對應篩選項正確。
4. 使用 `filter_url` 組合出的 URL 能正常請求並取得列表。

---

## 6. 批次處理範例腳本

下方為可重複使用的 PowerShell 腳本框架，將它儲存為 `decode-filters.ps1` 放在專案根目錄：

```powershell
# decode-filters.ps1
$root = 'C:\Users\Robert Yang\Documents\_project_\GitHub\bobyang3\tvbox'

# 找出所有含 base64+gzip 編碼 filter 的 .js / .json 檔
$files = Get-ChildItem -Path $root -Filter '*.js' -Recurse | Where-Object {
    $content = Get-Content -LiteralPath $_.FullName -Raw
    $content -match "filter:\s*['\"]?H4sI" -or $content -match '"filter"\s*:\s*"H4sI'
}
# 也搜尋 .json 檔
$jsonFiles = Get-ChildItem -Path $root -Filter '*.json' -Recurse | Where-Object {
    $content = Get-Content -LiteralPath $_.FullName -Raw
    $content -match "filter:\s*['\"]?H4sI" -or $content -match '"filter"\s*:\s*"H4sI'
}
$allFiles = $files + $jsonFiles | Select-Object -Unique

foreach ($file in $allFiles) {
    $path = $file.FullName
    $content = Get-Content -LiteralPath $path -Raw
    $b64 = $null

    if ($content -match "filter:\s*'(H4sI[^']+)'") { $b64 = $matches[1] }
    elseif ($content -match 'filter:\s*"(H4sI[^"]+)"') { $b64 = $matches[1] }
    elseif ($content -match '"filter"\s*:\s*"(H4sI[^"]+)"') { $b64 = $matches[1] }

    if (-not $b64) { continue }

    try {
        $bytes = [Convert]::FromBase64String($b64)
        $ms = New-Object System.IO.MemoryStream
        $ms.Write($bytes, 0, $bytes.Length)
        $ms.Position = 0
        $gzip = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
        $reader = New-Object System.IO.StreamReader($gzip)
        $json = $reader.ReadToEnd()
        $reader.Close(); $gzip.Close(); $ms.Close()

        if ($content -match '"filter"\s*:\s*"H4sI') {
            $newContent = $content -replace '"filter"\s*:\s*"H4sI[^"]+"', '"filter": ' + $json
        } elseif ($content -match 'filter:\s*"H4sI') {
            $newContent = $content -replace 'filter:\s*"H4sI[^"]+"', "filter: $json"
        } else {
            $newContent = $content -replace "filter:\s*'H4sI[^']+'", "filter: $json"
        }

        Set-Content -LiteralPath $path -Value $newContent -Encoding UTF8
        Write-Host "UPDATED: $($file.FullName)"
    } catch {
        $errMsg = $_.Exception.Message
        Write-Host "ERROR $($file.FullName): $errMsg"
    }
}

Write-Host "完成。"
```

執行：

```powershell
.\decode-filters.ps1
```

---

## 7. 完成後清單

執行完所有檔案後，應能確認：

- [ ] 整個專案內無任何 `filter` 欄位仍含 `H4sI`（以 `rg` 搜尋確認）
- [ ] 每個 `filter` 欄位皆為可讀 JSON 物件
- [ ] 每個 `filter_def` 與 `filter` 的索引鍵一致
- [ ] 每個檔案皆為 UTF-8 編碼，無亂碼
- [ ] 已與 `子子影视.js` / `七年影视.js` / `4k剧院.js` 等範例格式對照

---

參考來源：FongMi/CatVodSpider `docs/development.md` 與 `examples/javascript/spider.js`。