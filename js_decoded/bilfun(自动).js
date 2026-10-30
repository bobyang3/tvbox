var rule = {
    模板: '自动',
    模板修改: $js.toString(() => {
        muban.自动.二级.tabs = '.module-tab-item.tab-item';
    }),
    title: 'bilfun(自动)',
    host: 'http://bilfun.cc',
    url: '/bilfunshow/fyclassfyfilter.html',
    class_parse: '.navbar-items li:gt(1):lt(9);a&&Text;a&&href;/bilfun/(\\d+).html',
    filterable: 1,
    filter_url: '-{{fl.地区}}-{{fl.排序}}-{{fl.剧情}}-{{fl.语言}}-{{fl.字母}}---fypage---{{fl.年代}}',
    filter:  {,
    filter_def: {
        动漫: {类型: '4'},
        电影: {类型: '1'},
        连续剧: {类型: '2'},
        综艺: {类型: '3'},
        爽文短剧: {类型: '22'},
        纪录片: {类型: '19'},
        体育赛事: {类型: '20'},
        影视解说: {类型: '21'}
    },
    searchUrl: '/bilfunsearch/**----------fypage---.html',
}

