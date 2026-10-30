# JavaScript 爬蟲舊 API 遷移

本文件適用於本次 QuickJS 爬蟲 API 清理後的原始碼，尚未對應已發布的模組版本；實際使用需搭配包含此異動的 QuickJS 模組與相容 App；wrapper Java 與 JNI 必須來自相同來源，舊 JNI 不能搭配新增的物件綁定 API。建置方式見[開發說明](development.md#執行環境)。

不能只看版本號或相容性標記判斷新 API 是否可用，還需確認來源與打包內容；更新模組後重啟 App 再驗證，避免繼續使用舊程序中的入口。

清理依據是重複入口、隱含行為與舊協定的維護成本。方法較舊、名稱較短或標準 API 能完成類似工作，都不足以單獨構成移除理由。

## AI 遷移順序

先讀[替換清單](#替換清單)、[爬蟲入口](#爬蟲入口)、[完整 ID 集合](#完整-id-集合)與[驗證](#驗證)，再依來源使用的功能閱讀其餘段落。本文件是修改規則，不代表所有使用端都已完成遷移。

1. 盤點 VOD 與直播來源的指定入口、必要 helper、配置的 ext 格式與配套 App／wrapper／runtime；區分 QuickJS 爬蟲與 Node.js 工具，不把 require、process、Buffer 或 DOM 當成宿主能力。
2. 保存既有分類、篩選、搜尋、列表 ID、每集播放值與登入流程，確認請求的正文、編碼、Cookie、簽名及錯誤處理。
3. 改為 default Spider 子類別與公開 catvod API，同步修改 helper 的 imports 及 vendor 路徑；不匯入 catvod:host 或自行重建 ctx.bind 橋接。
4. 沿呼叫鏈處理 Promise，核對完整 ids／vipFlags、搜尋頁碼與分類 extend。不能只加 async 或只改方法名稱；詳情只處理 ids[0] 仍未完成遷移。
5. 依語意選 net.json／req、batch／map、Local／TTL；代理的 URL 產生端、接收參數與回傳格式一起修改，不更動來源的簽名、登入與字元編碼規則。
6. 核對 Session、reader、WebSocket、彈幕停止回呼及 destroy 的資源釋放，再依驗證表逐項回報；Node.js 語法或單筆成功不代表全部入口與 Android 已通過。

共用欄位與可選功能見[開發說明](development.md)與 [QuickJS Demo](../examples/javascript/spider.js)。核對實作時，TV repo 的 `quickjs/src/main/assets/js/lib/catvod.js` 定義公開 SDK，`quickjs/src/main/assets/js/lib/net.js` 定義網路合約，`quickjs/src/main/java/com/fongmi/quickjs/crawler/Spider.java` 負責入口轉接；爬蟲仍只使用公開 API。

## 替換清單

| 舊寫法 | 現行寫法 | 移除原因與差異 |
| --- | --- | --- |
| 全域 `req/http/ws/connect` | `this.net.req/ws/connect` 或明確匯入 `net` | 網路能力由 Spider 資源及模組提供 |
| 全域 `session/sleep/cached/clearCache` | `this.net.session/sleep/cached/clearCache` | 移除與 net 重複的入口 |
| 全域 `getCookie/setCookie/getUserAgent` | `this.net.getCookie/setCookie/getUserAgent` | 根網路仍使用 App 的登入資訊與 UA；子 session 保持隔離 |
| 同步 `net.req()`、`net.http()` | `await this.net.req(url, options)` | HTTP 統一回傳 Promise；子 session 與 batch 同樣使用 req，不保留 http 別名 |
| `http/ws(url, {async, complete})` | `await this.net.req/ws(url, options)` | 一次請求只使用 Promise，不以 options 改變交付方式 |
| `evalJs(source, options)` | `await this.js.eval(source, options)` | 保留受管理的腳本執行 |
| `global/window/self` 別名 | `globalThis` | 使用標準全域物件名稱；QuickJS 爬蟲並未因此提供 DOM |
| `__jsEvalReturn()`、`__JS_SPIDER__`、default 物件／factory | `export default class extends Spider` | 統一為與 Java／Python 相近的類別入口 |
| `dialog(options, onAction)` | `await this.dialog(options, onAction)` | callback 為第二個參數，不放在 options 內；options 只保留可序列化資料 |
| `js2Proxy()` 與 `from=catvod` 代理協定 | `this.proxyUrl(params)` 與 `proxy(params)` | 移除另一套參數、回傳格式和 Res 轉接；URL 產生端與 proxy 必須一起修改 |
| 直接呼叫全域 `proxyUrl(params)` | `this.proxyUrl(params)` | 爬蟲使用 Spider 類別實例的代理網址產生方法 |

`async` 與 `complete` 不再是 `net.req/ws` 的有效 options；傳入時會取得含 error 的失敗結果。不要只改函式名稱而保留這兩個欄位。`net.connect(url, options, listener)` 的 listener 用於持續 WebSocket 事件，仍保留。

公開 API 從 `catvod` 模組匯入。`hostReq`、`hostHttp` 等橋接不再註冊為全域函式；底層函式綁定在原生物件，由內部 `catvod:host` 模組持有。爬蟲派送與 Dialog callback 也由宿主持有引用，不公開 spider／dialogActions 全域物件。session 路由欄位 netId 仍由宿主管理。

## 網路請求

JS 使用 `await this.net.req`，不再提供同步 HTTP。方法名稱與 Java／Python 對齊；JS 的 Promise 交付方式仍保留語言本身的非同步模型。時間單位為毫秒。輔助模組也可從 `catvod` 明確匯入 `net` 再使用 `net.req`，但爬蟲主體一律經由 `this.net` 取得站點資源。

```javascript
const response = await this.net.req(url, {
    params: {keyword: key, page: pg},
    headers,
    timeout: 5000
});
if (response.error) throw new Error(response.error);
if (response.code < 200 || response.code >= 300) throw new Error(`HTTP ${response.code}`);
const text = response.content;
```

呼叫端必須等待 Promise，不能直接讀取 `this.net.req(...).content`。HTTP 非 2xx 仍保留回應，網路失敗則帶有 error；不要把登入頁或錯誤正文當成成功列表。

只需要 JSON 時使用 `const data = await this.net.json(url, options)`；網路失敗、HTTP 非 2xx 或無效 JSON 會拋出例外。一般請求預設回傳文字，`buffer: 3` 回傳 ArrayBuffer，可交給 Uint8Array、TextDecoder 或代理。

需要區分 403 的會員限制、保留大整數 ID，或正文還需解密時，保留 req 與來源自己的解析流程。req 後使用 JSON.parse 本身不是過時寫法，不把 HTTP 錯誤或解析失敗改成成功空列表，也不把已登入流程改為訪客請求。

| 請求情況 | 現行寫法與注意事項 |
| --- | --- |
| URL query | options.params，保留來源既有編碼及同名參數，不手動重複編碼 |
| 表單 | `{method: "POST", postType: "form", data: fields}`；postType 預設 json，不能只搬 data |
| JSON | `{method: "POST", postType: "json", data: value}`；data 與 body 擇一 |
| 原始正文 | `{method: "POST", body: text, headers: {"Content-Type": mime}}`；二進位 body 用 0～255 整數陣列 |
| 二進位回應 | `await this.net.req(url, {buffer: 3})`，檢查 error／code 後使用 content |
| 持續 WebSocket | `this.net.connect(url, options, listener)`；listener 處理事件，不是舊 complete callback |
| 單次 WebSocket 交換 | `await this.net.ws(url, options)`；成功回傳 code＝101，首個完整訊息在 content 後關閉 |
| 每筆有解析或簽名 | `await this.net.map(items, mapper, 4)`；mapper 接收 item、index，保留輸入順序 |
| 固定 HTTP 批次 | `await this.net.batch(requests, 4)`；每筆是 `{url, options}`，逐一檢查結果 |

GET／HEAD 不傳正文。buffer 只控制回應，不會把 JSON data 中的 Uint8Array 變成原始二進位正文。共用 net 沒有逐次請求指定外連代理的 options；來源仍需要時保留其能力並列明缺口，不傳入未支援的 proxy／proxies 欄位當成已完成。使用者明確取消此功能時，可刪除對應設定、請求分支與資源清理，不再保留空殼。

根網路的 Cookie API 仍對應 App 登入資訊。需要獨立 Cookie 與生命週期時建立子 session，使用完成後關閉。

```javascript
const client = this.net.session();
try {
    const data = await client.json(url, {headers});
    return {list: data.list};
} finally {
    client.close();
}
```

## 爬蟲入口

以下範例的 ext 是包含 url、detailUrl 的 JSON 設定字串，由來源解析；網址或其他字串設定則保留各自的解析流程。

```javascript
import {Spider} from "catvod";

export default class Source extends Spider {
    async init(extend) {
        this.config = JSON.parse(extend);
    }

    async homeContent(filter) {
        const data = await this.net.json(this.config.url);
        return {class: data.categories};
    }

    async detailContent(ids) {
        const list = await this.net.map(ids, async id => {
            const data = await this.net.json(this.config.detailUrl + encodeURIComponent(id));
            return {vod_id: id, vod_name: data.name};
        });
        return {list};
    }
}
```

只接受繼承 `Spider` 的 default class。constructor 保持同步；網路與其他非同步初始化放在 `async init(extend)`。站點鍵由 `this.siteKey` 提供，資源使用 `this.net/local/js/dialog`；輔助模組可從 `catvod` 明確匯入相同資源或便利函式。

| 舊方法 | 現行方法與參數 |
| --- | --- |
| `home(filter)` | `homeContent(filter)` |
| `homeVod()` | `homeVideoContent()` |
| `category(tid, pg, filter, extend)` | `categoryContent(tid, pg, filter, extend)` |
| `detail(id)` | `detailContent(ids)`，收到完整 ID 陣列 |
| `search(key, quick, pg)` | `searchContent(key, quick, pg = "1")` |
| `play(flag, id, flags)` | `playerContent(flag, id, vipFlags)` |
| `live(url)` | `liveContent(url)` |
| `sniffer()` | `manualVideoCheck()` |
| `isVideo(url)` | `isVideoFormat(url)` |

其餘公開入口為 `action(action)`、`proxy(params)`、`danmaku(id, emit)` 與 `destroy()`。action 回傳操作結果，proxy 回傳下節的代理陣列，danmaku 回傳停止函式；它們不是另一組需要改名的舊別名。

搜尋的雙參數入口會由宿主補上字串頁碼 `"1"`，與 Python adapter 一致；顯式傳入的頁碼保持原值。detailContent 收到完整陣列，playerContent 的 vipFlags 也保留完整陣列，空陣列不會省略。categoryContent 的 extend 是物件，參數順序與 Java／Python 相同。

已宣告的入口參數沿用表中的 key、pg、id、vipFlags、action、params，避免同義名稱混用。JS 方法可省略未使用的參數，宿主仍按完整合約傳入；不為對齊宣告而新增未使用參數，也不把同步值一律改成 async。

App 爬蟲測試頁使用相同的完整入口名稱，參數以 JSON 陣列提供。布林值使用 true／false，分類 extend 與 proxy params 使用字串鍵值物件；參數數量與型別須符合入口。

Python 入口目前使用同步 def，Java Spider 入口同步回傳 String／boolean／Object[]；它們沒有自動等待 coroutine 或 Future 的入口協定。JS 的派送層統一 await 同步值、Promise 與 thenable，再依入口交付資料字串、代理陣列或布林值。非同步模型依語言保留，對齊的是方法名稱、參數及完成後的資料語意。

三語言的代理入口統一為 proxy(params)。Dialog 都提供 dialog.show(options, onAction)，Python 寫作 self.dialog.show(options, onAction)，也保留可呼叫物件的 self.dialog(options, onAction) 用法。Java init 額外接受 Android Context，JS／Python 的 init 只接收來源設定。

init、上述入口、action、proxy、destroy 均可宣告 async 或回傳 Promise，宿主會等待結果。danmaku 可非同步取得停止函式，停止函式本身也可回傳 Promise。這不會讓同步 CPU 計算自動平行執行；呼叫取消與期限仍由 Invocation 管理，constructor 和模組評估也受期限約束。

init 原樣收到設定中的 ext 字串，需要 JSON 時由來源呼叫 JSON.parse，不額外包成 `{stype, skey, ext}`；categoryContent 的 extend 仍是篩選物件。類別方法會綁定所屬實例，可將 `this.method` 直接交給 map 或事件 callback，並保留相同函式引用；方法內另宣告的一般函式仍遵循 JS 的 this 規則。

資料入口可直接回傳物件或陣列，由宿主序列化。既有 JSON 字串與 live 的 TXT／M3U 字串仍原樣傳遞；proxy 的原生陣列、manualVideoCheck／isVideoFormat 的布林值不走資料序列化。批次詳情的內部項目方法應回傳物件，合併各 list 後交給宿主序列化。

物件／陣列、Local 與 TTL loader 的資料必須可序列化為 JSON；不要放入 undefined、函式、Symbol、BigInt、Map、Set、NaN 或 Infinity。二進位依用途明確轉成 JSON 陣列，或使用 proxy 正文合約，不直接把 ArrayBuffer 當成一般 JSON 資料。大型 ID 依來源規則保留字串，避免先轉 Number 而遺失精度。影音判斷必須回傳 boolean，不能使用 0／1 或字串代替。

Dialog 使用 `await this.dialog(options, onAction)`；第二個參數可省略。callback 收到 `{button, values}`，可回傳更新物件或 Promise；最終回傳仍是 `{button, values}` 或取消時的 null。不可將 onAction 放回 options。輸入等待只暫停已讓出執行權的呼叫期限，未 await 的 Dialog 不會停用正在執行 JS 的期限。

不再改寫來源中的 `__JS_SPIDER__` 字串，也不會依舊入口改變 req 的語意。

### 完整 ID 集合

把舊 detail(id) 的單筆請求與解析搬到 `async detailItem(id)`，保留簽名、快取、線路、集數及附加欄位，回傳含 list 的物件。入口處理完整集合：

```javascript
async detailContent(ids) {
    if (!ids.length) return {list: []};
    const responses = await this.net.map(ids, this.detailItem, 4);
    return {...responses[0], list: responses.flatMap(response => response.list)};
}
```

保留輸入順序，不自行去重；空集合不發請求。單筆失敗讓整次呼叫 reject，不捕捉後略過該 ID。範例沿用第一筆的頂層欄位；若來源有批次訊息語意，明確合併必要欄位，不只取 list 而丟失資訊。原 API 若直接支援批次 ID，優先使用其批次接口。

來源原本以空 list 與 msg 回報錯誤時，保留這個錯誤格式並讓整個批次失敗，不交付成功的部分當成完整結果。未上架或沒有可播放內容等合法空結果可與其他詳情合併，但須保留各筆提示，不能只沿用第一筆的 msg。

需要共用登入或依序變更狀態時，以 for...of 逐筆 await，再合併結果。不要用未等待的 forEach(async ...) 或把 ids.map(async ...) 的 Promise 陣列直接放進 list，也不以無上限 Promise.all 取代既有並行限制。

### 非同步與生命週期

純資料組裝保留同步方法；呼叫 net.req／json、js.eval、dialog.show 或其他 Promise 時，await 或直接 return 該 Promise，並一路修改必要呼叫端。不得在同步 constructor 發出未受等待的初始化請求。

只實作來源支援的功能。Spider 預設首頁回傳 `{class: []}`，列表入口回傳 `{list: []}`，播放／操作回傳 `{}`，直播回傳空字串，proxy 回傳 `[404, 'text/plain', '']`，init 可省略；刪除冗餘覆寫前先確認原行為。destroy hook 含 Promise 有 5 秒期限，呼叫前網路工作已取消；只釋放自行建立的 Session、reader、連線、計時器或回呼引用，不在 destroy 安排新請求，不關閉共用站點 net。proxy 成功交付的 stream 由 App 接管，不能先關閉再回傳。

## 代理

`proxy(params)` 是播放器等呼叫端使用的 App 本地 HTTP 入口，與外連 HTTP／SOCKS 代理是不同能力；移除不再使用的外連代理，不代表應刪除仍有用途的本地轉送。來源沒有本地代理功能時可省略覆寫，使用基底 404。

URL 產生端使用業務參數，不自行組合 do 或 siteKey。

```javascript
const url = this.proxyUrl({url: mediaUrl});
const lanUrl = this.proxyUrl({url: mediaUrl}, false);
```

proxyUrl 的第一個參數是業務參數物件，第二個參數 local 預設 true；傳 false 產生區域網路 URL。App 自動加入 do／siteKey 並編碼 query，拒絕覆寫這兩個保留參數；不要再手動附加或重複編碼。getPort 與 getProxy 仍可取得連接埠及基礎 URL（Java／Python 則使用 `getProxyUrl`）。

proxy 收到一個扁平的字串鍵值物件 params，依序合併請求參數、HTTP 標頭、檔案資訊，後者覆寫同名欄位；也包含 do／siteKey 路由欄位。依來源讀取 params.url、params.id 等欄位，網址參數已由 HTTP 層解碼，不重複 decodeURIComponent。回傳 `[狀態碼, MIME, body, headers]`，headers 可省略。舊 js2Proxy 使用的路徑片段與 header 分離參數，以及回傳 JSON 字串 `{code, buffer, content, headers}` 的格式，均需改成此合約。

回應 headers 的值使用字串或字串陣列，多值以 `, ` 合併；一般與串流回應都保留字串內容，無效型別會回報錯誤，不再轉成空字串。

proxy2 的具名欄位比位置陣列容易閱讀，對既有爬蟲也有相容價值。未選它作為統一介面，是基於原實作的限制：

- 回傳固定先經 JSON 字串與 Res 解析，content 是字串，二進位使用 buffer: 2 的 Base64，無法直接交付 Uint8Array／ArrayBuffer。
- 原呼叫使用一般 Invocation，沒有現行代理的 stream handle 交接與所有權流程。
- Res 雖可解析 headers，proxy2 最後只交出狀態碼、MIME 與 body 三格；HTTP server 因此沒有收到其他回應 headers。

這些限制可以修正，具名物件本身也不是過時格式。本次沿用已有二進位與串流支援的陣列合約，避免同時新增另一套公開回傳 API；不代表已證明所有外部爬蟲都不再使用 proxy2。

```javascript
async proxy(params) {
    const result = await this.net.stream(params.url);
    return [result.code, result.contentType, result.stream, result.headers];
}
```

此方法放在 default 匯出的 Spider 子類別中。`stream` 交出後由 App 接管所有權；自行讀取串流時改用 `this.net.openStream`，並在 finally 關閉 reader。

非串流 body 可為字串、Uint8Array 或 ArrayBuffer。二進位資料直接傳遞，避免先編碼再解碼；字串使用 UTF-8。

```javascript
return [200, "application/octet-stream", new Uint8Array([0, 127, 128, 255])];
```

第五格值為 1 的 Base64 body 選項仍保留，包含原先支援的 Base64 data URL。來源已是 Base64 時可以繼續使用；串流不能加上此旗標。本次只移除舊 catvod 代理協定，沒有把所有編碼便利功能一起刪除。

## 保留的便利方法與函式庫

| 保留項目 | 保留原因 |
| --- | --- |
| `sha256X(text)` | 同步回傳 SHA-256 hex；WebCrypto digest 是 Promise 與 ArrayBuffer，並非相同呼叫合約 |
| `randomX(size)` | 直接回傳 URL-safe、無 padding 的隨機字串，size 是位元組數；有效範圍為 1..1024，超出範圍仍回傳空字串 |
| `joinUrl(parent, child)` | 保留原 URI 解析語意，避免為改成 new URL 而改變既有來源行為 |
| `getPort()`、`getProxy(local)` | 仍可取得代理連接埠及本機／區域網路基礎 URL；站點代理使用 `this.proxyUrl(params)`，第二個參數傳 false 取得區域網路網址 |
| `md5X/aesX/desX/rsaX` | 保留現有演算法、模式與輸入輸出編碼能力，標準 WebCrypto 不等價涵蓋 |
| `s2t/t2s/openWeb/htmlQuery` | 仍有文字轉換、App 與 HTML 擷取用途 |
| `cheerio.min.js` | 保留 DOM 查詢與操作能力；Jable 仍有使用，htmlQuery 不等價涵蓋 |
| `crypto-js.js` | 保留完整雜湊、加解密與二進位編碼能力；紅果改用模組內建版本，不再攜帶自己的副本 |
| `gbk.js` | 保留舊站搜尋需要的 GBK URL 編碼；TextDecoder 支援 GBK 解碼，TextEncoder 僅提供 UTF-8 編碼，不能直接取代 |

移除 `cat.js` 與 `similarity.js`：目前使用端沒有引用，前者是多種工具的合併包，後者屬於爬蟲自己的字串比對邏輯。仍使用這兩個模組的外部爬蟲，需改為自行提供相依函式庫，或依實際功能遷移；不能只替換匯入路徑就視為相容。

內建 JS 分為 `js/lib` 的宿主橋接與 `js/vendor` 的工具函式庫。公開 SDK 仍以 `import {Spider} from 'catvod';` 使用；工具庫改從 `assets://js/vendor/` 匯入，原先的 `assets://js/lib/cheerio.min.js`、`crypto-js.js`、`gbk.js` 路徑需同步調整。

紅果的 CryptoJS 匯入改為 `import 'assets://js/vendor/crypto-js.js';`，仍使用其 SHA-512、AES-CBC 與 Base64 能力。這是共用內建函式庫，並非將簽名與加密邏輯改成不同演算法。

new URL、crypto.getRandomValues 與 crypto.subtle.digest 仍可直接使用，但不是要求所有爬蟲遷移便利方法的理由。本次也保留 JAR 注入函式、類別方法的 this、凍結 prototype、彈幕釋放與呼叫取消流程。

## Local 與 TTL 快取

這部分使用既有共用 API，並非本次新增另一套快取。local 保存站點隔離的 JSON 值，提供 get／set／delete，set／delete 不回傳值；不要將 Local 設定當成會自動過期的快取，也不要依賴舊成功／失敗字串或隱含 expiresAt 欄位。

```javascript
this.local.set("preferences", {category: "movie", page: 1});
const preferences = this.local.get("preferences", {});
this.local.delete("preferences");
```

物件直接交給 set，get 也直接取得原生值，不先 JSON.stringify 再保存或一律 JSON.parse。舊資料若本來存成 JSON 字串，由來源針對該 key 明確遷移；合法的普通字串仍保留字串。不存在時回傳 null 或 get 的第二參數，清 TTL 快取不會刪除 Local。

限時資料使用 `await net.cached(key, {ttl, stale, persist}, loader)`，ttl 單位為毫秒。播放 URL 或短期憑證應依來源期限明確設定，通常使用 `stale: false, persist: false`；失敗應由 loader 拋出，不要偽裝成空的成功結果。舊快取資料不會自動轉換成這個合約。

## 驗證

逐一盤點入口及 helper 中的舊入口名稱、全域網路函式、net.http、__jsEvalReturn／__JS_SPIDER__、default 物件／factory、options.async／complete、js2Proxy／proxy2、舊 vendor 路徑與 catvod:host。搜尋命中只是定位，需閱讀函式與必要呼叫端；保留便利函式及合法 JSON.parse 不列為失敗。

| 檢查 | 通過條件 |
| --- | --- |
| 語法與載入 | ES module 語法通過，配套 QuickJS 可載入 default Spider 子類別、helper 與 vendor，init 完成後才呼叫入口 |
| 詳情集合 | 測 `[]`、`["a"]`、`["a", "b"]`、重複 ID 及單筆失敗；核對順序、完整欄位與 reject 傳遞 |
| 參數 | 測雙參數搜尋與顯式頁碼、空／多筆 vipFlags、分類 extend 物件；不可只檢查參數個數 |
| 非同步 | 驗證同步值、Promise 的完成順序，純資料與非同步布林接口、proxy、彈幕停止回呼均符合各自合約 |
| 列表與播放 | 分類／搜尋兩頁、尾頁、無結果與篩選正確；接通列表 ID → 詳情 → 每集播放值 → 播放結果 |
| 網路與資源 | 正文格式、毫秒期限、非 2xx／登入錯誤、Cookie／Session、Local／TTL、Dialog、reader、取消與 destroy 符合來源規則 |
| 代理 | 測扁平字串 params、URL 往返、headers 的字串／多值／無效型別、非 ASCII 文字與含 0／128／255 的二進位；串流交接後可讀取並由 App 關閉 |

完整清單才使用 page；外站已分頁就保留當頁，不再切片，有精確總筆數才填 total。記錄配套 App、QuickJS 模組、wrapper／JNI 來源；舊模組缺少 API 時不以相容分支掩蓋配套錯誤。

完成回報列出已修改檔案、保留分支及原因、實際執行的檢查與未測項目。分開說明語法、QuickJS／Android 載入、取樣詳情／播放網址及實際裝置播放；Node.js 或單筆成功不代表每個爬蟲都已全面遷移。
