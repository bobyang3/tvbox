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
# 使用方法: python 4gtv.py off (關閉轉發) 或 python 4gtv.py on (開啟轉發)
cmd_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
TS_RELAY_ENV = cmd_arg if cmd_arg in ['on', 'off'] else os.environ.get('TS_RELAY', 'on').lower()
GROUP_NAME = os.environ.get('GROUP_NAME', 'RobYang四季')
PROXY_URL = os.environ.get('PROXY_URL', '')

# --- 頻道數據 (使用 Asset ID 作為唯一 Key，同步自 4gtv_channels.txt)  ---
CH_DATA = {
    '4gtv-4gtv003': '民視第一台',
    '4gtv-4gtv001': '民視台灣台',
    '4gtv-4gtv002': '民視',
    '4gtv-4gtv040': '中視',
    '4gtv-4gtv041': '華視',
    '4gtv-4gtv042': '公視戲劇',
    'litv-ftv17': '好消息2台',
    'litv-ftv16': '好消息',
    '4gtv-4gtv018': '達文西頻道',
    '4gtv-4gtv044': '靖天卡通台',
    '4gtv-4gtv004': '民視綜藝台',
    '4gtv-4gtv070': '愛爾達娛樂台',
    '4gtv-4gtv046': '靖天綜合台',
    '4gtv-4gtv047': '靖天日本台',
    'litv-ftv09': '民視影劇台',
    '4gtv-4gtv049': '采昌影劇台',
    '4gtv-4gtv009': '中天新聞台',
    'litv-ftv13': '民視新聞台',
    '4gtv-4gtv074': '中視新聞',
    '4gtv-4gtv052': '華視新聞',
    'litv-longturn14': '寰宇新聞台',
    '4gtv-4gtv013': '視納華仁紀實頻道',
    '4gtv-4gtv017': 'amc電影台',
    '4gtv-4gtv011': '影迷數位電影台',
    '4gtv-4gtv055': '靖天映畫',
    '4gtv-4gtv077': 'TRACE Sport Stars',
    '4gtv-4gtv101': '智林體育台',
    '4gtv-4gtv057': '靖洋卡通Nice Bingo',
    'litv-ftv07': '民視旅遊台',
    '4gtv-4gtv014': '時尚運動X',
    '4gtv-4gtv082': 'TRACE Urban',
    '4gtv-4gtv083': 'Mezzo Live HD',
    '4gtv-4gtv059': 'CLASSICA 古典樂',
    '4gtv-4gtv061': '靖天電影台',
    '4gtv-4gtv062': '靖天育樂台',
    '4gtv-4gtv063': 'KLT-靖天國際台',
    '4gtv-4gtv065': '靖天資訊台',
    '4gtv-4gtv035': '鳳梨直擊台',
    '4gtv-4gtv038': '香蕉直擊台',
    '4gtv-4gtv043': '客家電視台',
    '4gtv-4gtv006': '豬哥亮歌廳秀',
    '4gtv-4gtv039': '八大綜藝台',
    '4gtv-4gtv058': '靖天戲劇台',
    '4gtv-4gtv045': '靖洋戲劇台',
    '4gtv-4gtv054': 'Nice TV 靖天歡樂台',
    '4gtv-live208': 'Love Nature',
    '4gtv-live201': '車迷TV',
    '4gtv-live206': '幸福空間居家台',
    '4gtv-live207': '三立綜合台',
    '4gtv-4gtv084': '國會頻道1',
    '4gtv-4gtv085': '國會頻道2',
    '4gtv-4gtv034': '八大精彩台',
    '4gtv-live047': '東森購物一台',
    '4gtv-live046': '東森購物二台',
    '4gtv-live121': 'LUXE TV Channel',
    '4gtv-live122': 'TV5MONDE STYLE HD 生活時尚',
    '4gtv-4gtv053': 'GINX Esports TV',
    '4gtv-live138': 'ROCK Action',
    '4gtv-4gtv073': 'TVBS',
    '4gtv-4gtv068': 'TVBS歡樂台',
    '4gtv-live105': '尼克兒童頻道',
    '4gtv-live620': 'HITS頻道',
    '4gtv-live030': 'LiveABC互動英語頻道',
    '4gtv-4gtv079': 'ARIRANG阿里郎頻道',
    '4gtv-live021': '經典電影台',
    '4gtv-live022': '經典卡通台',
    '4gtv-live024': '精選動漫台',
    '4gtv-live007': '大愛電視',
    '4gtv-live008': '人間衛視',
    '4gtv-live026': 'History 歷史頻道',
    '4gtv-live027': 'CI 罪案偵查頻道',
    '4gtv-live029': 'Lifetime 娛樂頻道',
    '4gtv-live031': '電影原聲台CMusic',
    '4gtv-live032': 'Nick Jr. 兒童頻道',
    '4gtv-live050': '新唐人亞太台',
    '4gtv-live060': 'SBN全球財經台',
    '4gtv-live069': 'CinemaWorld',
    '4gtv-live071': 'DW德國之聲',
    '4gtv-4gtv067': 'TVBS精采台',
    '4gtv-live089': '三立新聞iNEWS',
    '4gtv-live106': '大愛二台',
    '4gtv-live107': 'MOMO親子台',
    '4gtv-live130': 'CNBC Asia 財經台',
    '4gtv-live144': '金光布袋戲',
    '4gtv-live120': '愛爾達生活旅遊台',
    '4gtv-live215': '民視(直播)',
    '4gtv-live012': '滾動力rollor',
    '4gtv-4gtv076': '亞洲旅遊台',
    '4gtv-live112': 'Global Trekker',
    '4gtv-live403': '民視第一台(備)',
    '4gtv-live401': '民視台灣台(備)',
    '4gtv-live452': '華視新聞(備)',
    '4gtv-live413': '民視新聞台(備)',
    '4gtv-live474': '中視新聞(備)',
    '4gtv-live409': '中天新聞台(備)',
    '4gtv-live417': '亞洲旅遊台(備)',
    '4gtv-live408': '寰宇新聞台(備)',
    '4gtv-live405': '博斯高球台',
    '4gtv-live404': '博斯運動一台',
    '4gtv-live407': '博斯無限台',
    '4gtv-live406': '博斯網球台',
    '4gtv-4gtv075': '鏡電視新聞台',
    '4gtv-live014': '原住民族電視台',
    '4gtv-live011': 'fun探索娛樂台',
    '4gtv-live080': 'ROCK Entertainment',
    '4gtv-live410': '八大綜藝台(備)',
    '4gtv-live411': '時尚運動X(備)',
    '4gtv-4gtv156': '寰宇新聞台灣台',
    '4gtv-live017': 'DreamWorks 夢工廠動畫',
    '4gtv-live059': 'Bloomberg TV',
    '4gtv-live049': '東森購物四台',
    '4gtv-live048': '東森購物三台',
    '4gtv-live302': '芭樂直擊台',
    '4gtv-4gtv072': 'TVBS新聞',
    '4gtv-4gtv152': '東森新聞台',
    '4gtv-4gtv153': '東森財經新聞台',
    'fast-live139': 'GagaOOLala 精選',
    'fast-live415': 'MOMO親子精選',
}

