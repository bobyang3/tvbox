var rule = {
  title: '墨点影视',
  host: 'https://www.modiandy.com/',
  url: '/fyclass/page/fypage',
  searchUrl: '/search/**/page/fypage',
  searchable: 2,
  headers: {'User-Agent': 'PC_UA',},
  class_parse: '.navbar-nav ul.list li;a&&Text;a&&href;/(\\w+/\\w+)',
  //class_name:'电影&电视剧&综艺&动漫&纪录片&微电影',
  //class_url:'dianying&dianshiju&zongyi&dongman&jilupian&weidianying',
  play_parse: true,
  lazy:'',
  limit: 6,
  double: true,
  推荐: '.new-list;li;.subject&&Text;img&&_src;.state&&Text;a&&href',
  一级: '.item;.subject&&Text;img&&_src;.state&&Text;a&&href',
二级: `js:
let khtml = request(input);
let kdetail = pdfh(khtml, '.info');
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(kdetail, '.subject&&Text');
VOD.vod_pic = pdfh(kdetail, '.lazy-load-img&&_src');
VOD.type_name = pdfh(kdetail, '.rstype&&Text');
VOD.vod_remarks = pdfh(kdetail, '.block-wrap em&&Text');
VOD.vod_year = pdfh(kdetail, '.year--label&&Text');
VOD.vod_area = pdfh(kdetail, '.area--label&&Text');
VOD.vod_director = pdfh(kdetail, 'p.ellipsis-one:eq(0)--label&&Text');
VOD.vod_actor = pdfh(kdetail, '.performer_row--label&&Text');
VOD.vod_content = pdfh(khtml, '.content&&Text');

let ktabs = [];
let i = 1;
pdfa(khtml, '.nav-tabs a').map((it) => { 
    ktabs.push(i + pdfh(it, '.tab-nav&&title'));
    i++
});
VOD.vod_play_from = ktabs.join('$$$');

let kplists = [];
let htmls = pdfa(khtml, '.item-name a').map((it) => { return request(pd(it, 'a&&href', input), {headers: {'User-Agent': 'MOBILE_UA'}} ) });
htmls.forEach((ht) => {
    if (ht) {
        let plist = pdfa(ht, '.episodes-list:eq(0)&&a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input) });
        plist = plist.join('#');
        kplists.push(plist)
    } else {
        kplists.push('')
    }
});
VOD.vod_play_url = kplists.join('$$$')
`,
  搜索: '.item;.subject&&Text;img&&_src;.state&&Text;a&&href',
}
