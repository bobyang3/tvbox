# -*- coding: utf-8 -*-
# by @嗷呜
import sys
from pyquery import PyQuery as pq
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):

    def init(self, extend=""):
        pass


    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }

    host = "https://4k-av.com"

    def homeContent(self, filter):
        data=self.getpq()
        result = {}
        classes = []
        for k in list(data('#category ul li').items())[:-1]:
            classes.append({
                'type_name': k.text(),
                'type_id': k('a').attr('href')
            })
        result['class'] = classes
        result['list'] = self.getlist(data('#MainContent_scrollul ul li'),'.poster span')
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data=self.getpq(f"{tid}page-{pg}.html")
        result = {}
        result['list'] = self.getlist(data('#MainContent_newestlist .virow .NTMitem'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
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
        data=self.getpq(video_id)
        v=data('#videoinfo')
        vod = {
            'type_name': v('#MainContent_tags.tags a').text(),
            'vod_year': v('#MainContent_videodetail.videodetail a').text(),
            'vod_remarks': v('#MainContent_titleh12 h2').text(),
            'vod_content': v('p.cnline').text(),
            'vod_play_from': '4KAV',
            'vod_play_url': ''
        }
        vlist=data('#rtlist li')
        if vlist:
            c=[f"{i('span').text()}${i('a').attr('href')}" for i in list(vlist.items())[1:]]
            c.insert(0,f"{vlist.eq(0)('span').text()}${video_id}")
            vod['vod_play_url'] = '#'.join(c)
        else:
            vod['vod_play_url'] = f"{data('#tophead h1').text()}${video_id}"
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=self.getpq(f"/s?k={key}")
        return {'list':self.getlist(data('#MainContent_newestlist .virow.search .NTMitem.Main'))}

    def playerContent(self, flag, id, vipFlags):
        try:
            data=self.getpq(id)
            p,url=0,data('#MainContent_videowindow source').attr('src')
            if not url:raise Exception("未找到播放地址")
        except Exception as e:
            p,url=1,f"{self.host}{id}"
        headers = {
            'origin': self.host,
            'referer': f'{self.host}/',
            'sec-ch-ua-platform': '"macOS"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        return  {'parse': p, 'url': url, 'header': headers}


    def liveContent(self, url):
        pass

    def getlist(self,data,y='.resyear label[title="分辨率"]'):
        videos = []
        for i in data.items():
            ns = i('.title h2').text().split(' ')
            videos.append({
                'vod_id': i('.title a').attr('href'),
                'vod_name': ns[0],
                'vod_pic': i('.poster img').attr('src'),
                'vod_remarks': ns[-1] if len(ns) > 1 else '',
                'vod_year': i(y).text()
            })
        return videos

    def getpq(self, path=''):
        url=f"{self.host}{path}"
        data = self.net.req(url, {"headers": self.headers, "timeout": 5000})["content"]
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))