# --- 輔助函式 ---

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
    return f"http://{request.headers.get('Host', '127.0.0.1:5000')}"

def get_m3u8_recursive(url):
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
    for asset, name in CH_DATA.items():
        lines.append(f'#EXTINF:-1 tvg-id="{asset}" tvg-name="{name}" group-title="{GROUP_NAME}",{name}')
        lines.append(f'{host}/?id={asset}')
    return Response("\n".join(lines), mimetype='application/x-mpegurl')

@app.route('/txt')
def playlist_txt():
    host = get_real_host()
    lines = [f"{GROUP_NAME},#genre#"]
    for asset, name in CH_DATA.items():
        lines.append(f"{name},{host}/?id={asset}")
    return Response("\n".join(lines), mimetype='text/plain; charset=utf-8')

@app.route('/help')
def help_page():
    host = get_real_host()
    html = f"""
    <html><body style="font-family:sans-serif; padding:20px;">
        <h2>📺 4GTV 轉發服務 V13 (簡化版)</h2>
        <p>目前模式：<b>{TS_RELAY_ENV.upper()}</b> | 分組：<b>{GROUP_NAME}</b></p>
        <ul>
            <li>M3U 清單：<a href="{host}/m3u">{host}/m3u</a></li>
            <li>TXT 清單：<a href="{host}/txt">{host}/txt</a></li>
            <li>測試播放 (民視)：<a href="{host}/?id=4gtv-4gtv002">{host}/?id=4gtv-4gtv002</a></li>
        </ul>
    </body></html>
    """
    return render_template_string(html)

@app.route('/')
def index():
    fs_asset_id = request.args.get('id', '4gtv-4gtv002')
    if fs_asset_id not in CH_DATA: return "Invalid Asset ID", 400

    try:
        # API 請求，fnCHANNEL_ID 設為 1 (API 通常只看 Asset ID)
        url = 'https://api2.4gtv.tv/App/GetChannelUrl2'
        fs_enc_key = str(uuid.uuid4()).upper()
        payload = {"fnCHANNEL_ID": "1", "fsDEVICE_TYPE": "mobile", 
                   "clsAPP_IDENTITY_VALIDATE_ARUS": {"fsVALUE": "", "fsENC_KEY": fs_enc_key},
                   "fsASSET_ID": fs_asset_id}
        headers = {"4GTV_AUTH": generate_4gtv_auth(), "fsDEVICE": "iOS", "fsENC_KEY": fs_enc_key, "Content-Type": "application/json"}
        
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome131", verify=False, proxies=get_proxies())
        urls = r.json().get('Data', {}).get('flstURLs', [])
        final_url = next((u for u in urls if 'cds.cdn.hinet.net' not in u), "")

        if TS_RELAY_ENV == 'off': return redirect(final_url)

        m3u8_text, base_url = get_m3u8_recursive(final_url)
        if not m3u8_text: return "Resolve Error", 502
        
        host, query_str = get_real_host(), (base_url.split('?')[1] if '?' in base_url else "")
        output = []
        for line in m3u8_text.split('\n'):
            line = line.strip()
            if line.startswith('#') or not line: output.append(line)
            else:
                ts = urljoin(base_url, line).replace('2000000', '6000000') # 畫質提升
                if query_str and '?' not in ts: ts += f"?{query_str}"
                output.append(f"{host}/ts?url={quote(ts)}")
        return Response('\n'.join(output), mimetype='application/vnd.apple.mpegurl')
    except Exception as e: return str(e), 500

if __name__ == '__main__':
    print(f"【服務啟動】TS_RELAY: {TS_RELAY_ENV.upper()}")
    app.run(host='0.0.0.0', port=5000)