muban.mxpro.二级.desc = '.module-info-item:eq(-1)&&Text;;;.module-info-item-content:eq(2)&&Text;.module-info-item-content:eq(1)&&Text'
muban.mxpro.二级.tabs = '#y-playList&&.tab-item'
muban.mxpro.二级.tab_text = 'body--small&&Text'
var rule = {
    title: '网飞.TV',
    模板: 'mxpro',
    host: 'https://www.wangfei.tv',
    // url:'/vodshow/id/fyclass/page/fypage.html',
    url: '/vodshow/id/fyfilter.html',
    filterable: 1,//是否启用分类筛选,
    filter_url: '{{fl.cateId}}{{fl.area}}{{fl.by or "/by/time"}}{{fl.class}}{{fl.lang}}{{fl.letter}}/page/fypage{{fl.year}}',
    filter: {,
    filter_def: {
        dy: {cateId: 'dy'},
        juji: {cateId: 'juji'},
        zongyi: {cateId: 'zongyi'},
        dongman: {cateId: 'dongman'},
        jilupian: {cateId: 'jilupian'},
        dyjs: {cateId: 'dyjs'}
    },
    searchUrl: '/index.php/rss.xml?wd=**',
    class_parse: '.navbar-items li:gt(1):lt(8);a&&title;a&&href;.*/(.*?).html',
    lazy: $js.toString(() => {
        let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        let url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\.m3u8|\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        }
    }),
    搜索: $js.toString(() => {
        let html = request(input);
        let items = pdfa(html, 'rss&&item');
        // log(items);
        let d = [];
        items.forEach(it => {
            it = it.replace(/title|link|author|pubdate|description/g, 'p');
            let url = pdfh(it, 'p:eq(1)&&Text');
            d.push({
                title: pdfh(it, 'p&&Text'),
                url: url,
                desc: pdfh(it, 'p:eq(3)&&Text'),
                content: pdfh(it, 'p:eq(2)&&Text'),
                pic_url: "",
            });
        });
        setResult(d);
    }),

}

