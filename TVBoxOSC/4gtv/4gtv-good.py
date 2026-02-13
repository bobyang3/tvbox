#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from Crypto.Cipher import AES
from flask import Flask, request, redirect, Response, stream_with_context, render_template_string
from urllib.parse import urlparse, quote, urljoin
from curl_cffi import requests

app = Flask(__name__)

# --- 配置設定 (優先級：指令參數 > 環境變數 > 預設值) ---
# 支援 python 4gtv13.py off 直接關閉 Relay 功能
cmd_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
TS_RELAY_ENV = cmd_arg if cmd_arg in ['on', 'off'] else os.environ.get('TS_RELAY', 'on').lower()
GROUP_NAME = os.environ.get('GROUP_NAME', 'RobYang四季')
PROXY_URL = os.environ.get('PROXY_URL', '')  # 海外環境(如美國)請設定台灣 Proxy

# --- 完整頻道清單 (根據 4gtv.m3u 同步名稱與 ID) ---
CH_DATA = {
    '1': {'asset': '4gtv-4gtv003', 'name': '民視第一台'},
    '2': {'asset': '4gtv-4gtv001', 'name': '民視台灣台'},
    '3': {'asset': '4gtv-4gtv002', 'name': '民視'},
    '4': {'asset': '4gtv-4gtv040', 'name': '中視'},
    '6': {'asset': '4gtv-4gtv041', 'name': '華視'},
    '7': {'asset': '4gtv-4gtv042', 'name': '公視戲劇'},
    '8': {'asset': 'litv-ftv17', 'name': '好消息2台'},
    '9': {'asset': 'litv-ftv16', 'name': '好消息'},
    '11': {'asset': '4gtv-4gtv018', 'name': '達文西頻道'},
    '15': {'asset': '4gtv-4gtv044', 'name': '靖天卡通台'},
    '16': {'asset': '4gtv-4gtv004', 'name': '民視綜藝台'},
    '19': {'asset': '4gtv-4gtv070', 'name': '愛爾達娛樂台'},
    '21': {'asset': '4gtv-4gtv046', 'name': '靖天綜合台'},
    '22': {'asset': '4gtv-4gtv047', 'name': '靖天日本台'},
    '23': {'asset': 'litv-longturn18', 'name': '中視新聞台'},
    '24': {'asset': 'litv-ftv09', 'name': '民視影劇台'},
    '25': {'asset': '4gtv-4gtv049', 'name': '采昌影劇台'},
    '30': {'asset': '4gtv-4gtv009', 'name': '中天新聞台'},
    '31': {'asset': 'litv-ftv13', 'name': '民視新聞台'},
    '33': {'asset': '4gtv-4gtv074', 'name': '中視新聞'},
    '34': {'asset': '4gtv-4gtv052', 'name': '華視新聞'},
    '36': {'asset': 'litv-longturn14', 'name': '寰宇新聞台'},
    '38': {'asset': '4gtv-4gtv013', 'name': '視納華仁紀實頻道'},
    '39': {'asset': '4gtv-4gtv017', 'name': 'amc電影台'},
    '40': {'asset': '4gtv-4gtv011', 'name': '影迷數位電影台'},
    '42': {'asset': '4gtv-4gtv055', 'name': '靖天映畫'},
    '48': {'asset': 'litv-longturn05', 'name': '三立綜合台'},
    '50': {'asset': 'litv-longturn07', 'name': '三立iNEWS'},
    '57': {'asset': '4gtv-live047', 'name': '東森購物一台'},
    '58': {'asset': '4gtv-live046', 'name': '東森購物二台'},
    '59': {'asset': '4gtv-live048', 'name': '東森購物三台'},
    '61': {'asset': 'litv-ftv07', 'name': '民視旅遊台'},
    '82': {'asset': '4gtv-live021', 'name': '經典電影台'},
    '107': {'asset': '4gtv-4gtv043', 'name': '客家電視台'},
    '113': {'asset': '4gtv-4gtv006', 'name': '豬哥亮歌廳秀'},
    '114': {'asset': '4gtv-4gtv039', 'name': '八大綜藝台'},
    '124': {'asset': '4gtv-live080', 'name': 'ROCK Entertainment'},
    '168': {'asset': '4gtv-live206', 'name': '幸福空間居家台'},
    '183': {'asset': '4gtv-4gtv073', 'name': 'TVBS'},
    '184': {'asset': '4gtv-4gtv068', 'name': 'TVBS歡樂台'},
    '231': {'asset': '4gtv-live107', 'name': 'MOMO親子台'},
    '268': {'asset': '4gtv-4gtv075', 'name': '鏡電視新聞台'},
    '282': {'asset': '4gtv-live017', 'name': 'DreamWorks 夢工廠動畫'},
    '291': {'asset': '4gtv-4gtv072', 'name': 'TVBS新聞台'},
    '292': {'asset': '4gtv-4gtv152', 'name': '東森新聞台'},
    '293': {'asset': '4gtv-4gtv153', 'name': '東森財經新聞台'},
    '301': {'asset': 'fast-live139', 'name': 'GagaOOLala 精選'},
    '302': {'asset': '4gtv-live096', 'name': 'INULTRA'},
    '999': {'asset': 'fast-live415', 'name': 'MOMO親子精選'},
}

