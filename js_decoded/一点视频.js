var rule = {
    title: '一点视频',
    host: 'https://www.1av.me',
    url: '/vodtype/fyclass-fypage.html',
    searchUrl: '/vodsearch/**-/page/fypage.html',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    class_name: '国产视频&国产自拍&国产偷拍&探花系列&国产主播&学生嫩妹&人妻少妇&港台靓女&明星换脸&网红黑料&国产群交&国产乱伦&麻豆传媒&绿帽换妻&国产人妖&亚洲色情&日韩无码&欧美无码&中文字幕&三级电影&成人动漫&童颜巨乳&美腿丝袜&熟女人妻&少女萝莉&强奸乱伦&口交群交', //静态分类名称拼接
    class_url: '1&2&3&4&5&6&7&8&9&10&12&13&11&14&15&16&17&18&20&21&22&23&24&25&26&27&28', //静态分类标识拼接
    play_parse: true,
    lazy: '',
    limit: 6,
    推荐: '',
    double: true,
    一级: '.video-wrapper&&a;a&&title;img&&src;.number&&Text;a&&href',
    二级: '*',
    搜索: '.video-wrapper&&a;a&&title;img&&src;.number&&Text;a&&href',
}
