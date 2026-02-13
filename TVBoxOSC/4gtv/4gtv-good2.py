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
cmd_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
TS_RELAY_ENV = cmd_arg if cmd_arg in ['on', 'off'] else os.environ.get('TS_RELAY', 'on').lower()
GROUP_NAME = os.environ.get('GROUP_NAME', 'RobYang四季')
PROXY_URL = os.environ.get('PROXY_URL', '')

# --- 頻道數據 (Asset ID 作為唯一 Primary Key) ---
# 格式: 'Asset ID': ('API所需數字ID', '中文名稱')
CH_DATA = {
    '4gtv-4gtv003': ('1', '民視第一台'),
    '4gtv-4gtv001': ('2', '民視台灣台'),
    '4gtv-4gtv002': ('3', '民視'),
    '4gtv-4gtv040': ('4', '中視'),
    '4gtv-4gtv041': ('6', '華視'),
    '4gtv-4gtv042': ('7', '公視戲劇'),
    'litv-ftv17': ('8', '好消息2台'),
    'litv-ftv16': ('9', '好消息'),
    '4gtv-4gtv018': ('11', '達文西頻道'),
    '4gtv-4gtv044': ('15', '靖天卡通台'),
    '4gtv-4gtv004': ('16', '民視綜藝台'),
    '4gtv-4gtv070': ('19', '愛爾達娛樂台'),
    '4gtv-4gtv046': ('21', '靖天綜合台'),
    '4gtv-4gtv047': ('22', '靖天日本台'),
    'litv-ftv09': ('24', '民視影劇台'),
    '4gtv-4gtv049': ('25', '采昌影劇台'),
    '4gtv-4gtv009': ('30', '中天新聞台'),
    'litv-ftv13': ('31', '民視新聞台'),
    '4gtv-4gtv074': ('33', '中視新聞'),
    '4gtv-4gtv052': ('34', '華視新聞'),
    'litv-longturn14': ('36', '寰宇新聞台'),
    '4gtv-4gtv013': ('38', '視納華仁紀實頻道'),
    '4gtv-4gtv017': ('39', 'amc電影台'),
    '4gtv-4gtv011': ('40', '影迷數位電影台'),
    '4gtv-4gtv055': ('42', '靖天映畫'),
    '4gtv-4gtv077': ('57', 'TRACE Sport Stars'),
    '4gtv-4gtv101': ('58', '智林體育台'),
    '4gtv-4gtv057': ('59', '靖洋卡通Nice Bingo'),
    'litv-ftv07': ('61', '民視旅遊台'),
    '4gtv-4gtv014': ('69', '時尚運動X'),
    '4gtv-4gtv082': ('78', 'TRACE Urban'),
    '4gtv-4gtv083': ('79', 'Mezzo Live HD'),
    '4gtv-4gtv059': ('80', 'CLASSICA 古典樂'),
    '4gtv-live021': ('82', '經典電影台'),
    '4gtv-4gtv062': ('83', '靖天育樂台'),
    '4gtv-4gtv063': ('84', 'KLT-靖天國際台'),
    '4gtv-4gtv065': ('88', '靖天資訊台'),
    '4gtv-4gtv035': ('93', '鳳梨直擊台'),
    '4gtv-4gtv038': ('94', '香蕉直擊台'),
    '4gtv-4gtv043': ('107', '客家電視台'),
    '4gtv-4gtv006': ('113', '豬哥亮歌廳秀'),
    '4gtv-4gtv039': ('114', '八大綜藝台'),
    '4gtv-4gtv058': ('116', '靖天戲劇台'),
    '4gtv-4gtv045': ('118', '靖洋戲劇台'),
    '4gtv-4gtv054': ('119', 'Nice TV 靖天歡樂台'),
    '4gtv-live080': ('124', 'ROCK Entertainment'),
    '4gtv-live208': ('139', 'Love Nature'),
    '4gtv-live201': ('160', '車迷TV'),
    '4gtv-live206': ('168', '幸福空間居家台'),
    '4gtv-live207': ('169', '三立綜合台'),
    '4gtv-4gtv084': ('170', '國會頻道1'),
    '4gtv-4gtv085': ('171', '國會頻道2'),
    '4gtv-4gtv034': ('172', '八大精彩台'),
    '4gtv-live047': ('173', '東森購物一台'),
    '4gtv-live046': ('174', '東森購物二台'),
    '4gtv-live121': ('175', 'LUXE TV Channel'),
    '4gtv-live122': ('178', 'TV5MONDE STYLE HD 生活時尚'),
    '4gtv-4gtv053': ('179', 'GINX Esports TV'),
    '4gtv-live138': ('180', 'ROCK Action'),
    '4gtv-4gtv073': ('183', 'TVBS'),
    '4gtv-4gtv068': ('184', 'TVBS歡樂台'),
    '4gtv-live105': ('185', '尼克兒童頻道'),
    '4gtv-live620': ('186', 'HITS頻道'),
    '4gtv-live030': ('188', 'LiveABC互動英語頻道'),
    '4gtv-4gtv079': ('189', 'ARIRANG阿里郎頻道'),
    '4gtv-live022': ('202', '經典卡通台'),
    '4gtv-live024': ('204', '精選動漫台'),
    '4gtv-live007': ('209', '大愛電視'),
    '4gtv-live008': ('210', '人間衛視'),
    '4gtv-live026': ('214', 'History 歷史頻道'),
    '4gtv-live027': ('215', 'CI 罪案偵查頻道'),
    '4gtv-live029': ('217', 'Lifetime 娛樂頻道'),
    '4gtv-live031': ('218', '電影原聲台CMusic'),
    '4gtv-live032': ('219', 'Nick Jr. 兒童頻道'),
    '4gtv-live050': ('223', '新唐人亞太台'),
    '4gtv-live060': ('224', 'SBN全球財經台'),
    '4gtv-live069': ('225', 'CinemaWorld'),
    '4gtv-live071': ('226', 'DW德國之聲'),
    '4gtv-4gtv067': ('227', 'TVBS精采台'),
    '4gtv-live089': ('229', '三立新聞iNEWS'),
    '4gtv-live106': ('230', '大愛二台'),
    '4gtv-live107': ('231', 'MOMO親子台'),
    '4gtv-live130': ('235', 'CNBC Asia 財經台'),
    '4gtv-live144': ('236', '金光布袋戲'),
    '4gtv-live120': ('237', '愛爾達生活旅遊台'),
    '4gtv-live215': ('246', '民視(直播)'),
    '4gtv-live012': ('249', '滾動力rollor'),
    '4gtv-4gtv076': ('250', '亞洲旅遊台'),
    '4gtv-live112': ('252', 'Global Trekker'),
    '4gtv-4gtv075': ('268', '鏡電視新聞台'),
    '4gtv-live014': ('273', '原住民族電視台'),
    '4gtv-live011': ('274', 'fun探索娛樂台'),
    '4gtv-4gtv156': ('280', '寰宇新聞台灣台'),
    '4gtv-live017': ('282', 'DreamWorks 夢工廠動畫'),
    '4gtv-live059': ('283', 'Bloomberg TV'),
    '4gtv-live049': ('286', '東森購物四台'),
    '4gtv-live048': ('287', '東森購物三台'),
    '4gtv-live302': ('290', '芭樂直擊台'),
    '4gtv-4gtv072': ('291', 'TVBS新聞'),
    '4gtv-4gtv152': ('292', '東森新聞台'),
    '4gtv-4gtv153': ('293', '東森財經新聞台'),
    'fast-live139': ('301', 'GagaOOLala 精選'),
    'fast-live415': ('999', 'MOMO親子精選'),
}