ID_TO_FS_ASSET_ID = {k: v['asset'] for k, v in CH_DATA.items()}
FS_ASSET_ID_TO_ID = {v['asset']: k for k, v in CH_DATA.items()}

# --- 核心邏輯 ---

def get_proxies():
    return {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

def generate_4gtv_auth():
    head_key = "PyPJU25iI2IQCMWq7kblwh9sGCypqsxMp4sKjJo95SK43h08ff+j1nbWliTySSB+N67BnXrYv9DfwK+ue5wWkg=="
    KEY, IV = b"ilyB29ZdruuQjC45JhBBR7o2Z8WJ26Vg", b"JUMxvVMmszqUTeKn"
    try:
        decode = base64.b64decode(head_key)
        format_date = datetime.now(timezone.utc).strftime("%Y%m%d")
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_raw = cipher.decrypt(decode)
        decrypted = decrypted_raw[:-decrypted_raw[-1]]
        to_hash = format_date + decrypted.decode('utf-8')
        return base64.b64encode(hashlib.sha512(to_hash.encode()).digest()).decode()
    except: return ""

def get_real_host():
    # 動態取得請求的 Host，解決 127.0.0.1 或 Domain 存取不一致的問題
    return f"http://{request.headers.get('Host', '127.0.0.1:5000')}"

def get_m3u8_recursive(url):
    """遞歸解析直到找到包含影片片段的底層播放列表"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://www.4gtv.tv/'}
    try:
        r = requests.get(url, headers=headers, impersonate="chrome131", verify=False, timeout=10, proxies=get_proxies())
        content = r.text.strip()
        media_line = next((l.strip() for l in reversed(content.split('\n')) if l.strip() and not l.startswith('#')), None)
        if not media_line: return None, None
        full_url = urljoin(url, media_line)
        return get_m3u8_recursive(full_url) if '.m3u8' in media_line else (content, url)
    except: return None, None

@app.route('/ts')
def proxy_ts():
    """代理影片片段數據流，解決海外 IP 被封鎖問題"""
    target_url = request.args.get('url')
    if not target_url: return "Missing URL", 400
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.4gtv.tv/'}
    def generate():
        try:
            r = requests.get(target_url, headers=headers, stream=True, impersonate="chrome131", verify=False, timeout=25, proxies=get_proxies())
            yield from r.iter_content(chunk_size=1024*256)
        except: pass
    return Response(stream_with_context(generate()), content_type="video/mp2t")

@app.route('/m3u')
def playlist_m3u():
    host = get_real_host()
    lines = ["#EXTM3U"]
    for cid in sorted(CH_DATA.keys(), key=lambda x: int(x)):
        name, asset = CH_DATA[cid]['name'], CH_DATA[cid]['asset']
        lines.append(f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" group-title="{GROUP_NAME}",{name}')
        lines.append(f'{host}/?id={asset}')
    return Response("\n".join(lines), mimetype='application/x-mpegurl')

@app.route('/txt')
def playlist_txt():
    host = get_real_host()
    lines = [f"{GROUP_NAME},#genre#"]
    for cid in sorted(CH_DATA.keys(), key=lambda x: int(x)):
        lines.append(f"{CH_DATA[cid]['name']},{host}/?id={CH_DATA[cid]['asset']}")
    return Response("\n".join(lines), mimetype='text/plain; charset=utf-8')

@app.route('/help')
def help_page():
    host = get_real_host()
    html = f"""
    <html><body style="font-family:sans-serif; padding:20px;">
        <h2>📺 4GTV 轉發服務 V13</h2>
        <p>運作模式：<b>{TS_RELAY_ENV.upper()}</b> | 清單分組：<b>{GROUP_NAME}</b></p>
        <p>代理設定：<b>{'已啟用: ' + PROXY_URL if PROXY_URL else '直接連線'}</b></p>
        <ul>
            <li>M3U 清單：<a href="{host}/m3u">{host}/m3u</a></li>
            <li>TXT 清單：<a href="{host}/txt">{host}/txt</a></li>
            <li>測試 ID 播放 (民視)：<a href="{host}/?id=3">{host}/?id=3</a></li>
        </ul>
    </body></html>
    """
    return render_template_string(html)

@app.route('/')
def index():
    user_input_id = request.args.get('id', '4gtv-4gtv002')
    channel_id = user_input_id if user_input_id.isdigit() else FS_ASSET_ID_TO_ID.get(user_input_id)
    fs_asset_id = ID_TO_FS_ASSET_ID.get(user_input_id) if user_input_id.isdigit() else user_input_id
    if not fs_asset_id: return "Invalid ID", 400

    try:
        url = 'https://api2.4gtv.tv/App/GetChannelUrl2'
        fs_enc_key = str(uuid.uuid4()).upper()
        payload = {"fnCHANNEL_ID": channel_id, "fsDEVICE_TYPE": "mobile", "clsAPP_IDENTITY_VALIDATE_ARUS": {"fsVALUE": "", "fsENC_KEY": fs_enc_key}, "fsASSET_ID": fs_asset_id}
        headers = {"4GTV_AUTH": generate_4gtv_auth(), "fsDEVICE": "iOS", "fsENC_KEY": fs_enc_key, "Content-Type": "application/json"}
        
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome131", verify=False, proxies=get_proxies())
        urls = r.json().get('Data', {}).get('flstURLs', [])
        final_url = next((u for u in urls if 'cds.cdn.hinet.net' not in u), "")

        # 核心修正：除非 TS_RELAY 為 off，否則一律中轉畫質修正後的 TS 片段
        if TS_RELAY_ENV == 'off':
            return redirect(final_url)

        m3u8_text, base_url = get_m3u8_recursive(final_url)
        if not m3u8_text: return "Resolve Error", 502
        
        host, query_str = get_real_host(), (base_url.split('?')[1] if '?' in base_url else "")
        output = []
        for line in m3u8_text.split('\n'):
            line = line.strip()
            if line.startswith('#') or not line.strip(): output.append(line)
            else:
                # 畫質提升邏輯：將 2000k 替換為 6000k
                ts = urljoin(base_url, line).replace('2000000', '6000000')
                if query_str and '?' not in ts: ts += f"?{query_str}"
                output.append(f"{host}/ts?url={quote(ts)}")
        return Response('\n'.join(output), mimetype='application/vnd.apple.mpegurl')
    except Exception as e: return str(e), 500

if __name__ == '__main__':
    print(f"【服務啟動】目前的 TS_RELAY 模式: {TS_RELAY_ENV.upper()}")
    app.run(host='0.0.0.0', port=5000)