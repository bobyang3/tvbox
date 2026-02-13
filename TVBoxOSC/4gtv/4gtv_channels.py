from curl_cffi import requests
import time

# 本地代理（視需求開啟）
proxies = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897",
}

# 創建 session 並模擬 Chrome
session = requests.Session()
# 如果在海外，請取消下面這行的註釋以使用代理
# session.proxies = proxies
session.impersonate = "chrome124"

# 輸出 TXT 文件
txt_file = "4gtv_channels_new.txt"

print("🚀 開始抓取頻道資訊...")

with open(txt_file, "w", encoding="utf-8") as f:
    # 增加到 400 以確保抓到所有新頻道
    for i in range(1, 999):
        url = f"https://api2.4gtv.tv/Channel/GetChannel/{i}"

        try:
            r = session.get(
                url,
                timeout=10,
                headers={
                    "Accept": "application/json",
                    "Referer": "https://www.4gtv.tv/",
                }
            )

            if r.status_code != 200:
                continue

            data = r.json()

            if data.get("Success") and data.get("Data"):
                name = data["Data"].get("fsNAME")
                asset_id = data["Data"].get("fs4GTV_ID") # 這是 Asset ID
                numeric_id = str(i) # 這就是 fnCHANNEL_ID

                if name and asset_id:
                    # 輸出格式：名稱,Asset_ID,數字_ID
                    line = f"{name},{asset_id},{numeric_id}\n"
                    f.write(line)
                    print(f"成功: {name} | Asset: {asset_id} | ID: {numeric_id}")

        except Exception as e:
            print(f"頻道 {i} 出錯: {e}")

        time.sleep(0.1) # 稍微縮短延遲以提升速度

print(f"\n✅ 抓取完成！結果已保存到 {txt_file}")