# --- 核心邏輯 (基於 good.py) ---

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
        return base64.b64encode(hashlib.sha512((format_date + decrypted.decode('utf-8')).encode()).digest()).decode()
    except: return ""

def get_real_host():
    # 改進：自動從標頭抓取目前 Host，解決 127.0.0.1 播放問題
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
    """代理影片片段數據流"""
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
    for asset, data in CH_DATA.items():
        name = data[1]
        lines.append(f'#EXTINF:-1 tvg-id="{asset}" tvg-name="{name}" group-title="{GROUP_NAME}",{name}')
        lines.append(f'{host}/?id={asset}')
    return Response("\n".join(lines), mimetype='application/x-mpegurl')

@app.route('/txt')
def playlist_txt():
    host = get_real_host()
    lines = [f"{GROUP_NAME},#genre#"]
    for asset, data in CH_DATA.items():
        lines.append(f"{data[1]},{host}/?id={asset}")
    return Response("\n".join(lines), mimetype='text/plain; charset=utf-8')

@app.route('/help')
def help_page():
    host = get_real_host()
    html = f"""
    <html><body style="font-family:sans-serif; padding:20px;">
        <h2>📺 4GTV 轉發服務 V13 Final</h2>
        <p>目前模式：<b>{TS_RELAY_ENV.upper()}</b> | 分組：<b>{GROUP_NAME}</b></p>
        <ul>
            <li>M3U 清單：<a href="{host}/m3u">{host}/m3u</a></li>
            <li>TXT 清單：<a href="{host}/txt">{host}/txt</a></li>
            <li>測試 ID 播放 (民視)：<a href="{host}/?id=4gtv-4gtv002">{host}/?id=4gtv-4gtv002</a></li>
        </ul>
    </body></html>
    """
    return render_template_string(html)

