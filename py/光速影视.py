# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib.parse import quote, urlparse
from base64 import b64encode, b64decode
import json
import time
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):

    def init(self, extend=""):
        self.host = self.gethost()
        pass



    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def action(self, action):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        data = self.getdata("/api.php/getappapi.index/initV119")
        dy = {"class": "类型", "area": "地区", "lang": "语言", "year": "年份", "letter": "字母", "by": "排序",
              "sort": "排序"}
        filters = {}
        classes = []
        json_data = data["type_list"]
        homedata = data["banner_list"][8:]
        for item in json_data:
            if item["type_name"] == "全部":
                continue
            has_non_empty_field = False
            jsontype_extend = json.loads(item["type_extend"])
            homedata.extend(item["recommend_list"])
            jsontype_extend["sort"] = "最新,最热,最赞"
            classes.append({"type_name": item["type_name"], "type_id": item["type_id"]})
            for key in dy:
                if key in jsontype_extend and jsontype_extend[key].strip() != "":
                    has_non_empty_field = True
                    break
            if has_non_empty_field:
                filters[str(item["type_id"])] = []
                for dkey in jsontype_extend:
                    if dkey in dy and jsontype_extend[dkey].strip() != "":
                        values = jsontype_extend[dkey].split(",")
                        value_array = [{"n": value.strip(), "v": value.strip()} for value in values if
                                       value.strip() != ""]
                        filters[str(item["type_id"])].append({"key": dkey, "name": dy[dkey], "value": value_array})
        result = {}
        result["class"] = classes
        result["filters"] = filters
        result["list"] = homedata[1:]
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        body = {"area": extend.get('area', '全部'), "year": extend.get('year', '全部'), "type_id": tid, "page": pg,
                "sort": extend.get('sort', '最新'), "lang": extend.get('lang', '全部'),
                "class": extend.get('class', '全部')}
        result = {}
        data = self.getdata("/api.php/getappapi.index/typeFilterVodList", body)
        result["list"] = data["recommend_list"]
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
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
        body = f"vod_id={video_id}"
        data = self.getdata("/api.php/getappapi.index/vodDetail", body)
        vod = data["vod"]
        play = []
        names = []
        for itt in data["vod_play_list"]:
            a = []
            names.append(itt["player_info"]["show"])
            for it in itt['urls']:
                it['user_agent']=itt["player_info"].get("user_agent")
                it["parse"]=itt["player_info"].get("parse")
                a.append(f"{it['name']}${self.e64(json.dumps(it))}")
            play.append("#".join(a))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        body = f"keywords={key}&type_id=0&page={pg}"
        data = self.getdata("/api.php/getappapi.index/searchList", body)
        result = {"list": data["search_list"], "page": pg}
        return result

    def playerContent(self, flag, id, vipFlags):
        ids = json.loads(self.d64(id))
        h = {"User-Agent": (ids['user_agent'] or "okhttp/3.14.9")}
        try:
            if re.search(r'url=', ids['parse_api_url']):
                data = self.net.json(ids['parse_api_url'], {'headers': h, 'timeout': 10000})
                url = data.get('url') or data['data'].get('url')
            else:
                body = f"parse_api={ids.get('parse') or ids['parse_api_url'].replace(ids['url'], '')}&url={quote(self.aes(ids['url'], True))}&token={ids.get('token')}"
                b = self.getdata("/api.php/getappapi.index/vodParse", body)['json']
                url = json.loads(b)['url']
                if 'error' in url: raise ValueError(f"解析失败: {url}")
            p = 0
        except Exception as e:
            print('错误信息：', e)
            url, p = ids['url'], 1

        if re.search(r'\.jpg|\.png|\.jpeg', url):
            url = self.Mproxy(url)
        result = {}
        result["parse"] = p
        result["url"] = url
        result["header"] = h
        return result

    def proxy(self, params):
        return self.Mlocal(params)

    def gethost(self):
        headers = {
            'User-Agent': 'okhttp/3.14.9'
        }
        host = (self.net.req('https://jingyu-1312635929.cos.ap-nanjing.myqcloud.com/1.json', {'headers': headers}))['content'].strip()
        return host

    phend = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)',
        'allowCrossProtocolRedirects': 'true'
    }

    def aes(self, operation, text):
        key = "4d83b87c4c5ea111".encode("utf-8")
        iv = key
        if operation == "encrypt":
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
            ct = b64encode(ct_bytes).decode("utf-8")
            return ct
        elif operation == "decrypt":
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size)
            return pt.decode("utf-8")

    def header(self):
        t = str(int(time.time()))
        header = {"Referer":self.host,
            "User-Agent": "okhttp/3.14.9", "app-version-code": "300", "app-ui-mode": "light",
                  "app-api-verify-time": t, "app-user-device-id": self.md5(t),
                  "app-api-verify-sign": self.aes("encrypt", t),
                  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        return header

    def getdata(self, path, data=None):
        options = {"headers": self.header(), "method": "POST", "timeout": 10000}
        if data is not None:
            options["body"] = data
        vdata = self.net.json(f"{self.host}{path}", options)['data']
        data1 = self.aes("decrypt", vdata)
        return json.loads(data1)

    def Mproxy(self, url):
        return self.getProxyUrl({"url": b64encode(url.encode('utf-8')).decode('utf-8'), "type": "m3u8"})

    def Mlocal(self, param,header=None):
        url = self.d64(param["url"])
        ydata = self.net.req(url, {'headers': header, "redirect": 0, "buffer": 3})
        if ydata.get("error"):
            raise RuntimeError(ydata["error"])
        if 300 <= ydata["code"] < 400:
            location = next((value for name, value in ydata["headers"].items() if name.lower() == "location"), None)
            if isinstance(location, list):
                location = location[0] if location else None
            if not location:
                raise RuntimeError(f"HTTP {ydata['code']} response has no Location header")
            url = location
            ydata = self.net.req(url, {'headers': header, "buffer": 3})
        if ydata.get("error"):
            raise RuntimeError(ydata["error"])
        if not 200 <= ydata["code"] < 300:
            raise RuntimeError(f"HTTP {ydata['code']}")
        data = ydata["content"].decode('utf-8')
        parsed_url = urlparse(url)
        durl = parsed_url.scheme + "://" + parsed_url.netloc
        lines = data.strip().split('\n')
        for index, string in enumerate(lines):
            if '#EXT' not in string and 'http' not in string:
                last_slash_index = string.rfind('/')
                lpath = string[:last_slash_index + 1]
                lines[index] = durl + ('' if lpath.startswith('/') else '/') + lpath
        data = '\n'.join(lines)
        return [200, "application/vnd.apple.mpegur", data]

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self,encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()
