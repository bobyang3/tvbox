var rule = {
    title: '地瓜视频',
    "author": "xxxxx",
    host: 'https://www.112vv.cc',
    url: '/vodtype/fyclass-fypage.html',
    class_name: '国产视频&国产自拍&国产偷拍&网红主播&国产探花&清纯学生&少妇淫妻&明星换脸&国产传媒&亚洲专区&日韩无码&欧美无码&中文字幕&三级伦理&卡通动漫&巨乳美乳&强奸乱伦&制服丝袜&少女萝莉&人妻熟女&群交口交&日本素人&高清名优&男同女同', //静态分类名称拼接
    class_url: '6&7&8&9&36&10&21&11&12&22&23&24&25&26&27&28&29&30&31&32&33&37&38&39',
    searchUrl: '/vodsearch/**-/page/fypage.html',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: '',
    filter_url: '',
    filter_def: {},
    headers: {
        'User-Agent': 'MOBILE_UA'
    },

    timeout: 5000,
    //class_parse: 'body&&.sou-tag,0&&.sou-tag;a&&Text;a&&href',
    cate_exclude: '',
    play_parse: true,
    lazy:`js:
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		var url = html.url;
		if (html.encrypt == '1') {
			url = unescape(url)
		} else if (html.encrypt == '2') {
			url = unescape(base64Decode(url))
		}
		if (/\\.m3u8|\\.mp4/.test(url)) {
			input = {
				jx: 0,
				url: url,
				parse: 0
			}
		} else {
			input
		}
	`,
    double: true,
    limit: 6,
    //推荐: '.row&&dl;h5&&Text;.nature&&data-original;;a&&href',
    一级: ".row-m-space8&&li;a&&title;img&&src;.item-auxiliary&&Text;a&&href",
    二级:"*",
    搜索: '.row-m-space8&&li;*;*;*;*',
}
