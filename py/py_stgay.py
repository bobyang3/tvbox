# coding=utf-8
# !/usr/bin/python
import sys
from base.spider import Spider
from pyquery import PyQuery as pq
from urllib.parse import quote, unquote
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
sys.path.append('..') 

class Spider(Spider):
    def init(self, extend="{}"):
        self.host = "https://stgay.com"
        self.headers = {
            'Referer': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
        }
        self.session = self.net.session()

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        if getattr(self, "session", None):
            self.session.close()

    def homeContent(self, filter):
        rsp = self.getpq('all/play')
        CLASSES = []
        for a in rsp('#app-nav a.app-nav-item').items():
            href = a.attr('href')
            if href and '/videos/' in href:
                CLASSES.append({
                'type_name': a.text().strip(),
                'type_id': href.split('/')[-1]
            })
        filter = []
        for a in rsp('.dx-line-tab-item a').items():
            href = a.attr('href').split('/')[-1]
            if href != 'play':
                filter.append({
                    'n': a.text().strip(),
                    'v': href
                })
        return {
            'class': CLASSES,
            'filters': {'play': [{'key': 'tag', 'value': filter}]}
        }

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        type = 'all' if tid == 'play' else 'category'
        tag = extend["tag"] if 'tag' in extend else tid
        rsp = self.getpq(f'{type}/{tag}/{pg}')
        videos = []
        for item in rsp('.video-item').items():
            title_link = item.find('a.line-clamp-1')
            href = title_link.attr('href')
            text = title_link.text().strip()
            img_src = item.find('img').attr('data-src')
            duration = item.find('.flex.justify-end .text-white').text().strip()
            videos.append({
                "vod_id": href.split('/')[-1],
                "vod_name": text,
                "vod_pic": f"{self.getProxyUrl()}&type=img&url={quote(img_src)}",
                "vod_remarks": duration
            })
        pager = rsp('ul.pager.dx-pager')
        limit = int(pager.attr('data-rec-per-page'))
        total = int(pager.attr('data-rec-total'))
        return {
            "list": videos,
            "page": pg,
            "pagecount": (total + limit - 1) // limit,
            "limit": limit,
            "total": total
        }

    def detailContent(self, array):
        rsp = self.getpq(array[0])
        mse_div = rsp('#mse')
        id = mse_div.attr('data-video')
        pic = mse_div.attr('data-poster')
        url = mse_div.attr('data-url')
        vod = {
            "vod_id": id,
            "vod_name": rsp('h1.dx-title').text().encode('latin-1').decode('utf-8').strip(), 
            "vod_pic": f"{self.getProxyUrl()}&type=img&url={quote(pic)}",
            'vod_play_from': '搜同社区',
            'vod_play_url': f"{id}${quote(url)}"
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        rsp = self.getpq(f'search/{quote(key)}/{pg}')
        videos = []
        for item in rsp('.video-item').items():
            title_link = item.find('a.line-clamp-1')
            href = title_link.attr('href')
            text = title_link.text().encode('latin-1').decode('utf-8').strip()
            img_src = item.find('img').attr('data-src')
            duration = item.find('.flex.justify-end .text-white').text().strip()
            videos.append({
                "vod_id": href.split('/')[-1],
                "vod_name": text,
                "vod_pic": f"{self.getProxyUrl()}&type=img&url={quote(img_src)}",
                "vod_remarks": duration
            })
        pager = rsp('ul.pager.dx-pager')
        limit = int(pager.attr('data-rec-per-page'))
        total = int(pager.attr('data-rec-total'))
        return {
            "list": videos,
            "page": pg,
            "pagecount": (total + limit - 1) // limit,
            "limit": limit,
            "total": total
        }

    def playerContent(self, flag, id, vipFlags):
        return {
            "url": unquote(id),
            "parse": '0',
            "contentType": '',
            "header": self.headers
        }

    def proxy(self, param):
        if param['type'] == 'img':
            content = self.decrypt_img(unquote(param['url']))
            return [200, "application/octet-stream", content]
        return [404, "text/plain", ""]

    def _request(self, url, options):
        response = self.session.req(url, options)
        if response.get("error"):
            raise RuntimeError(response["error"])
        if not 200 <= response["code"] < 300:
            raise RuntimeError(f"HTTP {response['code']} while requesting {url}")
        return response

    def getpq(self, path):
        response = self._request(
            f'{self.host}/videos/{path}', {"timeout": 5000}
        )
        return pq(response["content"])
    
    def decrypt_img(self, url):
        key_str = 'f5d965df75336270'
        iv_str = '97b60394abc2fbe1'
        key = key_str.encode('utf-8')
        iv = iv_str.encode('utf-8')
        response = self._request(
            url, {"timeout": 5000, "buffer": 3}
        )
        encrypted_bytes = response["content"]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        final_data = unpad(decrypted_bytes, AES.block_size)
        return final_data
