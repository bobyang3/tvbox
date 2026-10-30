var rule = {
    author: '小可乐/240701/第一版',
    title: 'GO影视',
    类型: '影视',
    host: 'https://www.goys.cc',
    hostJs: '',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,

    homeUrl: '/',
    url: '/vodshow/fyfilter.html',
    filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
    detailUrl: '',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,

    class_name: '电影&剧集&综艺&动漫&短剧&番剧',
    class_url: '1&2&3&4&30&31',
    filter_def: {
        1: {cateId: '1'},
        2: {cateId: '2'},
        3: {cateId: '3'},
        4: {cateId: '4'},
        30: {cateId: '30'},
        31: {cateId: '31'}
    },

    play_parse: true,
    lazy: `js:
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
let kjiexi = HOST + '/paly/goys/?url=';
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kjiexi + kurl };
}
`,

    limit: 9,
    double: false,
    推荐: '*',
    一级: '.module-item;a:eq(0)&&title;img&&data-src;.module-item-text&&Text;a:eq(0)&&href',
    二级: {
        title: 'h1&&Text;.tag-link:eq(1)&&Text',
        img: '.video-cover&&img&&data-src',
        desc: '.video-info-items:eq(-2)&&Text;.tag-link:eq(-2)&&Text;.tag-link:eq(-1)&&Text;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text',
        content: '.vod_content&&span&&Text',
        tabs: '.tab-item span',
        tab_text: 'body&&Text',
        lists: '.sort-item:eq(#id)&&a',
        list_text: 'body&&Text',
        list_url: 'a&&href',
    },
    搜索: '.module-search-item;.video-serial&&title;*;.video-serial&&Text;.video-serial&&href',

    filter: {
}

