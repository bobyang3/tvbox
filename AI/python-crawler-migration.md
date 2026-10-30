# Python 爬蟲舊 API 遷移

本文件適用於本次移除舊 Python API 後的原始碼。這些異動尚未對應已發布的模組版本；實際使用需搭配包含此異動的 Python 模組與相容 App，建置方式見[開發說明](development.md#執行環境)。爬蟲仍使用 CPython 3.10，入口維持同步 `def`。

不能只看版本號或相容性標記判斷新 API 是否可用，還需確認來源與打包內容；更新模組後重啟 App 再驗證，避免繼續使用舊程序中的入口。

## AI 遷移順序

先讀[替換清單](#替換清單)、[爬蟲入口](#爬蟲入口)、[完整 ID 集合](#完整-id-集合)與[驗證](#驗證)，再依來源使用的功能閱讀其餘段落。本文件是修改規則，不代表所有使用端都已完成遷移。

1. 列出指定入口、必要 helper、配置的 ext 格式與配套 App／模組。先區分 App 爬蟲與獨立配置產生工具；後者不注入 self.net，不改造成 Spider。
2. 保存既有分類、篩選、搜尋、列表 ID、每集播放值與登入流程，確認請求的正文、編碼、Cookie、簽名及錯誤處理。
3. 依替換清單修改已移除 API，保留來源業務邏輯；不新增同名相容層，也不直接依賴 app.py 或 runtime 的內部方法。
4. 盤點包含 VOD 與直播來源，核對每個入口的參數與回傳，特別是 detailContent 的完整 ids、playerContent 的 vipFlags、proxy(params)，以及搜尋預設字串頁碼 "1"。傳入正確但使用端只讀 ids[0]，仍未完成遷移。
5. 僅在語意相同時改用 net.json、net.batch／map、Local 或 TTL 快取；保留需要 HTTP 狀態、原始正文與仍需使用的來源指定代理分支。
6. 核對 Session、reader、WebSocket、彈幕停止回呼及自建資源的釋放，不關閉共用站點 net。最後以驗證表逐項回報，未測項目明列，不以語法或單筆成功宣稱全面完成。

共用欄位與可選功能見[開發說明](development.md)與 [Python Demo](../examples/python/spider.py)。核對實作時，TV repo 的 `chaquo/src/main/python/base/spider.py` 定義基底，`chaquo/src/main/python/app.py` 負責入口轉接，`chaquo/src/main/python/runtime/net.py` 定義網路合約；這些是閱讀依據，不是爬蟲應匯入的內部 API。

## 替換清單

| 舊寫法 | 現行寫法 | 差異 |
| --- | --- | --- |
| `self.fetch()`、`self.post()` | `self.net.req()`、`self.net.json()` | 使用宿主注入的網路，不再回傳 requests.Response |
| `self.str2json()`、`self.json2str()` | `json.loads()`、`json.dumps()` | 明確 import json；入口直接回傳 dict／list |
| `getCache()`、`setCache()`、`delCache()` | `self.local` 或 `self.net` 的 TTL 快取 | 依持久化設定或限時資料選擇；這三個舊方法已在先前共享 API 改版移除 |
| 共用 `cache/py`、`SourceFileLoader` 載入 | `self.loadModule()`、`self.loadSpider()` | 方法保留，只使用站點隔離的 Runtime |
| `Runner`、`Trigger` | 繼承 `base.spider.Spider`，由 App 呼叫 | 舊轉接檔已移除，不自行包裝宿主橋接 |
| `self.getProxyUrl(False)` | `self.getProxyUrl(local=False)` | 第一個參數是代理參數集合，不再接受布林值 |
| `localProxy(param)` | `proxy(params)` | params 是代理參數 dict，不保留舊入口 |
| `getName()` | 配置中的 `name` | 宿主不呼叫此方法，刪除來源覆寫 |
| `self.html(content)` | `lxml.etree.HTML(content)` | 自行 import lxml，不再經基底轉呼叫 |
| `self.regStr(reg, src, group)` | `re.search()` 後取得群組 | 呼叫端保留找不到時回傳空字串等規則 |
| `self.removeHtmlTags(src)` | 解析 HTML 後擷取文字 | 原方法只用正則刪除標籤，與解析 HTML 的結果可能不同 |
| `self.cleanText(src)` | 來源自己的 `re` 過濾規則 | 原方法只刪除部分 Emoji 區段，沒有通用文字清理合約 |

`getDependence()`、`loadModule()`、`loadSpider()` 仍可使用。上述四個 HTML／文字工具已從基底移除，lxml 與標準庫 re 仍可直接 import。不要新增同名舊方法或捕捉 AttributeError 後改走另一套相容流程。

宿主橋接集中在 `runtime.loader`、`runtime.net`、`runtime.dialog`、`runtime.format`，取代原先的 `_tv_*` 模組名稱。Dialog 直接注入為 `self.dialog`，不再經過 `self._dialog` 與基底方法轉呼叫；可使用與 Java／JS 一致的 `self.dialog.show(options, onAction)`，原有 `self.dialog(options, onAction)` 也由同一個可呼叫物件提供。入口仍使用同步 `def`，不自動等待 coroutine。

`base` 只保留爬蟲使用的 `spider.py`。公開入口與共用 API 維持 `homeContent`、`getProxyUrl` 等既有名稱，宿主內部 helper 採 snake_case；爬蟲不直接依賴 `runtime` 或 `app.py` 的內部函式名稱。

原先注入的 `_tv_runtime` 欄位改為 `runtime`，由宿主管理載入與釋放。來源不覆寫此欄位，依賴與子爬蟲仍透過 `loadModule()`／`loadSpider()` 使用。

## 爬蟲入口

入口類別維持 `from base.spider import Spider as BaseSpider` 與 `class Spider(BaseSpider)`，需要初始化時實作同步 `init(self, extend="")`，由 App 注入資源後呼叫；省略時使用基底的空實作。匯出必須是 Spider 子類別，不能直接匯出基底、函式或實例。不要自行建立另一份 BaseSpider 或把入口改成 async def。

以下參數均省略 self；公開名稱維持原有 camelCase，自訂 helper 使用 snake_case，私有 helper 可保留前置底線。

| 入口 | 參數與回傳 |
| --- | --- |
| `init(extend="")` | extend 是來源設定字串，需要 JSON 時由來源解析；回傳 None |
| `homeContent(filter)` | filter 是 bool；回傳含 class、可選 filters 的 dict |
| `homeVideoContent()` | 回傳含 list 的 dict |
| `categoryContent(tid, pg, filter, extend)` | pg 保留呼叫值，extend 是篩選 dict；回傳當頁 list 與分頁欄位 |
| `detailContent(ids)` | ids 是完整 ID list；回傳含完整詳情 list 的 dict |
| `searchContent(key, quick, pg="1")` | quick 是 bool；雙參數呼叫預設 pg="1"，回傳當頁 list 與分頁欄位 |
| `playerContent(flag, id, vipFlags)` | id 是每集播放值，vipFlags 是完整 list，含空 list；回傳播放 dict |
| `liveContent(url)` | 回傳直播 dict／list，或原有 TXT／M3U 字串 |
| `proxy(params)` | params 是扁平的字串鍵值 dict；回傳 `[status, mime, body, headers]`，正文與標頭見[代理網址](#代理網址) |
| `manualVideoCheck()`、`isVideoFormat(url)` | 回傳 bool，不回傳 JSON 字串 |
| `action(action)` | action 是操作字串；回傳操作結果 dict／list |
| `danmaku(id, emit)` | 用 emit(item) 發送資料，回傳可呼叫的停止函式；不回傳 coroutine |
| `destroy()` | 釋放自行建立的資源；回傳 None |

init 的 extend 字串與 categoryContent 的 extend dict 是不同參數，不要一律 json.loads。只實作來源支援的功能，不為對齊名稱硬補 VOD、登入或彈幕。基底預設首頁回傳 `{"class": []}`，列表入口回傳 `{"list": []}`，播放／操作回傳 `{}`，直播回傳空字串，proxy 回傳 `[404, "text/plain", ""]`；刪除冗餘覆寫前，先確認這些預設值保留原行為。

App 爬蟲測試頁也使用完整入口名稱，參數以 JSON 陣列按上表順序提供；搜尋省略 pg 時使用 "1"。布林值使用 true／false，分類 extend 與 proxy params 的值使用字串。

## 網路請求

`self.net` 在 `init()` 前由 App 注入。請求使用 options 字典，時間單位為毫秒。

| 原 requests 用法 | 遷移方式 |
| --- | --- |
| `response.json()` | 直接使用 `self.net.json(url, options)` |
| `response.text` | `self.net.req(url, options)["content"]`，先檢查 error 與 code |
| `response.content` | options 設 `buffer: 3`，成功回應的 content 為 bytes |
| `response.status_code` | `response["code"]`；網路錯誤先檢查 error |
| `response.headers` | `response["headers"]`；重複 header 的值可能為陣列 |
| `params={...}` | options 的 `params`；保留既有 query，字典值可用陣列傳送同名參數，None 會略過 |
| `timeout=5` | `timeout: 5000`；整次請求期限另用 `callTimeout` |
| `allow_redirects=False` | `redirect: 0`；預設跟隨重新導向 |
| `cookies={...}`、requests.Session | 使用 Cookie API 或 `self.net.session()` |
| `stream=True` | `self.net.openStream()`；以 with／finally 關閉 reader |
| `verify=False` | 沒有同名 options；TLS 行為由宿主網路層決定，不原樣搬入此參數 |

新 `timeout` 預設為 10000 毫秒，與舊 fetch／post 的 5 秒不同。需要維持舊期限時明確傳 5000；`timeout` 管理連線／讀寫，`callTimeout` 管理整次請求。

### GET 與 JSON

只需要 JSON 時直接取得解析結果。網路失敗、HTTP 非 2xx 或無效 JSON 會拋出例外，不再額外呼叫 `.json()` 或 `json.loads()`。

```python
data = self.net.json(url, {
    "params": {"keyword": key, "page": pg},
    "headers": headers,
    "timeout": 5000,
})
```

需要狀態碼、錯誤正文或文字時使用 req。HTTP 非 2xx 仍保留回應；不要把登入頁或錯誤偽裝成成功空列表。

例如需區分 403 的會員限制，或正文還需解密時，保留 req 與來源自己的解析流程。req 後使用 json.loads 本身不是過時寫法，不能只因回應是 JSON 就機械替換成 net.json。

```python
response = self.net.req(url, {"headers": headers, "timeout": 5000})
if response.get("error"):
    raise RuntimeError(response["error"])
if not 200 <= response["code"] < 300:
    raise RuntimeError(f"HTTP {response['code']}")
text = response["content"]
```

req 預設回傳文字，編碼依 HTTP 回應處理，不再由基底強制指定 UTF-8。需要自行解碼時使用 `buffer: 3`，檢查成功後對 bytes 呼叫 `decode()`。

### POST 與正文

舊 `post(data={...})` 通常送出表單，新網路 API 的 `postType` 預設為 json。遷移表單時必須明確指定 form。

```python
data = self.net.json(url, {
    "method": "POST",
    "postType": "form",
    "data": {"name": name, "page": pg},
    "headers": headers,
    "timeout": 5000,
})
```

| 正文格式 | options |
| --- | --- |
| JSON 值 | `method: "POST", postType: "json", data: value` |
| 表單 | `method: "POST", postType: "form", data: {...}` |
| multipart 文字欄位 | `method: "POST", postType: "form-data", data: {...}` |
| 已編碼文字 | `method: "POST", body: text`，並提供 Content-Type |
| 原始 bytes | `method: "POST", body: list(payload)`，並提供 Content-Type |

`data` 與 `body` 互斥；GET／HEAD 不接受正文。form／form-data 的 data 必須是物件，欄位經共用網路層轉字串並去除前後空白。需要重複表單欄位或精確保留文字時，自行編碼後以 body 傳送；form-data 此處只提供文字欄位，不對應 requests 的 files 參數。

```python
response = self.net.req(url, {
    "method": "POST",
    "headers": {"Content-Type": "application/octet-stream"},
    "body": list(payload),
    "buffer": 3,
})
```

`buffer` 只控制回應格式；原始二進位正文仍須轉成 0～255 整數陣列。req 的網路與 HTTP 錯誤檢查方式與 GET 相同。

### Cookie、Session 與生命週期

`self.net.getCookie(url)`／`setCookie(url, cookie)` 讀寫 WebView Cookie，寫入接受單筆 Set-Cookie 格式；請求設 `cookie: True` 才會自動帶入與更新。App 的 User-Agent 可由 `self.net.getUserAgent()` 取得，再按來源需要放入 headers，不會自動套用到所有請求。

需要隔離 Cookie 時建立 Session，請求會自動使用該 Session 的 Cookie，並在結束時關閉。

```python
with self.net.session() as session:
    session.json(login_url, {
        "method": "POST",
        "postType": "form",
        "data": credentials,
    })
    data = session.json(data_url)
```

Session 關閉只釋放自己的請求、Cookie 與快取，不關閉父站點。站點的 self.net 由 App 管理；子爬蟲不要自行關閉共用 self.net。串流以 `reader.read(size)` 取得 bytes，結束時回傳 None，reader 也須以 with／finally 關閉。

共用 net 目前沒有逐次請求指定外連代理的 options。來源仍需要時，不能直接刪除既有 requests 分支，或把 proxies 塞進 options 當成已遷移；保留其設定、錯誤與 Session 釋放，並列出尚未由共用 API 涵蓋的能力。使用者明確取消此功能時，可刪除對應設定、請求分支與資源清理，不再保留空殼。既有登入 Cookie／token 也不能在遷移時改為訪客流程。

## Local 與 TTL 快取

小型持久化設定使用 Local，Python 直接存 JSON 值，不先序列化成字串。

```python
self.local.set("preferences", {"category": "movie", "page": 1})
preferences = self.local.get("preferences", {})
self.local.delete("preferences")
```

Local 按 Site.key 隔離；不存在時回傳 None，或 get 的第二參數。set／delete 回傳 None，呼叫時的例外會向外傳遞，不能再比較舊的 `"succeed"`／`"failed"`。App 清快取不會刪除 Local，改 Site.key 後也不會自動沿用原站點資料。

舊 `/cache` 與 Local 是不同資料空間，不會自動搬移。Local 不解析 `expiresAt`，即使欄位時間已過仍原樣回傳；不要直接搬入舊資料並假定具有過期判斷。重要設定需由來源明確處理遷移或透過配置重新提供，不加入全域舊快取 fallback。

需要期限的資料使用 cached，由 loader 產生 JSON 值。

```python
catalog = self.net.cached(
    "catalog",
    {"ttl": 60000, "stale": False},
    lambda: self.net.json(catalog_url),
)
```

- ttl 為必填毫秒數；0 不快取。stale 預設 True，可能先回過期值再背景更新；需要等待新資料時設 False。
- persist 預設 False；只為可公開持久化的資料啟用，Session 不支援 persist。Cookie、token、簽名播放網址不寫入長期 Local 或持久快取。
- `self.net.peek(key)` 可讀到過期值，不能拿來取代有效期判斷。`self.net.clearCache(key)` 清單筆，省略 key 清整個站點快取。
- cached 不是 setCache 的同參數替代；儲存設定用 Local，限時資料才交給 loader 與 TTL。

## 依賴與子爬蟲

保留 loadModule 回傳的模組物件，不再載入後用 `importlib.import_module("helper")` 找全域同名模組，也不手動修改 sys.path、sys.modules 或共用 cache/py。

```python
def init(self, extend=""):
    self.helper = self.loadModule("helper")
    self.child = self.loadSpider("child")
    self.child.init(extend)
```

loadModule／loadSpider 的名稱相對於入口爬蟲來源解析，模組與檔案快取按站點、來源及載入世代隔離。loadSpider 不會自動呼叫子爬蟲 init；在父爬蟲 init 中載入時，子爬蟲共用目前站點的 net、local、js 與 Dialog，不建立另一份站點資源。

使用 `self.js.eval()` 仍需配套的 App 與 QuickJS 模組，Python 模組本身不另建 JavaScript 引擎。

getDependence 仍可宣告依賴。若使用一般 import 且名稱可能與全域模組碰撞，在 getDependence 宣告後於 init 中 import，或直接採用 loadModule。

```python
def getDependence(self):
    return ["helper"]

def init(self, extend=""):
    import helper
    self.helper = helper
```

不要直接建構脫離 App Runtime 的爬蟲，再期待 loadModule／loadSpider 從舊共用目錄載入。Runner／Trigger 不再使用；以 `from base.spider import Spider as BaseSpider` 匯入基底並定義 `class Spider(BaseSpider)`，由 App 完成載入、注入、呼叫與釋放。

## JSON 與入口回傳

只在解析正文或建立指定格式的請求時使用標準庫 JSON。

```python
import json

data = json.loads(text)
body = json.dumps(data, ensure_ascii=False)
```

首頁、分類、搜尋、詳情與播放結果直接回傳 dict／list，由 app.py 的 encode_json 統一序列化，不回傳額外 json.dumps 後的字串。原先 app.py 內部的 str2json／json2str 也已移除或重新命名；呼叫端使用標準庫 json，不依賴宿主內部 helper。

布林接口仍回傳 bool，proxy 回傳 `[status, mime, body, headers]`；直播文字格式也維持原有合約，不套用一般資料入口的 JSON 包裝。

資料結果、Local 與 TTL loader 的值必須可序列化為 JSON，NaN／Infinity、set、自訂物件與一般 bytes 不能直接放入；bytes 使用[代理正文合約](#代理網址)。影音判斷必須回傳 bool，不能使用 0／1 或字串代替。入口及彈幕停止函式若回傳 awaitable，宿主會報錯，不會自動執行 asyncio。

### 完整 ID 集合

舊實作若只處理 ids[0]，先把單筆解析搬到 `_detail(self, video_id)`，把其中對 ids[0] 的使用換成 video_id，並保留既有請求、簽名、快取、線路、集數與附加欄位。helper 回傳含 list 的 dict，再由入口合併：

```python
def detailContent(self, ids):
    if not ids:
        return {"list": []}
    responses = [self._detail(video_id) for video_id in ids]
    return {**responses[0], "list": [item for response in responses for item in response["list"]]}
```

保留輸入順序，不自行去重；空集合不發請求，單筆錯誤向外傳遞，不捕捉後略過該 ID。範例沿用第一筆的頂層欄位；有批次訊息或其他來源語意時明確處理，不只取 list 而丟失必要欄位。原 API 若直接支援批次 ID，優先使用其批次接口。

來源原本以空 list 與 msg 回報錯誤時，可在整個批次外層保留這個錯誤格式，失敗時不交付已累積的部分結果。未上架或沒有免費集數等合法空結果可與其他詳情合併，但須保留各筆提示，不能只沿用第一筆的 msg。

預設依序處理。各筆解析確定不修改共用登入、Session 或暫存狀態時，才改用 `self.net.map(ids, lambda video_id, index: self._detail(video_id), 4)`；mapper 接收 item、index 兩個參數。固定請求可用 net.batch，每筆仍需檢查 error 與 code。不以無上限執行緒或 asyncio 取代此合約。

## HTML 與文字處理

HTML 解析直接使用 lxml，並處理空內容無法建立樹的情況。

```python
from lxml import etree

html_text = "<div>你好 &amp; <b>世界</b></div>"
root = etree.HTML(html_text)
plain_text = "" if root is None else "".join(root.itertext())
```

這也可取代需要擷取文字的 removeHtmlTags 用法。解析器會處理 `&amp;` 等實體，與原本 `re.sub('<.*?>', '', src)` 的結果不完全相同；script／style 內容與段落空白需按來源需求處理。

正則擷取由來源明確指定群組及無匹配結果，以下保留舊 regStr 找不到時回傳空字串的行為。

```python
import re

source = "ID:123"
match = re.search(r"ID:(\d+)", source)
value = match.group(1) if match else ""
```

cleanText 的過濾範圍由來源決定。確實需要原有行為時，可直接使用以下明確規則；它只涵蓋舊方法的四段 Unicode 範圍，不是完整的 Emoji 過濾。

```python
import re

title = "電影😀"
pattern = re.compile('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
title = pattern.sub("", title)
```

## 代理網址

`proxy(params)` 是播放器等呼叫端使用的 App 本地 HTTP 入口，與外連 HTTP／SOCKS 代理是不同能力。來源沒有本地代理功能時可省略覆寫，使用基底 404；不保留只回傳 proxy ok 的空殼。

第一個參數傳入業務參數集合，是否使用本機位址以 local 指定。

```python
local_url = self.getProxyUrl({"id": "a+b &=中文"})
lan_url = self.getProxyUrl({"id": "a+b &=中文"}, local=False)
lan_base = self.getProxyUrl(local=False)
```

App 自動加入 do／siteKey 並編碼 query；呼叫端不能覆寫這兩個保留參數，也不要再手動附加站點識別或重複編碼。舊的 `getProxyUrl(False)`／`getProxyUrl(True)` 會失敗。

proxy 收到的 params 是扁平的字串鍵值 dict，依序合併請求參數、HTTP 標頭與檔案資訊，後者覆寫同名欄位；也包含 do／siteKey。依來源讀取 params.get("url")、params.get("id") 等欄位即可。HTTP 層已解碼網址參數，不再重複 unquote。

回傳 `[status, mime, body, headers]`，headers 可省略，值可為字串或字串陣列，多值以 `, ` 合併，無效型別會拋錯。文字正文使用 UTF-8；二進位可直接回傳 bytes，例如放在 proxy 方法內：

```python
return [200, "application/octet-stream", b"\x00\x7f\x80\xff", {"Cache-Control": "no-store"}]
```

既有 Base64 字串正文可保留第五格 1，包含 Base64 data URL；串流不能加上此旗標。原樣轉送網址可使用共用 stream：

```python
def proxy(self, params):
    response = self.net.stream(params["url"], {"timeout": 15000, "callTimeout": 15000})
    return [response["code"], response["contentType"], response["stream"], response["headers"]]
```

成功交付後由 App 關閉 stream，不在回傳前關閉；未交付時自行 close。自行讀取使用 `self.net.openStream()` 與 with／finally，產生器正文使用 `self.net.stream(generator())` 並 yield bytes。完整限制見[串流讀取與代理](development.md#串流讀取與代理)。

## 驗證

先逐一盤點入口與必要依賴中的 fetch／post、str2json／json2str、舊 Cache API、html／regStr／removeHtmlTags／cleanText、Runner／Trigger、_tv_*、SourceFileLoader 與手動 sys.path 修改。搜尋命中只是定位，必須閱讀所屬函式；正常的 json.loads、私有 helper 底線及保留 API 不列為失敗。

| 檢查 | 通過條件 |
| --- | --- |
| 語法與載入 | Python 3.10 下 py_compile 通過，配套 App 可載入、注入與 init；入口沒有 coroutine |
| 詳情集合 | 測 `[]`、`["a"]`、`["a", "b"]`、重複 ID 及單筆失敗；核對順序、完整欄位與錯誤傳遞 |
| 參數 | 測雙參數搜尋與顯式頁碼、空／多筆 vipFlags、分類 extend dict；不可只檢查參數個數 |
| 列表與播放 | 分類／搜尋兩頁、尾頁、無結果及篩選正確；逐一接通列表 ID → 詳情 → 每集播放值 → 播放結果 |
| HTTP 與登入 | 表單／JSON／原始 bytes、毫秒期限、非 2xx、登入頁與格式錯誤符合來源規則，不變成成功空列表 |
| 資源與隔離 | 實際使用的 Cookie、Session、Local／TTL、依賴、Dialog、proxy 與停止／destroy 流程保留隔離及釋放 |
| 代理 | 測扁平字串 params、URL 往返、headers 的字串／多值／無效型別、非 ASCII 文字與二進位；串流交接後由 App 關閉 |

完整清單才使用 self.page；外站已分頁就保留當頁，不再切片，有精確總筆數才填 total。App、Python 模組與來源須配套；主機適配器通過不代表 Android 注入、快取或取消已通過。

完成回報列出已修改檔案、保留分支及原因、實際執行的檢查與未測項目。分開說明語法、App 載入、取樣詳情／播放網址及實際裝置播放；沒有檢查所有適用入口與必要依賴，不宣稱每個爬蟲都已全面遷移。
