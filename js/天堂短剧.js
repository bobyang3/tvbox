var rule = {
    author: '小可乐/240525/第一版',
    title: '短剧天堂',
    host: 'https://duanjutt.tv',
    hostJs: '',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,

    homeUrl: '/',
    url: '/vodshow/fyfilter---fypage---.html',
    filter_url: '{{fl.cateId}}--{{fl.by}}---{{fl.letter}}',
    detailUrl: '',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,

    class_name: '逆袭(1组)&都市(2组)&神医(3组)&脑洞(4组)',
    class_url: '1&20&25&30',
    filter_def: {
        1: {cateId: '1'},
        20: {cateId: '20'},
        25: {cateId: '25'},
        30: {cateId: '30'}
    },

    play_parse: true,
    parse_url: '',
    lazy: `js:
var kcode = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
var kurl = kcode.url;
input = {
parse: 0, url: kurl, header: {"User-Agent": 'MOBILE_UA', "Referer":"https://duanjutt.tv"}
}`,

    limit: 9,
    double: false,
    推荐: '*;*;*;*;*',
    一级: '.myui-vodlist li;a&&title;a&&data-original;.text-right&&Text;a&&href',
    二级: {
//名称;类型
        "title": "h1&&Text;.data:eq(0)&&a:eq(0)&&Text",
//图片
        "img": ".picture&&img&&data-original",
//主要描述;年份;地区;演员;导演
        "desc": ".data:eq(1)&&Text;.data:eq(0)&&a:eq(-1)&&Text;.data:eq(0)&&a:eq(-2)&&Text;.data--span:eq(2)&&Text;.data--span:eq(3)&&Text",
//简介
        "content": ".data:eq(-1)&&Text",
//线路数组
        "tabs": ".nav-tabs:has(li)&&a",
//线路标题
        "tab_text": "body&&Text",
//播放数组 选集列表
        "lists": ".myui-content__list:eq(#id)&&a",
//选集标题
        "list_text": "body&&Text",
//选集链接
        "list_url": "a&&href"
    },
    搜索: '.myui-vodlist__media .thumb;*;*;*;*',

    filter: {
"1":[
{"key":"cateId","name":"类型","value":[{"n":"逆袭","v":"1"},{"n":"甜宠","v":"2"},{"n":"虐恋","v":"3"},{"n":"穿越","v":"4"},{"n":"重生","v":"5"}]},
{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},
{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}
],
"20":[
{"key":"cateId","name":"类型","value":[{"n":"都市","v":"20"},{"n":"现代言情","v":"21"},{"n":"古装","v":"22"},{"n":"古代言情","v":"23"},{"n":"战神","v":"24"}]},
{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},
{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}
],
"25":[
{"key":"cateId","name":"类型","value":[{"n":"神医","v":"25"},{"n":"神豪","v":"26"},{"n":"超能","v":"27"},{"n":"萌宝","v":"28"},{"n":"复仇","v":"29"}]},
{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},
{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}
],
"30":[
{"key":"cateId","name":"类型","value":[{"n":"脑洞","v":"30"},{"n":"赘婿","v":"31"},{"n":"玄幻","v":"32"},{"n":"热血","v":"33"},{"n":"其他","v":"34"}]},
{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},
{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}
]
}
}
