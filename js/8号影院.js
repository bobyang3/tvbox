Object.assign(muban.首图2.二级, {
    tabs: '.stui-pannel__head h3',
});
var rule = {
    模板: '首图2',
    title: '8号影院',
    host: 'http://www.bahaoys.com',
    url: "/frim/fyfilter.html",
    filterable: 1,//是否启用分类筛选,
    filter_url: "{{fl.按分类}}-fypage",
    tab_exclude: '本周热门|最近更新',
    filter: {"1":[{"key":"按分类","name":"按分类","value":[{"n":"动作片","v":"5"},{"n":"爱情片","v":"6"},{"n":"科幻片","v":"7"},{"n":"恐怖片","v":"8"},{"n":"喜剧片","v":"10"},{"n":"剧情片","v":"12"}]}],"2":[{"key":"按分类","name":"按分类","value":[{"n":"国产剧","v":"13"},{"n":"港台剧","v":"14"},{"n":"欧美剧","v":"15"},{"n":"日韩剧","v":"16"}]}],"3":[{"key":"按分类","name":"按分类","value":[]}],"4":[{"key":"按分类","name":"按分类","value":[]}]},
    filter_def: {
    1: {
      按分类: "1"
    },
    2: {
      按分类: "2"
    },
    3: {
      按分类: "3"
    },
    4: {
      按分类: "4"
    }
  },
    searchUrl: '/search.php?page=fypage&searchword=**   &searchtype=',
    class_parse: ".stui-tou__menu li;a&&Text;a&&href;.*/(.*?).html",
    lazy: $js.toString(() => {
        let init_js = `Object.defineProperties(navigator, {platform: {get: () => 'iPhone'}});`;
        input = {
            parse: 1,
            url: input,
            js: '',
            parse_extra: '&init_script=' + encodeURIComponent(base64Encode(init_js)),
        }
    }),
    搜索: '.stui-vodlist__media&&li;a&&title;.lazyload&&data-original;.text-right&&Text;a&&href',
}