@app.route('/')
def index():
    asset_id = request.args.get('id', '4gtv-4gtv002')
    if asset_id not in CH_DATA: return "Invalid Asset ID", 400

    # 重點：從字典提取內部 API 使用的數字 ID
    channel_id = CH_DATA[asset_id][0]

    try:
        url = 'https://api2.4gtv.tv/App/GetChannelUrl2'
        fs_enc_key = str(uuid.uuid4()).upper()
        payload = {"fnCHANNEL_ID": channel_id, "fsDEVICE_TYPE": "mobile", 
                   "clsAPP_IDENTITY_VALIDATE_ARUS": {"fsVALUE": "", "fsENC_KEY": fs_enc_key},
                   "fsASSET_ID": asset_id}
        headers = {"4GTV_AUTH": generate_4gtv_auth(), "fsDEVICE": "iOS", "fsENC_KEY": fs_enc_key, "Content-Type": "application/json"}
        
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome131", verify=False, proxies=get_proxies())
        urls = r.json().get('Data', {}).get('flstURLs', [])
        final_url = next((u for u in urls if 'cds.cdn.hinet.net' not in u), "")

        if TS_RELAY_ENV == 'off':
            return redirect(final_url)

        m3u8_text, base_url = get_m3u8_recursive(final_url)
        if not m3u8_text: return "Resolve Error", 502
        
        host, query_str = get_real_host(), (base_url.split('?')[1] if '?' in base_url else "")
        output = []
        for line in m3u8_text.split('\n'):
            line = line.strip()
            if line.startswith('#') or not line: output.append(line)
            else:
                # 畫質提升 (2M -> 6M)
                ts = urljoin(base_url, line).replace('2000000', '6000000')
                if query_str and '?' not in ts: ts += f"?{query_str}"
                output.append(f"{host}/ts?url={quote(ts)}")
        return Response('\n'.join(output), mimetype='application/vnd.apple.mpegurl')
    except Exception as e: return str(e), 500

if __name__ == '__main__':
    print(f"【服務啟動】目前的 TS_RELAY 模式: {TS_RELAY_ENV.upper()} | 分組名稱: {GROUP_NAME}")
    app.run(host='0.0.0.0', port=5000)