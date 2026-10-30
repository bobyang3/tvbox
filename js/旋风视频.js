var rule = {
    类型: '影视',//影视|听书|漫画|小说
    title: '旋风视频',
    host: 'https://miao101.com/',
    url: '/tag/fyfilter',
    searchUrl: '/search?q=**',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: {"电影":[{"key":"类型","name":"类型","value":[{"n":"动作片","v":"动作片"},{"n":"喜剧片","v":"喜剧片"},{"n":"爱情片","v":"爱情片"},{"n":"科幻片","v":"科幻片"},{"n":"奇幻片","v":"奇幻片"},{"n":"冒险片","v":"冒险片"},{"n":"恐怖片","v":"恐怖片"},{"n":"惊悚片","v":"惊悚片"},{"n":"悬疑片","v":"悬疑片"},{"n":"犯罪片","v":"犯罪片"},{"n":"动漫片","v":"动漫片"},{"n":"剧情片","v":"剧情片"},{"n":"战争片","v":"战争片"},{"n":"纪录片","v":"纪录片"}]}],"电视剧":[{"key":"类型","name":"类型","value":[{"n":"国产剧","v":"国产剧"},{"n":"香港剧","v":"香港剧"},{"n":"韩国剧","v":"韩国剧"},{"n":"欧美剧","v":"欧美剧"},{"n":"台湾剧","v":"台湾剧"},{"n":"日本剧","v":"日本剧"},{"n":"泰国剧","v":"泰国剧"}]}],"综艺":[{"key":"类型","name":"类型","value":[{"n":"大陆综艺","v":"大陆综艺"},{"n":"日韩综艺","v":"日韩综艺"},{"n":"港台综艺","v":"港台综艺"},{"n":"欧美综艺","v":"欧美综艺"}]}],"动漫":[{"key":"类型","name":"类型","value":[{"n":"国产动漫","v":"国产动漫"},{"n":"港台动漫","v":"港台动漫"},{"n":"日韩动漫","v":"日韩动漫"},{"n":"欧美动漫","v":"欧美动漫"},{"n":"海外动漫","v":"海外动漫"}]}],"体育":[{"key":"类型","name":"类型","value":[{"n":"足球","v":"足球"},{"n":"篮球","v":"篮球"},{"n":"网球","v":"网球"},{"n":"斯诺克","v":"斯诺克"}]}]},
    filter_url: '{{fl.类型}}/fypage',
    filter_def: {
        电影: {类型: '动作片'},
        电视剧: {类型: '国产剧'},
        综艺: {类型: '大陆综艺'},
        动漫: {类型: '国产动漫'},
        体育: {类型: '足球'}
    },
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    timeout: 5000,
    class_name: '电影&电视剧&综艺&动漫&体育',
    class_url: '电影&电视剧&综艺&动漫&体育',
    cate_exclude: '',
    play_parse: true,
    lazy: $js.toString(() => {
        input = {parse: 1, url: input, js: ''};
    }),
    double: false,
    推荐: '*',
    一级: '.g-2&&div.col-6;.card-title--span&&Text;img&&src;.sub&&Text;a&&href',
    二级: {
        title: 'h6&&Text;.row.mb-3:eq(1)&&.badge&&Text',
        img: 'img&&src',
        desc: '.row.mb-3:eq(1)&&.sub&&Text;.row.phone&&.flex-grow-1&&p:eq(3)&&Text;.row.phone&&.flex-grow-1&&p:eq(4)&&Text;.row.phone&&.flex-grow-1&&p:eq(1)&&Text;.row.phone&&.flex-grow-1&&p:eq(2)&&Text',
        content: '.text-break&&Text',
        tabs: '',
        lists: $js.toString(() => {
            let srcHtml = pdfh(html, '#container&&script&&Html');
            //log(srcHtml);
            let data = {};
            eval(srcHtml + '\ndata=vo;');
            // log(data);
            let list1 = data.clips.map(i => i.join('$'));
            LISTS = [list1];
        }),
        tab_text: 'body&&Text',
        list_text: 'body&&Text',
        list_url: 'a&&href',
        list_url_prefix: '',
    },
    搜索: '*',
}

