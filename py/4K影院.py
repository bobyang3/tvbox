# coding=utf-8
# !/usr/bin/python

"""

作者 丢丢喵推荐 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider as BaseSpider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import base64
import json
import time
import sys
import re
import os


xurl = "https://www.4kvm.net"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; Mi Note 2 Build/OPR1.170623.032) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.1.1'
          }

class Spider(BaseSpider):
    global xurl
    global headerx


    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {"class": []}

        detail = self.net.req(xurl, {"headers": headerx, "timeout": 5000})
        if detail.get("error"): raise RuntimeError(detail["error"])
        if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
        res = detail["content"]
        doc = BeautifulSoup(res, "lxml")
        soups = doc.find_all('ul', class_="main-header")

        for soup in soups:
            vods = soup.find_all('li')

            for vod in vods:

                name = vod.text.strip()

                if any(keyword in name for keyword in ["首页", "电视剧", "高分电影", "影片下载", "热门播放"]):
                    continue

                id = vod.find('a')['href']
                if 'http' not in id:
                    id = xurl + id

                result["class"].append({"type_id": id, "type_name": name})

        return result

    def homeVideoContent(self):
        videos = []

        detail = self.net.req(xurl, {"headers": headerx, "timeout": 5000})
        if detail.get("error"): raise RuntimeError(detail["error"])
        if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
        res = detail["content"]
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('article', class_="item movies")

        for vod in soups:

            name = vod.find('img')['alt']

            ids = vod.find('div', class_="poster")
            id = ids.find('a')['href']

            pic = vod.find('img')['src']

            remarks = vod.find('div', class_="rating")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                     }
            videos.append(video)

        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if 'movies' not in cid:

            if '@' in cid:
                fenge = cid.split("@")
                detail = self.net.req(fenge[0], {"headers": headerx, "timeout": 5000})
                if detail.get("error"): raise RuntimeError(detail["error"])
                if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
                res = detail["content"]
                doc = BeautifulSoup(res, "lxml")

                soups = doc.find_all('div', class_="se-c")

                for vod in soups:

                    name = vod.text.strip()

                    id = vod.find('a')['href']

                    pic = self.extract_middle_text(str(res), '<meta property="og:image"  content="', '"', 0).replace('#038;', '')

                    remark = "推荐"

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                            }
                    videos.append(video)
            else:
                if pg:
                    page = int(pg)
                else:
                    page = 1

                url = f'{cid}/page/{str(page)}'
                detail = self.net.req(url, {"headers": headerx, "timeout": 5000})
                if detail.get("error"): raise RuntimeError(detail["error"])
                if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
                res = detail["content"]
                doc = BeautifulSoup(res, "lxml")

                soups = doc.find_all('article', class_="item tvshows")

                for vod in soups:
                    name = vod.find('img')['alt']

                    ids = vod.find('div', class_="poster")
                    id = ids.find('a')['href']

                    pic = vod.find('img')['src']

                    remarks = vod.find('div', class_="update")
                    remark = remarks.text.strip()

                    video = {
                        "vod_id": id + '@' + name,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_tag": "folder",
                        "vod_remarks": remark
                            }
                    videos.append(video)
        else:
            if pg:
                page = int(pg)
            else:
                page = 1

            url = f'{cid}/page/{str(page)}'
            detail = self.net.req(url, {"headers": headerx, "timeout": 5000})
            if detail.get("error"): raise RuntimeError(detail["error"])
            if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
            res = detail["content"]
            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="animation-2")

            for item in soups:
                vods = item.find_all('article')

                for vod in vods:

                    name = vod.find('img')['alt']

                    ids = vod.find('div', class_="poster")
                    id = ids.find('a')['href']

                    pic = vod.find('img')['src']

                    remarks = vod.find('div', class_="rating")
                    remark = remarks.text.strip()

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                           }
                    videos.append(video)
                    
        if len(videos)<30:
            pagecount=1
        else:
            pagecount = 9999

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = pagecount
        result['total'] = 999
        result['limit'] = len(videos)

        return result

    def detailContent(self, ids):
        if not ids:
            return {'list': []}
        responses = [self._detail(video_id) for video_id in ids]
        failed = next((response for response in responses if isinstance(response, dict) and response.get("msg") and not response.get("list")), None)
        if failed:
            return failed
        first = responses[0]
        if all(isinstance(response, dict) and isinstance(response.get("list"), list) for response in responses):
            return {**first, "list": [item for response in responses for item in response["list"]]}
        return first

    def _detail(self, video_id):
        did = video_id
        result = {}
        videos = []
        xianlu = ''
        bofang = ''

        if 'movies' not in did:
            res = self.net.req(did, {"headers": headerx, "timeout": 5000})
            if res.get("error"): raise RuntimeError(res["error"])
            if not 200 <= res["code"] < 300: raise RuntimeError("HTTP "+str(res["code"]))
            res = res["content"]
            doc = BeautifulSoup(res, "lxml")

            content = '剧情介绍📢' + self.extract_middle_text(res,'<meta name="description" content="','"', 0)

            postid = self.extract_middle_text(res, 'postid:', ',', 0)

            res1 = self.extract_middle_text(res,'videourls:[','],', 0)
            data = json.loads(res1)

            for vod in data:

                name = str(vod['name'])

                id = f"{vod['url']}@{postid}"

                bofang = bofang + name + '$' + id + '#'

            bofang = bofang[:-1]
            xianlu = '4K影院'

        else:
            res = self.net.req(did, {"headers": headerx, "timeout": 5000})
            if res.get("error"): raise RuntimeError(res["error"])
            if not 200 <= res["code"] < 300: raise RuntimeError("HTTP "+str(res["code"]))
            res = res["content"]
            doc = BeautifulSoup(res, "lxml")

            content = '剧情介绍📢' + self.extract_middle_text(res, '<meta name="description" content="', '"', 0)

            bofang = self.extract_middle_text(res, "data-postid='", "'", 0)
            xianlu = '4K影院'

        videos.append({
            "vod_id": did,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        if '@' in id:
            fenge = id.split("@")

            url = f'{xurl}/artplayer?id={fenge[1]}&source=0&ep={fenge[0]}'
            detail = self.net.req(url, {"headers": headerx, "timeout": 5000})
            if detail.get("error"): raise RuntimeError(detail["error"])
            if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
            res = detail["content"]

            expires = self.extract_middle_text(res, "expires: '", "'", 0)
            client = self.extract_middle_text(res, "client: '", "'", 0)
            nonce = self.extract_middle_text(res, "nonce: '", "'", 0)
            token = self.extract_middle_text(res, "token: '", "'", 0)
            source = self.extract_middle_text(res, "source: '", "'", 0)

            payload = {
                "expires": expires,
                "client": client,
                "nonce": nonce,
                "token": token,
                "source": source
                      }

            response = self.net.req(source, {"method": "POST", "postType": "json", "data": payload, "headers": headerx, "timeout": 5000})
            if response.get("error"): raise RuntimeError(response["error"])
            if not 200 <= response["code"] < 300: raise RuntimeError("HTTP "+str(response["code"]))
            response_data = json.loads(response["content"])
            url = response_data['url']
        else:
            url = f'{xurl}/artplayer?mvsource=0&id={id}&type=hls'
            detail = self.net.req(url, {"headers": headerx, "timeout": 5000})
            if detail.get("error"): raise RuntimeError(detail["error"])
            if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
            res = detail["content"]

            expires = self.extract_middle_text(res, "expires: '", "'", 0)
            client = self.extract_middle_text(res, "client: '", "'", 0)
            nonce = self.extract_middle_text(res, "nonce: '", "'", 0)
            token = self.extract_middle_text(res, "token: '", "'", 0)
            source = self.extract_middle_text(res, "source: '", "'", 0)

            payload = {
                "expires": expires,
                "client": client,
                "nonce": nonce,
                "token": token,
                "source": source
                      }

            response = self.net.req(source, {"method": "POST", "postType": "json", "data": payload, "headers": headerx, "timeout": 5000})
            if response.get("error"): raise RuntimeError(response["error"])
            if not 200 <= response["code"] < 300: raise RuntimeError("HTTP "+str(response["code"]))
            response_data = json.loads(response["content"])
            url = response_data['url']

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []

        url = f'{xurl}/xssearch?s={key}'
        detail = self.net.req(url, {"headers": headerx, "timeout": 5000})
        if detail.get("error"): raise RuntimeError(detail["error"])
        if not 200 <= detail["code"] < 300: raise RuntimeError("HTTP "+str(detail["code"]))
        res = detail["content"]
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="result-item")

        for vod in soups:
            ids = vod.find('div', class_="title")
            id = ids.find('a')['href']

            if 'movies' not in id:

                name = vod.find('img')['alt']

                pic = vod.find('img')['src']

                remark = "推荐"

                video = {
                    "vod_id": id + '@' + name,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_tag": "folder",
                    "vod_remarks": remark
                        }
                videos.append(video)

            else:
                name = vod.find('img')['alt']

                pic = vod.find('img')['src']

                remark = "推荐"

                video = {
                    "vod_id": id,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                        }
                videos.append(video)

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 1
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def proxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None





