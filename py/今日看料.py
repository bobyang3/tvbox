# -*- coding: utf-8 -*-
# 🌈 Love 
import json
import random
import re
import sys
import threading
import time
import requests
from base64 import b64decode, b64encode
from urllib.parse import urlparse, quote

from pyquery import PyQuery as pq
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):

    def init(self, extend=""):
        try:self.proxies = json.loads(extend)
        except:self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        # Use working dynamic URLs directly
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        self.log(f"使用站点: {self.host}")
        print(f"使用站点: {self.host}")
        pass


    def isVideoFormat(self, url):
        # Treat direct media formats as playable without parsing
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
                
            data = self.getpq(response.text)
            result = {}
            classes = []
            
            # 优先从导航栏获取分类
            nav_selectors = [
                '#navbarCollapse .navbar-nav .nav-item .nav-link',
                '.navbar-nav .nav-item .nav-link',
                '#nav .menu-item a',
                '.menu .menu-item a'
            ]
            
            found_categories = False
            for selector in nav_selectors:
                for item in data(selector).items():
                    href = item.attr('href') or ''
                    name = item.text().strip()
                    
                    # 过滤掉非分类链接
                    if (not href or not name or 
                        href == '#' or 
                        href.startswith('http') or
                        'about' in href.lower() or
                        'contact' in href.lower() or
                        'tags' in href.lower() or
                        'top' in href.lower() or
                        'start' in href.lower() or
                        'time' in href.lower()):
                        continue
                    
                    # 确保是分类链接（包含category或明确的分类路径）
                    if '/category/' in href or any(cat in href for cat in ['/dy/', '/ks/', '/douyu/', '/hy/', '/hj/', '/tt/', '/wh/', '/asmr/', '/xb/', '/xsp/', '/rdgz/']):
                        # 处理相对路径
                        if href.startswith('/'):
                            type_id = href
                        else:
                            type_id = f'/{href}'
                            
                        classes.append({
                            'type_name': name,
                            'type_id': type_id
                        })
                        found_categories = True
            
            # 如果导航栏没找到，尝试从分类下拉菜单获取
            if not found_categories:
                category_selectors = [
                    '.category-list a',
                    '.slide-toggle + .category-list a',
                    '.menu .category-list a'
                ]
                for selector in category_selectors:
                    for item in data(selector).items():
                        href = item.attr('href') or ''
                        name = item.text().strip()
                        
                        if href and name and href != '#':
                            if href.startswith('/'):
                                type_id = href
                            else:
                                type_id = f'/{href}'
                                
                            classes.append({
                                'type_name': name,
                                'type_id': type_id
                            })
                            found_categories = True
            
            # 去重
            unique_classes = []
            seen_ids = set()
            for cls in classes:
                if cls['type_id'] not in seen_ids:
                    unique_classes.append(cls)
                    seen_ids.add(cls['type_id'])
            
            # 如果没有找到分类，创建默认分类
            if not unique_classes:
                unique_classes = [
                    {'type_name': '热点关注', 'type_id': '/category/rdgz/'},
                    {'type_name': '抖音', 'type_id': '/category/dy/'},
                    {'type_name': '快手', 'type_id': '/category/ks/'},
                    {'type_name': '斗鱼', 'type_id': '/category/douyu/'},
                    {'type_name': '虎牙', 'type_id': '/category/hy/'},
                    {'type_name': '花椒', 'type_id': '/category/hj/'},
                    {'type_name': '推特', 'type_id': '/category/tt/'},
                    {'type_name': '网红', 'type_id': '/category/wh/'},
                    {'type_name': 'ASMR', 'type_id': '/category/asmr/'},
                    {'type_name': 'X播', 'type_id': '/category/xb/'},
                    {'type_name': '小视频', 'type_id': '/category/xsp/'}
                ]
            
            result['class'] = unique_classes
            result['list'] = self.getlist(data('#index article a, #archive article a'))
            return result
            
        except Exception as e:
            print(f"homeContent error: {e}")
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article a, #archive article a'))}
        except Exception as e:
            print(f"homeVideoContent error: {e}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            # 修复URL构建 - 去除多余的斜杠
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"分类页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"分类页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # 如果没有找到视频，尝试其他选择器
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个视频")
            
            # 改进的页数检测逻辑
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def tagContent(self, tid, pg, filter, extend):
        """标签页面内容"""
        try:
            # 修复URL构建 - 去除多余的斜杠
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"标签页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"标签页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # 如果没有找到视频，尝试其他选择器
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个标签相关视频")
            
            # 页数检测
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"tagContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def detect_page_count(self, data, current_page):
        """改进的页数检测方法"""
        pagecount = 99999  # 默认大数字，允许无限翻页
        
        # 方法1: 检查分页器中的所有页码链接
        page_numbers = []
        
        # 查找所有可能的页码链接
        page_selectors = [
            '.page-navigator a',
            '.pagination a', 
            '.pages a',
            '.page-numbers a'
        ]
        
        for selector in page_selectors:
            for page_link in data(selector).items():
                href = page_link.attr('href') or ''
                text = page_link.text().strip()
                
                # 从href中提取页码
                if href:
                    # 匹配 /category/dy/2/ 这种格式
                    match = re.search(r'/(\d+)/?$', href.rstrip('/'))
                    if match:
                        page_num = int(match.group(1))
                        if page_num not in page_numbers:
                            page_numbers.append(page_num)
                
                # 从文本中提取数字页码
                if text and text.isdigit():
                    page_num = int(text)
                    if page_num not in page_numbers:
                        page_numbers.append(page_num)
        
        # 如果有找到页码，取最大值
        if page_numbers:
            max_page = max(page_numbers)
            print(f"从分页器检测到最大页码: {max_page}")
            return max_page
        
        # 方法2: 检查是否存在"下一页"按钮
        next_selectors = [
            '.page-navigator .next',
            '.pagination .next',
            '.next-page',
            'a:contains("下一页")'
        ]
        
        for selector in next_selectors:
            if data(selector):
                print("检测到下一页按钮，允许继续翻页")
                return 99999
        
        # 方法3: 如果当前页视频数量很少，可能没有下一页
        if len(data('#archive article, #index article, .post-card')) < 5:
            print("当前页内容较少，可能没有下一页")
            return int(current_page)
        
        print("使用默认页数: 99999")
        return 99999

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
            url = f"{self.host}{video_id}" if not video_id.startswith('http') else video_id
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [{'vod_play_from': '今日看料', 'vod_play_url': f'页面加载失败${url}'}]}
                
            data = self.getpq(response.text)
            vod = {'vod_play_from': '今日看料'}
            
            # 获取标题
            title_selectors = ['.post-title', 'h1.entry-title', 'h1', '.post-card-title']
            for selector in title_selectors:
                title_elem = data(selector)
                if title_elem:
                    vod['vod_name'] = title_elem.text().strip()
                    break
            
            if 'vod_name' not in vod:
                vod['vod_name'] = '今日看料视频'
            
            # 获取内容/描述
            try:
                clist = []
                if data('.tags .keywords a'):
                    for k in data('.tags .keywords a').items():
                        title = k.text()
                        href = k.attr('href')
                        if title and href:
                            # 使href相对路径
                            if href.startswith(self.host):
                                href = href.replace(self.host, '')
                            clist.append('[a=cr:' + json.dumps({'id': href, 'name': title}) + '/]' + title + '[/a]')
                vod['vod_content'] = ' '.join(clist) if clist else data('.post-content').text() or vod['vod_name']
            except:
                vod['vod_content'] = vod['vod_name']
            
            # 获取视频URLs
            try:
                plist = []
                used_names = set()
                
                # 查找DPlayer视频
                if data('.dplayer'):
                    for c, k in enumerate(data('.dplayer').items(), start=1):
                        config_attr = k.attr('data-config')
                        if config_attr:
                            try:
                                config = json.loads(config_attr)
                                video_url = config.get('video', {}).get('url', '')
                                if video_url:
                                    name = f"视频{c}"
                                    count = 2
                                    while name in used_names:
                                        name = f"视频{c}_{count}"
                                        count += 1
                                    used_names.add(name)
                                    self.log(f"解析到视频: {name} -> {video_url}")
                                    print(f"解析到视频: {name} -> {video_url}")
                                    plist.append(f"{name}${video_url}")
                            except:
                                continue
                
                # 查找视频标签
                if not plist:
                    video_selectors = ['video source', 'video', 'iframe[src*="video"]', 'a[href*=".m3u8"]', 'a[href*=".mp4"]']
                    for selector in video_selectors:
                        for c, elem in enumerate(data(selector).items(), start=1):
                            src = elem.attr('src') or elem.attr('href') or ''
                            if src and any(ext in src for ext in ['.m3u8', '.mp4', 'video']):
                                name = f"视频{c}"
                                count = 2
                                while name in used_names:
                                    name = f"视频{c}_{count}"
                                    count += 1
                                used_names.add(name)
                                plist.append(f"{name}${src}")
                
                if plist:
                    self.log(f"拼装播放列表，共{len(plist)}个")
                    print(f"拼装播放列表，共{len(plist)}个")
                    vod['vod_play_url'] = '#'.join(plist)
                else:
                    vod['vod_play_url'] = f"正片${url}"
                    
            except Exception as e:
                print(f"视频解析错误: {e}")
                vod['vod_play_url'] = f"正片${url}"
                
            return {'list': [vod]}
            
        except Exception as e:
            print(f"detailContent error: {e}")
            return {'list': [{'vod_play_from': '今日看料', 'vod_play_url': f'详情页加载失败${video_id if video_id else ""}'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            # 优先使用标签搜索
            encoded_key = quote(key)
            url = f"{self.host}/tag/{encoded_key}/{pg}" if pg != "1" else f"{self.host}/tag/{encoded_key}/"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                # 尝试搜索页面
                url = f"{self.host}/search/{encoded_key}/{pg}" if pg != "1" else f"{self.host}/search/{encoded_key}/"
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [], 'page': pg}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'))
            
            # 使用改进的页数检测方法
            pagecount = self.detect_page_count(data, pg)
            
            return {'list': videos, 'page': pg, 'pagecount': pagecount}
            
        except Exception as e:
            print(f"searchContent error: {e}")
            return {'list': [], 'page': pg}

    def getTagsContent(self, pg="1"):
        """获取标签页面内容"""
        try:
            url = f"{self.host}/tags.html"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [], 'page': pg}
                
            data = self.getpq(response.text)
            tags = []
            
            # 从标签页面提取所有标签 - 使用更宽松的选择器
            for tag_elem in data('a[href*="/tag/"]').items():
                tag_name = tag_elem.text().strip()
                tag_href = tag_elem.attr('href') or ''
                
                if tag_name and tag_href and '/tag/' in tag_href and tag_name != '全部标签':  # 排除标题链接
                    # 处理为相对路径
                    tag_id = tag_href.replace(self.host, '')
                    if not tag_id.startswith('/'):
                        tag_id = '/' + tag_id
                    
                    tags.append({
                        'vod_id': tag_id,
                        'vod_name': f"🏷️ {tag_name}",
                        'vod_pic': '',
                        'vod_remarks': '标签',
                        'vod_tag': 'tag',
                        'style': {"type": "rect", "ratio": 1.33}
                    })
            
            print(f"找到 {len(tags)} 个标签")
            
            # 分页处理 - 标签页面通常不需要分页
            result = {}
            result['list'] = tags
            result['page'] = pg
            result['pagecount'] = 1  # 标签页面通常只有一页
            result['limit'] = 999
            result['total'] = len(tags)
            return result
            
        except Exception as e:
            print(f"getTagsContent error: {e}")
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        url = id
        p = 1
        if self.isVideoFormat(url):
            if '.m3u8' in url:
                url = self._proxy_url(url)
            p = 0
        self.log(f"播放请求: parse={p}, url={url}")
        print(f"播放请求: parse={p}, url={url}")
        return {'parse': p, 'url': url, 'header': self.headers}

    def proxy(self, params):
        try:
            if params.get('type') == 'img':
                img_url = self.d64(params['url'])
                if not img_url.startswith(('http://', 'https://')):
                    if img_url.startswith('/'):
                        img_url = f"{self.host}{img_url}"
                    else:
                        img_url = f"{self.host}/{img_url}"
                
                res = requests.get(img_url, headers=self.headers, proxies=self.proxies, timeout=10)
                return [200, res.headers.get('Content-Type', 'image/jpeg'), res.content]
            elif params.get('type') == 'm3u8':
                return self.m3Proxy(params['url'])
            else:
                return self.tsProxy(params['url'])
        except Exception as e:
            print(f"localProxy error: {e}")
            return [500, "text/plain", f"Proxy error: {str(e)}".encode()]

    def _proxy_url(self, data, type='m3u8'):
        if data and len(self.proxies):
            return self.proxyUrl({"url": self.e64(data), "type": type})
        else:
            return data

    def m3Proxy(self, url):
        try:
            url = self.d64(url)
            ydata = requests.get(url, headers=self.headers, proxies=self.proxies, allow_redirects=False)
            data = ydata.content.decode('utf-8')
            if ydata.headers.get('Location'):
                url = ydata.headers['Location']
                data = requests.get(url, headers=self.headers, proxies=self.proxies).content.decode('utf-8')
            lines = data.strip().split('\n')
            last_r = url[:url.rfind('/')]
            parsed_url = urlparse(url)
            durl = parsed_url.scheme + "://" + parsed_url.netloc
            iskey = True
            for index, string in enumerate(lines):
                if iskey and 'URI' in string:
                    pattern = r'URI="([^"]*)"'
                    match = re.search(pattern, string)
                    if match:
                        lines[index] = re.sub(pattern, f'URI="{self._proxy_url(match.group(1), "mkey")}"', string)
                        iskey = False
                        continue
                if '#EXT' not in string:
                    if 'http' not in string:
                        domain = last_r if string.count('/') < 2 else durl
                        string = domain + ('' if string.startswith('/') else '/') + string
                    lines[index] = self._proxy_url(string, string.split('.')[-1].split('?')[0])
            data = '\n'.join(lines)
            return [200, "application/vnd.apple.mpegur", data]
        except Exception as e:
            print(f"m3Proxy error: {e}")
            return [500, "text/plain", f"m3u8 proxy error: {str(e)}".encode()]

    def tsProxy(self, url):
        try:
            url = self.d64(url)
            data = requests.get(url, headers=self.headers, proxies=self.proxies, stream=True)
            return [200, data.headers.get('Content-Type', 'video/mp2t'), data.content]
        except Exception as e:
            print(f"tsProxy error: {e}")
            return [500, "text/plain", f"ts proxy error: {str(e)}".encode()]

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def get_working_host(self):
        """Get working host from known dynamic URLs"""
        dynamic_urls = [
            'https://kanliao2.one/',
            'https://kanliao7.org/',
            'https://kanliao7.net/',
            'https://kanliao14.com/'
        ]
        
        for url in dynamic_urls:
            try:
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                if response.status_code == 200:
                    data = self.getpq(response.text)
                    articles = data('#index article a, #archive article a')
                    if len(articles) > 0:
                        self.log(f"选用可用站点: {url}")
                        print(f"选用可用站点: {url}")
                        return url
            except Exception as e:
                continue
        
        self.log(f"未检测到可用站点，回退: {dynamic_urls[0]}")
        print(f"未检测到可用站点，回退: {dynamic_urls[0]}")
        return dynamic_urls[0]

    def getlist(self, data, tid=''):
        videos = []
        for k in data.items():
            a = k.attr('href')
            b = k('h2').text() or k('.post-card-title').text() or k('.entry-title').text() or k.text()
            c = k('span[itemprop="datePublished"]').text() or k('.post-meta, .entry-meta, time, .post-card-info').text()
            
            # 过滤广告：检查是否包含"热搜HOT"标志
            if self.is_advertisement(k):
                print(f"过滤广告: {b}")
                continue
                
            if a and b and b.strip():
                # 处理相对路径
                if not a.startswith('http'):
                    if a.startswith('/'):
                        vod_id = a
                    else:
                        vod_id = f'/{a}'
                else:
                    vod_id = a
                    
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': b.replace('\n', ' ').strip(),
                    'vod_pic': self.get_article_img(k),
                    'vod_remarks': c.strip() if c else '',
                    'vod_tag': '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def is_advertisement(self, article_elem):
        """判断是否为广告（包含热搜HOT标志）"""
        # 检查.wraps元素是否包含"热搜HOT"文本
        hot_elements = article_elem.find('.wraps')
        for elem in hot_elements.items():
            if '热搜HOT' in elem.text():
                return True
        
        # 检查标题是否包含广告关键词
        title = article_elem('h2').text() or article_elem('.post-card-title').text() or ''
        ad_keywords = ['热搜HOT', '手机链接', 'DNS设置', '修改DNS', 'WIFI设置']
        if any(keyword in title for keyword in ad_keywords):
            return True
            
        # 检查背景颜色是否为广告特有的渐变背景
        style = article_elem.attr('style') or ''
        if 'background:' in style and any(gradient in style for gradient in ['-webkit-linear-gradient', 'linear-gradient']):
            # 进一步检查是否包含特定的广告颜色组合
            ad_gradients = ['#ec008c,#fc6767', '#ffe259,#ffa751']
            if any(gradient in style for gradient in ad_gradients):
                return True
                
        return False

    def get_article_img(self, article_elem):
        """从文章元素中提取图片，多种方式尝试"""
        # 方式1: 从script标签中提取loadBannerDirect
        script_text = article_elem('script').text()
        if script_text:
            match = re.search(r"loadBannerDirect\('([^']+)'", script_text)
            if match:
                url = match.group(1)
                if not url.startswith(('http://', 'https://')):
                    if url.startswith('/'):
                        url = f"{self.host}{url}"
                    else:
                        url = f"{self.host}/{url}"
                return self.proxyUrl({"url": self.e64(url), "type": "img"})
        
        # 方式2: 从背景图片中提取
        bg_elem = article_elem.find('.blog-background')
        if bg_elem:
            style = bg_elem.attr('style') or ''
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style)
            if bg_match:
                img_url = bg_match.group(1)
                if img_url and not img_url.startswith('data:'):
                    if not img_url.startswith(('http://', 'https://')):
                        if img_url.startswith('/'):
                            img_url = f"{self.host}{img_url}"
                        else:
                            img_url = f"{self.host}/{img_url}"
                    return self.proxyUrl({"url": self.e64(img_url), "type": "img"})
        
        # 方式3: 从图片标签中提取
        img_elem = article_elem.find('img')
        if img_elem:
            data_src = img_elem.attr('data-src')
            if data_src:
                if not data_src.startswith(('http://', 'https://')):
                    if data_src.startswith('/'):
                        data_src = f"{self.host}{data_src}"
                    else:
                        data_src = f"{self.host}/{data_src}"
                return self.proxyUrl({"url": self.e64(data_src), "type": "img"})
            
            src = img_elem.attr('src')
            if src:
                if not src.startswith(('http://', 'https://')):
                    if src.startswith('/'):
                        src = f"{self.host}{src}"
                    else:
                        src = f"{self.host}/{src}"
                return self.proxyUrl({"url": self.e64(src), "type": "img"})
        
        return ''

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))