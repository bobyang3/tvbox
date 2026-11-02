# -*- coding: utf-8 -*-
import re
from base.spider import Spider as BaseSpider
class Spider(BaseSpider):
    def init(self, extend=""):
        self.base, self.headers = "https://chaturbate.com", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        return self
    def homeContent(self, filter):
        return {"class": [{"type_id": "f", "type_name": "女性"}, {"type_id": "m", "type_name": "男性"}, {"type_id": "c", "type_name": "情侣"}]}
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if pg else 0
        gender = {"f": "f", "m": "m", "c": "c"}.get(tid, "")
        url = f"{self.base}/api/ts/roomlist/room-list/?enable_recommendations=false&genders={gender}&limit=90&offset={pg*90}"
        data = self.net.json(url, {"headers": self.headers, "timeout": 5000})
        total = data.get("total_count", 0)
        videos = [
            {"vod_id": r["username"], "vod_pic": r.get("img", ""), "vod_remarks": "",
             "vod_name": f'{r["username"]}{" (" + str(r["display_age"]) + ")" if r.get("display_age") else ""}'}
            for r in data.get("rooms", [])
        ]
        return {"list": videos, "page": pg + 1, "pagecount": (total + 89) // 90, "limit": 90, "total": total}
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
        room_slug = video_id
        return {"list": [{"vod_id": room_slug, "vod_name": f"Chaturbate - {room_slug}", "vod_pic": "", 
                "vod_play_from": "老僧酿酒、名妓读经", "vod_play_url": f"书生玩剣、将军作文${room_slug}"}]}
    def playerContent(self, flag, id, vipFlags):
        url, data, headers = "https://chaturbate.com/get_edge_hls_url_ajax/", {"room_slug": id}, {"X-Requested-With": "XMLHttpRequest"}
        try:
            play_url = self.net.json(url, {
                "method": "POST",
                "postType": "form",
                "data": data,
                "headers": headers,
                "timeout": 5000,
            }).get("url", id)
        except Exception:
            play_url = id
        return {"parse": 0, "playUrl": "", "url": play_url, "header": headers}

    def searchContent(self, key, quick, pg="1"):
        pg = int(pg) if pg else 0
        url_api = f"{self.base}/api/ts/roomlist/room-list/?enable_recommendations=false&limit=90&offset={pg*90}&query={key}"
        data = self.net.json(url_api, {"headers": self.headers, "timeout": 5000})
        videos = [
            {"vod_id": r["username"], "vod_pic": r.get("img", ""), "vod_remarks": "",
             "vod_name": f'{r["username"]}{" (" + str(r["display_age"]) + ")" if r.get("display_age") else ""}'}
            for r in data.get("rooms", [])
        ]
        return {"list": videos}

    def isVideoFormat(self, url): return ".m3u8" in url
    def manualVideoCheck(self): return True