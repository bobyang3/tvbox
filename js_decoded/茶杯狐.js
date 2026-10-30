var rule={
title: '茶杯狐',
host: 'https://www.5jcd.com',
url: '/show_fyfilter.html',
searchUrl: '/sou/page/fypage/wd/**.html',
searchable: 2,quickSearch: 0,filterable: 1,
headers: {'User-Agent': 'MOBILE_UA'},
filter_url: '{{fl.area}}{{fl.by}}{{fl.class}}{{fl.cateId}}/page/fypage{{fl.year}}',
filter_def: {
'/id/1': {cateId: '/id/1'},'/id/2': {cateId: '/id/2'},'/id/3': {cateId: '/id/3'},'/id/4': {cateId: '/id/4'}},
class_name: '电影&剧集&综艺&动漫',
class_url: '/id/1&/id/2&/id/3&/id/4',
lazy: '',
推荐: '*',double: true,
一级: '.myui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
二级: {
title: '.myui-content__detail .title&&Text;.myui-content__detail p:eq(-2)&&Text',
img: '.myui-content__thumb .lazyload&&data-original',
desc: '.myui-content__detail p:eq(0)&&Text;.myui-content__detail p:eq(1)&&Text;.myui-content__detail p:eq(2)&&Text',
content: '.content&&Text',
tabs:'.myui-panel-box.clearfix h3:not(:contains(热播))',
lists: '.myui-content__list:eq(#id) a'},
搜索: '#searchList li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.detail&&p:eq(2)&&Text',
filter: {"/id/1":[{"key":"cateId","name":"类型","value":[{"n":"类型","v":""},{"n":"纪录片","v":"/id/41"},{"n":"动作电影","v":"/id/31"},{"n":"喜剧电影","v":"/id/33"},{"n":"爱情电影","v":"/id/34"},{"n":"科幻电影","v":"/id/35"},{"n":"恐怖电影","v":"/id/36"},{"n":"警匪电影","v":"/id/37"},{"n":"战争电影","v":"/id/38"},{"n":"剧情电影","v":"/id/39"},{"n":"悬疑电影","v":"/id/40"},{"n":"奇幻电影","v":"/id/56"}]},{"key":"class","name":"剧情","value":[{"n":"剧情","v":""},{"n":"喜剧","v":"/class/喜剧"},{"n":"爱情","v":"/class/爱情"},{"n":"恐怖","v":"/class/恐怖"},{"n":"动作","v":"/class/动作"},{"n":"科幻","v":"/class/科幻"},{"n":"剧情","v":"/class/剧情"},{"n":"战争","v":"/class/战争"},{"n":"警匪","v":"/class/警匪"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动画","v":"/class/动画"},{"n":"奇幻","v":"/class/奇幻"},{"n":"武侠","v":"/class/武侠"},{"n":"冒险","v":"/class/冒险"},{"n":"枪战","v":"/class/枪战"},{"n":"悬疑","v":"/class/悬疑"},{"n":"惊悚","v":"/class/惊悚"},{"n":"经典","v":"/class/经典"},{"n":"青春","v":"/class/青春"},{"n":"文艺","v":"/class/文艺"},{"n":"古装","v":"/class/古装"},{"n":"历史","v":"/class/历史"},{"n":"运动","v":"/class/运动"},{"n":"农村","v":"/class/农村"}]},{"key":"area","name":"地区","value":[{"n":"地区","v":""},{"n":"🇨🇳大陆","v":"/area/大陆"},{"n":"🇭🇰香港","v":"/area/香港"},{"n":"🇹🇼台湾","v":"/area/台湾"},{"n":"🇺🇸美国","v":"/area/美国"},{"n":"🇫🇷法国","v":"/area/法国"},{"n":"🇬🇧英国","v":"/area/英国"},{"n":"🇯🇵日本","v":"/area/日本"},{"n":"🇰🇷韩国","v":"/area/韩国"},{"n":"🇩🇪德国","v":"/area/德国"},{"n":"🇹🇭泰国","v":"/area/泰国"},{"n":"🇮🇳印度","v":"/area/印度"},{"n":"🇮🇹意大利","v":"/area/意大利"},{"n":"🇪🇸西班牙","v":"/area/西班牙"},{"n":"🇨🇦加拿大","v":"/area/加拿大"}]},{"key":"year","name":"年份","value":[{"n": "2027", "v": "/year/2027"},{"n": "2026", "v": "/year/2026"},{"n": "2025", "v": "/year/2025"},{"n":"年份","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"by","name":"排序","value":[{"n":"排序","v":""},{"n":"时间","v":"/by/time"},{"n":"周人气","v":"/by/hits_week"},{"n":"月人气","v":"/by/hits_month"}]}],
}

