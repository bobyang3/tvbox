# getName() 遷移說明

## 問題
遷移後發現 `def getName(self):` 被移除，如何知道爬蟲的名稱？

## 答案
在 CatVodSpider 新架構中，**爬蟲名稱已從程式碼移至配置檔**。

## 舊架構（已廢棄）

```python
class Spider(BaseSpider):
    def getName(self):
        return "首页"
```

App 會呼叫 `getName()` 取得顯示名稱。

## 新架構（當前版本）

### 1. 配置檔定義名稱

```json
{
  "sites": [
    {
      "key": "4K",
      "name": "4K影視",          // ✅ 名稱在這裡
      "type": 3,
      "api": "./py/4K.py",       // 爬蟲檔案路徑
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    }
  ]
}
```

### 2. 爬蟲程式碼專注功能

```python
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    # ❌ 不需要 getName()
    
    def init(self, extend=""):
        # 初始化邏輯
        pass
    
    def homeContent(self, filter):
        # 首頁內容
        return {"class": [...]}
    
    def categoryContent(self, tid, pg, filter, extend):
        # 分類內容
        return {"list": [...]}
    
    # ... 其他功能方法
```

## 為什麼這樣改？

1. **職責分離**
   - 爬蟲：負責資料抓取
   - 配置：負責元資訊管理（名稱、圖示、語言等）

2. **多語言支援**
   - 修改顯示名稱不需要動程式碼
   - 同一個爬蟲可以有不同語言的配置

3. **統一管理**
   - 所有來源的配置在一處集中管理
   - 容易維護和更新

4. **效能優化**
   - App 不需要載入爬蟲就能知道名稱
   - 減少不必要的方法呼叫

## 實際使用範例

### config.json
```json
{
  "sites": [
    {
      "key": "movie_hunter",
      "name": "電影獵手",
      "type": 3,
      "api": "./py/电影猎手.py",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1,
      "ext": {
        "cookie": ""
      }
    },
    {
      "key": "aiguayingshi",
      "name": "愛瓜影視",
      "type": 3,
      "api": "./py/爱瓜影视.py",
      "searchable": 1,
      "quickSearch": 0,
      "filterable": 0
    }
  ]
}
```

### App 行為
1. 載入配置檔
2. 在來源列表顯示「電影獵手」、「愛瓜影視」
3. 用戶選擇來源時才載入對應的 `.py` 檔案
4. 呼叫 `homeContent()`、`categoryContent()` 等方法
5. **不會呼叫 `getName()`**

## 遷移檢查清單

- [x] 移除所有 `def getName(self):` 方法
- [x] 確認配置檔中每個 site 都有 `name` 欄位
- [x] 驗證 `name` 欄位與原 `getName()` 回傳值一致
- [x] 測試 App 能正確顯示名稱

## 參考資料

- [CatVodSpider 開發說明](https://github.com/FongMi/CatVodSpider/blob/main/docs/development.md)
- [Python 爬蟲範例](https://github.com/FongMi/CatVodSpider/blob/main/examples/python/spider.py)
- [配置檔範例](https://github.com/FongMi/CatVodSpider/blob/main/examples/config.json)

## 常見問題

**Q: 如果我想在程式碼中取得爬蟲名稱怎麼辦？**
A: 新架構不建議這樣做。如果確實需要，可以在 `init(extend)` 中解析 extend 參數傳入名稱。

**Q: 舊的配置檔案會自動遷移嗎？**
A: 不會。需要手動在配置檔中為每個來源添加 `name` 欄位。

**Q: 可以在配置檔中使用動態名稱嗎？**
A: 配置檔中的名稱是靜態的。如果需要動態顯示，可以在 `homeContent()` 回傳的分類中自訂。
