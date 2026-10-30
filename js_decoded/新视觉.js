muban.mxone5.二级.desc = '.video-info-items:eq(4)&&Text;;;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text';
muban.mxone5.二级.tab_text = 'body--small&&Text';
var rule={
	title:'新视觉影视',
	模板:'mxone5',
	host:'https://kan80.app',
	hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,".go:eq(0)&&a&&href");print(src);HOST=src',
	url:'/vodshow/fyfilter.html',
   filter_url:'{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
   filter: {,
    filter_def:{
        1:{cateId:'1'},
        2:{cateId:'2'},
        3:{cateId:'3'},
        4:{cateId:'4'}
    },
   cate_exclude:'纪录片',
   tab_rename:{'高清线路②':'量子','超清线路3':'乐视','高清线路③':'非凡','高清线路④':'优质','高清线路⑤':'索尼','超清线路2':'360'},
	searchUrl:'/vod-s/**----------fypage---.html',
	tab_remove:['夸克4K'],
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
}

