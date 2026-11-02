#coding=utf-8
#!/usr/bin/python
import sys
import json
import time
from uuid import uuid4
from urllib.parse import quote

from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
	def _clean_text(self, text):
		return (text or '').replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()


	def init(self, extend):
		try:
			extendDict = json.loads(extend)
			self.baseUrl = extendDict['server'].strip('/')
			self.username = extendDict['username']
			self.password = extendDict['password']
			self.thread = extendDict['thread'] if 'thread' in extendDict else 0
		except:
			self.baseUrl = ''
			self.username = ''
			self.password = ''
			self.thread = 0

	def destroy(self):
		pass

	def isVideoFormat(self, url):
		pass

	def manualVideoCheck(self):
		pass

	def homeContent(self, filter):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Views"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		data = self.net.json(url, {
			"params": params, "headers": header, "timeout": 30000,
		})
		typeInfos = data["Items"]
		classList = []
		for typeInfo in typeInfos:
			if "播放列表" in typeInfo['Name'] or '相机' in typeInfo['Name']:
				continue
			classList.append({"type_name": typeInfo['Name'], "type_id": typeInfo['Id']})
		result = {'class': classList}
		return result

	def homeVideoContent(self):
		return {}

	def categoryContent(self, cid, page, filter, ext):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		result = {}
		page = int(page)
		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken'],
			"SortBy": "DateLastContentAdded,SortName",
			"IncludeItemTypes": "Movie,Series",
			"SortOrder": "Descending",
			"ParentId": cid,
			"Recursive": "true",
			"Limit": "30",
			"ImageTypeLimit": 1,
			"StartIndex": str((page - 1) * 30),
			"EnableImageTypes": "Primary,Backdrop,Thumb,Banner",
			"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating,Status,CriticRating,EndDate,Path",
			"EnableUserData": "true"
		}
		data = self.net.json(url, {
			"params": params, "headers": header, "timeout": 30000,
		})
		videoList = data['Items']
		videos = []
		for video in videoList:
			name = self._clean_text(video['Name'])
			videos.append({
				"vod_id": video['Id'],
				"vod_name": name,
				"vod_pic": f"{self.baseUrl}/emby/Items/{video['Id']}/Images/Primary?maxWidth=400&tag={video['ImageTags']['Primary']}&quality=90" if 'Primary' in video['ImageTags'] else '',
				"vod_remarks": video['ProductionYear'] if 'ProductionYear' in video else ''
			})
		result['list'] = videos
		result['page'] = page
		total = int(data.get('TotalRecordCount', 0))
		result['pagecount'] = page + 1 if page * 30 < total else page
		result['limit'] = len(videos)
		result['total'] = total
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
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items/{video_id}"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		videoInfos_response = self.net.req(url, {
			"params": params, "headers": header, "timeout": 30000,
		})
		if videoInfos_response.get("error"):
			raise RuntimeError(videoInfos_response["error"])
		videoInfos = json.loads(videoInfos_response["content"])
		vod = {
			"vod_id": video_id,
			"vod_name": videoInfos['Name'],
			"vod_pic": f'{self.baseUrl}/emby/Items/{video_id}/Images/Primary?maxWidth=400&tag={videoInfos["ImageTags"]["Primary"]}&quality=90' if 'Primary' in videoInfos['ImageTags'] else '',
			"type_name": videoInfos['Genres'][0] if len(videoInfos['Genres']) > 0 else '',
			"vod_year": videoInfos['ProductionYear'] if 'ProductionYear' in videoInfos else '',
			"vod_content": videoInfos['Overview'].replace('\xa0', ' ').replace('\n\n', '\n').strip() if 'Overview' in videoInfos else '',
			"vod_play_from": "EMBY"
		}
		playUrl = ''
		if not videoInfos['IsFolder']:
			playUrl += f"{videoInfos['Name'].strip()}${videoInfos['Id']}#"
		else:
			url = f"{self.baseUrl}/emby/Shows/{video_id}/Seasons"
			params.update(
				{
					"UserId": embyInfos['User']['Id'],
					"EnableImages": "true",
					"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating",
					"EnableUserData": "true",
					"EnableTotalRecordCount": "false"
				}
			)
			seasons_response = self.net.req(url, {
				"params": params, "headers": header, "timeout": 30000,
			})
			if seasons_response.get("error"):
				raise RuntimeError(seasons_response["error"])
			if seasons_response["code"] == 200:
				playInfos = json.loads(seasons_response["content"])['Items']
				for playInfo in playInfos:
					url = f"{self.baseUrl}/emby/Shows/{playInfo['Id']}/Episodes"
					params.update(
						{
							"SeasonId": playInfo['Id'],
							"Fields": "BasicSyncInfo,CanDelete,CommunityRating,PrimaryImageAspectRatio,ProductionYear,Overview"
						}
					)
					videoList = self.net.json(url, {
						"params": params, "headers": header, "timeout": 30000,
					})['Items']
					for video in videoList:
						playUrl += f"{playInfo['Name'].replace('#', '-').replace('$', '|').strip()}|{video['Name'].strip()}${video['Id']}#"
			else:
				url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
				params = {
					"ParentId": video_id,
					"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating,CriticRating",
					"ImageTypeLimit": "1",
					"StartIndex": "0",
					"EnableUserData": "true",
					"X-Emby-Client": embyInfos['SessionInfo']['Client'],
					"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
					"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
					"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
					"X-Emby-Token": embyInfos['AccessToken']
				}
				videoList = self.net.json(url, {
					"params": params, "headers": header, "timeout": 30000,
				})['Items']
				for video in videoList:
					playUrl += f"{video['Name'].replace('#', '-').replace('$', '|').strip()}${video['Id']}#"
		vod['vod_play_url'] = playUrl.strip('#')
		result = {'list': [vod]}
		return result

	def searchContent(self, key, quick, pg="1"):
		return self.searchContentPage(key, quick, pg)

	def searchContentPage(self, keywords, quick, page):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}
		page = int(page)
		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken'],
			"SortBy": "SortName",
			"SortOrder": "Ascending",
			"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,Status,EndDate",
			"StartIndex": str(((page-1)*50)),
			"EnableImageTypes": "Primary,Backdrop,Thumb",
			"ImageTypeLimit": "1",
			"Recursive": "true",
			"SearchTerm": keywords,
			"IncludeItemTypes": "Movie,Series,BoxSet",
			"GroupProgramsBySeries": "true",
			"Limit": "50",
			"EnableTotalRecordCount": "true"
		}
		data = self.net.json(url, {
			"params": params, "headers": header, "timeout": 30000,
		})

		videos = []
		vodList = data['Items']
		for vod in vodList:
			sid = vod['Id']
			name = self._clean_text(vod['Name'])
			pic = f'{self.baseUrl}/emby/Items/{sid}/Images/Primary?maxWidth=400&tag={vod["ImageTags"]["Primary"]}&quality=90' if 'Primary' in vod["ImageTags"] else ''
			videos.append({
				"vod_id": sid,
				"vod_name": name,
				"vod_pic": pic,
				"vod_remarks": vod['ProductionYear'] if 'ProductionYear' in vod else ''
			})
		result = {'list': videos}
		return result

	def playerContent(self, flag, pid, vipFlags):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Items/{pid}/PlaybackInfo"
		params = {
			"UserId": embyInfos['User']['Id'],
			"IsPlayback": "false",
			"AutoOpenLiveStream": "false",
			"StartTimeTicks": 0,
			"MaxStreamingBitrate": "2147483647",
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		data = "{\"DeviceProfile\":{\"SubtitleProfiles\":[{\"Method\":\"Embed\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"Embed\"},{\"Format\":\"subrip\",\"Method\":\"Embed\"},{\"Format\":\"sub\",\"Method\":\"Embed\"},{\"Method\":\"Embed\",\"Format\":\"pgssub\"},{\"Format\":\"subrip\",\"Method\":\"External\"},{\"Method\":\"External\",\"Format\":\"sub\"},{\"Method\":\"External\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"External\"},{\"Method\":\"External\",\"Format\":\"vtt\"},{\"Method\":\"External\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"External\"}],\"CodecProfiles\":[{\"Codec\":\"h264\",\"Type\":\"Video\",\"ApplyConditions\":[{\"Property\":\"IsAnamorphic\",\"Value\":\"true\",\"Condition\":\"NotEquals\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"high|main|baseline|constrained baseline\",\"Condition\":\"EqualsAny\",\"Property\":\"VideoProfile\"},{\"IsRequired\":false,\"Value\":\"80\",\"Condition\":\"LessThanEqual\",\"Property\":\"VideoLevel\"},{\"IsRequired\":false,\"Value\":\"true\",\"Condition\":\"NotEquals\",\"Property\":\"IsInterlaced\"}]},{\"Codec\":\"hevc\",\"ApplyConditions\":[{\"Property\":\"IsAnamorphic\",\"Value\":\"true\",\"Condition\":\"NotEquals\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"high|main|main 10\",\"Condition\":\"EqualsAny\",\"Property\":\"VideoProfile\"},{\"Property\":\"VideoLevel\",\"Value\":\"175\",\"Condition\":\"LessThanEqual\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"true\",\"Condition\":\"NotEquals\",\"Property\":\"IsInterlaced\"}],\"Type\":\"Video\"}],\"MaxStreamingBitrate\":40000000,\"TranscodingProfiles\":[{\"Container\":\"ts\",\"AudioCodec\":\"aac,mp3,wav,ac3,eac3,flac,opus\",\"VideoCodec\":\"hevc,h264,mpeg4\",\"BreakOnNonKeyFrames\":true,\"Type\":\"Video\",\"MaxAudioChannels\":\"6\",\"Protocol\":\"hls\",\"Context\":\"Streaming\",\"MinSegments\":2}],\"DirectPlayProfiles\":[{\"Container\":\"mov,mp4,mkv,hls,webm\",\"Type\":\"Video\",\"VideoCodec\":\"h264,hevc,dvhe,dvh1,h264,hevc,hev1,mpeg4,vp9\",\"AudioCodec\":\"aac,mp3,wav,ac3,eac3,flac,truehd,dts,dca,opus,pcm,pcm_s24le\"}],\"ResponseProfiles\":[{\"MimeType\":\"video/mp4\",\"Type\":\"Video\",\"Container\":\"m4v\"}],\"ContainerProfiles\":[],\"MusicStreamingTranscodingBitrate\":40000000,\"MaxStaticBitrate\":40000000}}"
		playback_info = self.net.json(url, {
			"method": "POST", "params": params, "body": data,
			"headers": header, "timeout": 30000,
		})
		url = self.baseUrl + playback_info['MediaSources'][0]['DirectStreamUrl']
		if int(self.thread) > 0:
			proxy_health = self.net.req('http://127.0.0.1:7777', {"timeout": 1000})
			if proxy_health.get("error") or not 200 <= proxy_health["code"] < 400:
				fallback_health = self.net.req('http://127.0.0.1:9978/go', {"timeout": 10000})
				if fallback_health.get("error") or not 200 <= fallback_health["code"] < 400:
					raise RuntimeError("Neither local playback proxy is available")
			url = f'http://127.0.0.1:7777/?url={quote(url)}&thread={self.thread}'
		result = {
			"url": url,
			"header": self.header,
			"parse": 0
		}
		return result


	def getAccessToken(self):
		embyInfos = getattr(self, "_emby_infos", None)
		if embyInfos:
			return embyInfos

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		embyInfos = self.net.json(
			f"{self.baseUrl}/emby/Users/AuthenticateByName",
			{
				"method": "POST",
				"params": {
					"Username": self.username, "Password": self.password,
					"Pw": self.password, "X-Emby-Client": "Yamby",
					"X-Emby-Device-Name": "Yamby", "X-Emby-Device-Id": str(uuid4()),
					"X-Emby-Client-Version": "1.0.2",
				},
				"headers": header, "timeout": 30000,
			}
		)
		self._emby_infos = embyInfos
		return embyInfos

	header = {"User-Agent": "Yamby/1.0.2(Android"}
